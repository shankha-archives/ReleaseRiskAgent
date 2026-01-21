"""RAG System for test case context and impact analysis"""
import os
import logging
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json

logger = logging.getLogger(__name__)

class RAGSystem:
    """RAG system for storing and retrieving test cases"""
    
    def __init__(self, persist_dir: str = "/app/data/chroma"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collections
        self.test_cases_collection = self.client.get_or_create_collection(
            name="test_cases",
            metadata={"description": "Existing test cases from the codebase"}
        )
        
        self.mr_history_collection = self.client.get_or_create_collection(
            name="mr_history",
            metadata={"description": "Historical MR analysis data"}
        )
        
        logger.info(f"RAG system initialized with persist_dir: {persist_dir}")
    
    def add_test_case(self, test_data: Dict[str, Any]):
        """Add a test case to the knowledge base"""
        test_id = test_data.get('id', test_data.get('name'))
        
        # Create text representation for embedding
        text = f"""
        Test: {test_data.get('name', 'Unknown')}
        Type: {test_data.get('type', 'Unknown')}
        File: {test_data.get('file_path', 'Unknown')}
        Description: {test_data.get('description', '')}
        Code: {test_data.get('code', '')[:500]}
        """
        
        self.test_cases_collection.add(
            ids=[test_id],
            documents=[text],
            metadatas=[test_data]
        )
        
        logger.info(f"Added test case: {test_id}")
    
    def bulk_add_test_cases(self, test_cases: List[Dict[str, Any]]):
        """Bulk add test cases"""
        if not test_cases:
            return
        
        ids = []
        documents = []
        metadatas = []
        
        for test_data in test_cases:
            test_id = test_data.get('id', test_data.get('name', f"test_{len(ids)}"))
            
            text = f"""
            Test: {test_data.get('name', 'Unknown')}
            Type: {test_data.get('type', 'Unknown')}
            File: {test_data.get('file_path', 'Unknown')}
            Description: {test_data.get('description', '')}
            Code: {test_data.get('code', '')[:500]}
            """
            
            ids.append(test_id)
            documents.append(text)
            metadatas.append(test_data)
        
        self.test_cases_collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"Bulk added {len(test_cases)} test cases")
    
    def find_related_tests(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Find test cases related to the query"""
        results = self.test_cases_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['ids'] or not results['ids'][0]:
            return []
        
        related_tests = []
        for i, test_id in enumerate(results['ids'][0]):
            related_tests.append({
                'id': test_id,
                'distance': results['distances'][0][i] if results['distances'] else 0,
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'document': results['documents'][0][i] if results['documents'] else ''
            })
        
        return related_tests
    
    def calculate_test_impact(self, changed_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate which tests are impacted by file changes"""
        impacted_tests = set()
        impact_by_file = {}
        
        for file_change in changed_files:
            file_path = file_change.get('file_path', file_change.get('new_path', ''))
            
            # Build query from file path and changes
            query = f"File: {file_path} Changes in code paths"
            
            # Find related tests
            related = self.find_related_tests(query, n_results=5)
            
            file_tests = []
            for test in related:
                # Only include if similarity is high enough (distance < 0.8)
                if test['distance'] < 0.8:
                    test_id = test['id']
                    impacted_tests.add(test_id)
                    file_tests.append({
                        'test_id': test_id,
                        'test_name': test['metadata'].get('name', test_id),
                        'test_type': test['metadata'].get('type', 'unknown'),
                        'relevance': 1 - test['distance']  # Convert distance to relevance
                    })
            
            if file_tests:
                impact_by_file[file_path] = file_tests
        
        # Calculate impact metrics
        total_tests = self.test_cases_collection.count()
        impact_ratio = len(impacted_tests) / total_tests if total_tests > 0 else 0
        
        return {
            'impacted_tests': list(impacted_tests),
            'impact_count': len(impacted_tests),
            'total_tests': total_tests,
            'impact_ratio': round(impact_ratio, 3),
            'impact_by_file': impact_by_file
        }
    
    def generate_regression_tests(self, changed_files: List[Dict[str, Any]], 
                                 risk_level: str) -> List[Dict[str, Any]]:
        """Generate must-do regression test recommendations"""
        impact_data = self.calculate_test_impact(changed_files)
        
        # Get all impacted tests
        impacted_tests = impact_data['impacted_tests']
        
        # Build recommendations based on risk level
        recommendations = []
        
        if risk_level == 'high':
            # High risk: Run all impacted tests + critical regression suite
            recommendations.append({
                'category': 'impacted_tests',
                'priority': 'critical',
                'test_count': len(impacted_tests),
                'description': f"Run all {len(impacted_tests)} impacted tests",
                'tests': impacted_tests
            })
            recommendations.append({
                'category': 'smoke_tests',
                'priority': 'critical',
                'description': "Run complete smoke test suite",
                'estimated_duration': '15 minutes'
            })
        elif risk_level == 'medium':
            # Medium risk: Run impacted tests + selective regression
            recommendations.append({
                'category': 'impacted_tests',
                'priority': 'high',
                'test_count': len(impacted_tests),
                'description': f"Run {len(impacted_tests)} impacted tests",
                'tests': impacted_tests
            })
        else:
            # Low risk: Run minimal impacted tests
            recommendations.append({
                'category': 'impacted_tests',
                'priority': 'medium',
                'test_count': min(len(impacted_tests), 5),
                'description': f"Run top {min(len(impacted_tests), 5)} impacted tests",
                'tests': impacted_tests[:5]
            })
        
        return recommendations
    
    def store_mr_analysis(self, mr_id: str, analysis_data: Dict[str, Any]):
        """Store MR analysis in history"""
        analysis_text = f"""
        MR: {mr_id}
        Risk Score: {analysis_data.get('risk_score', {}).get('score', 0)}
        Files Changed: {len(analysis_data.get('files_changed', []))}
        """
        
        self.mr_history_collection.add(
            ids=[mr_id],
            documents=[analysis_text],
            metadatas=[analysis_data]
        )
        
        logger.info(f"Stored MR analysis: {mr_id}")
    
    def get_test_stats(self) -> Dict[str, Any]:
        """Get statistics about stored test cases"""
        return {
            'total_tests': self.test_cases_collection.count(),
            'mr_history_count': self.mr_history_collection.count()
        }
