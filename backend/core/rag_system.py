"""RAG System for test case context and impact analysis using ChromaDB"""
import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
import json
import shutil

logger = logging.getLogger(__name__)

class RAGSystem:
    """RAG system for storing and retrieving test cases using ChromaDB"""
    
    def __init__(self, persist_dir: str = "/app/data/chroma"):
        self.persist_dir = os.environ.get('CHROMA_PERSIST_DIR', persist_dir)
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model (Standard OpenAI)
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OPENAI_API_KEY not found. Embeddings will fail.")
            
        self.embedding_model = OpenAIEmbeddings(
            api_key=api_key,
            model="text-embedding-3-small" # Standard model
        )
        
        # Get or create collections
        # Note: Chroma handling of embeddings is usually automatic if not specified, 
        # but for consistent results with LangChain we can embed manually or use an embedding function adapter.
        # For simplicity here, we'll embed manually using langchain and store vectors.
        
        self.test_cases_collection = self.client.get_or_create_collection(
            name="test_cases",
            metadata={"description": "Existing test cases from the codebase"}
        )
        
        self.mr_history_collection = self.client.get_or_create_collection(
            name="mr_history",
            metadata={"description": "Historical MR analysis data"}
        )
        
        logger.info(f"RAG system initialized with persist_dir: {self.persist_dir}")
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text"""
        text = text.replace("\n", " ")
        return self.embedding_model.embed_query(text)

    def add_test_case(self, test_data: Dict[str, Any]):
        """Add a test case to the knowledge base"""
        test_id = str(test_data.get('id', test_data.get('name')))
        
        # Create text representation for embedding
        text = f"""
        Test: {test_data.get('name', 'Unknown')}
        Type: {test_data.get('type', 'Unknown')}
        File: {test_data.get('file_path', 'Unknown')}
        Description: {test_data.get('description', '')}
        Code: {test_data.get('code', '')[:1000]}
        """
        
        # Embed manually
        embedding = self._get_embedding(text)
        
        # Clean metadata
        clean_metadata = {k: str(v) for k, v in test_data.items() if isinstance(v, (str, int, float, bool))}
        clean_metadata['text'] = text
        
        self.test_cases_collection.upsert(
            ids=[test_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[clean_metadata]
        )
        
        logger.info(f"Added test case: {test_id}")
    
    def bulk_add_test_cases(self, test_cases: List[Dict[str, Any]]):
        """Bulk add test cases"""
        if not test_cases:
            return
        
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for test_data in test_cases:
            test_id = str(test_data.get('id', test_data.get('name', f"test_{len(ids)}")))
            
            text = f"""
            Test: {test_data.get('name', 'Unknown')}
            Type: {test_data.get('type', 'Unknown')}
            File: {test_data.get('file_path', 'Unknown')}
            Description: {test_data.get('description', '')}
            Code: {test_data.get('code', '')[:1000]}
            """
            
            ids.append(test_id)
            documents.append(text)
            embeddings.append(self._get_embedding(text))
            
            clean_meta = {k: str(v) for k, v in test_data.items() if isinstance(v, (str, int, float, bool))}
            clean_meta['text'] = text
            metadatas.append(clean_meta)
            
        # Batch add (Chroma handles batching usually, but good to be safe if list is huge)
        self.test_cases_collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"Bulk added {len(test_cases)} test cases")
    
    def find_related_tests(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Find test cases related to the query"""
        embedding = self._get_embedding(query)
        
        results = self.test_cases_collection.query(
            query_embeddings=[embedding],
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
            
            query = f"File: {file_path} Changes in code paths"
            related = self.find_related_tests(query, n_results=5)
            
            file_tests = []
            for test in related:
                # Chroma returns distance (lower is better, e.g. L2)
                # If using cosine via embedding model, distance is usually 1 - cosine
                # Assume threshold for relevance
                if test['distance'] < 0.5: 
                    test_id = test['id']
                    impacted_tests.add(test_id)
                    file_tests.append({
                        'test_id': test_id,
                        'test_name': test['metadata'].get('name', test_id),
                        'test_type': test['metadata'].get('type', 'unknown'),
                        'relevance': 1 - test['distance']
                    })
            
            if file_tests:
                impact_by_file[file_path] = file_tests
        
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
        impacted_tests = impact_data['impacted_tests']
        
        recommendations = []
        
        if risk_level.lower() == 'high':
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
        elif risk_level.lower() == 'medium':
            recommendations.append({
                'category': 'impacted_tests',
                'priority': 'high',
                'test_count': len(impacted_tests),
                'description': f"Run {len(impacted_tests)} impacted tests",
                'tests': impacted_tests
            })
        else:
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
        
        embedding = self._get_embedding(analysis_text)
        
        clean_metadata = {k: str(v) for k, v in analysis_data.items() if isinstance(v, (str, int, float, bool))}
        clean_metadata['text'] = analysis_text
        
        self.mr_history_collection.upsert(
            ids=[mr_id],
            embeddings=[embedding],
            documents=[analysis_text],
            metadatas=[clean_metadata]
        )
        
        logger.info(f"Stored MR analysis: {mr_id}")
    
    def get_test_stats(self) -> Dict[str, Any]:
        """Get statistics about stored test cases"""
        return {
            'total_tests': self.test_cases_collection.count(),
            'mr_history_count': self.mr_history_collection.count()
        }
