"""LangGraph-based PR Review Agent"""
import os
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
from datetime import datetime

from risk_engine import RiskEngine
from static_analyzer import StaticAnalyzer
from test_generator import TestGenerator
from mitigation_engine import MitigationEngine
from models import (
    PRAnalysis, RiskScore, StaticAnalysisResult, 
    TestCase, Mitigation, ExecutionTrace
)

class PRReviewState(TypedDict):
    """State for PR review workflow"""
    pr_data: Dict[str, Any]
    files: List[Dict[str, Any]]
    risk_signals: Dict[str, float]
    risk_score: Dict[str, Any]
    static_analysis: List[Dict[str, Any]]
    test_cases: List[Dict[str, Any]]
    mitigations: List[Dict[str, Any]]
    execution_trace: Dict[str, Any]
    error: str
    step: str

class PRReviewAgent:
    """Main PR Review Agent using LangGraph"""
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.environ.get('AZURE_OPENAI_ENDPOINT'),
            api_key=os.environ.get('AZURE_OPENAI_API_KEY'),
            api_version=os.environ.get('AZURE_OPENAI_API_VERSION'),
            deployment_name=os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME'),
            temperature=0.3
        )
        
        self.risk_engine = RiskEngine()
        self.static_analyzer = StaticAnalyzer()
        self.test_generator = TestGenerator()
        self.mitigation_engine = MitigationEngine()
        
        # Build workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(PRReviewState)
        
        # Add nodes
        workflow.add_node("parse_pr", self.parse_pr)
        workflow.add_node("compute_risk", self.compute_risk)
        workflow.add_node("static_analysis", self.static_analysis)
        workflow.add_node("generate_tests", self.generate_tests)
        workflow.add_node("generate_mitigations", self.generate_mitigations)
        workflow.add_node("create_trace", self.create_trace)
        
        # Define edges
        workflow.set_entry_point("parse_pr")
        workflow.add_edge("parse_pr", "compute_risk")
        workflow.add_edge("compute_risk", "static_analysis")
        workflow.add_edge("static_analysis", "generate_tests")
        workflow.add_edge("generate_tests", "generate_mitigations")
        workflow.add_edge("generate_mitigations", "create_trace")
        workflow.add_edge("create_trace", END)
        
        return workflow.compile()
    
    def parse_pr(self, state: PRReviewState) -> PRReviewState:
        """Parse PR data and extract files"""
        print("🔍 Step 1: Parsing PR data...")
        
        try:
            pr_data = state['pr_data']
            
            # Parse diff content to extract files
            # MOCK DATA NOTE: In production, this would parse actual git diff
            # For now, we'll use a simple parser or mock data
            files = self._parse_diff(pr_data.get('diff_content', ''))
            
            state['files'] = files
            state['step'] = 'parse_pr'
            print(f"   ✓ Parsed {len(files)} files")
            
        except Exception as e:
            state['error'] = f"Parse error: {str(e)}"
            print(f"   ✗ Error: {e}")
        
        return state
    
    def _parse_diff(self, diff_content: str) -> List[Dict[str, Any]]:
        """Parse git diff to extract file changes"""
        # MOCK DATA NOTE: Simplified parser
        # TODO: Use proper git diff parser (e.g., unidiff library)
        
        files = []
        
        if not diff_content or diff_content == "MOCK":
            # Return mock files for demo
            return [
                {
                    'file_path': 'src/payment/processor.py',
                    'additions': 150,
                    'deletions': 45,
                    'changes': 'def process_payment(amount):\n    # Payment processing logic\n    pass',
                    'content': 'def process_payment(amount):\n    if amount <= 0:\n        raise ValueError("Invalid amount")\n    # Process payment\n    return True'
                },
                {
                    'file_path': 'src/auth/login.py',
                    'additions': 80,
                    'deletions': 20,
                    'changes': 'def login(username, password):\n    # Login logic\n    pass',
                    'content': 'def login(username, password):\n    user = authenticate(username, password)\n    return create_session(user)'
                }
            ]
        
        # Simple diff parsing (production would use unidiff)
        current_file = None
        for line in diff_content.split('\n'):
            if line.startswith('diff --git'):
                if current_file:
                    files.append(current_file)
                current_file = {'additions': 0, 'deletions': 0, 'changes': ''}
            elif line.startswith('+++'):
                if current_file:
                    current_file['file_path'] = line.split('/', 1)[1] if '/' in line else line[4:]
            elif current_file:
                if line.startswith('+') and not line.startswith('+++'):
                    current_file['additions'] += 1
                    current_file['changes'] += line[1:] + '\n'
                elif line.startswith('-') and not line.startswith('---'):
                    current_file['deletions'] += 1
        
        if current_file:
            files.append(current_file)
        
        return files if files else []
    
    def compute_risk(self, state: PRReviewState) -> PRReviewState:
        """Compute risk score"""
        print("📊 Step 2: Computing risk score...")
        
        try:
            files = state['files']
            pr_data = state['pr_data']
            
            # Prepare data for risk engine
            risk_data = {
                'files': files,
                'is_near_freeze': pr_data.get('is_near_freeze', False),
                'is_stacked': pr_data.get('is_stacked', False)
            }
            
            # Compute signals
            signals = self.risk_engine.compute_signals(risk_data)
            
            # Calculate risk score
            risk_score = self.risk_engine.calculate_risk_score(signals)
            
            state['risk_signals'] = signals.model_dump()
            state['risk_score'] = risk_score.model_dump()
            state['step'] = 'compute_risk'
            
            print(f"   ✓ Risk Score: {risk_score.score:.2f} ({risk_score.level.upper()})")
            
        except Exception as e:
            state['error'] = f"Risk computation error: {str(e)}"
            print(f"   ✗ Error: {e}")
        
        return state
    
    def static_analysis(self, state: PRReviewState) -> PRReviewState:
        """Perform static code analysis"""
        print("🔬 Step 3: Running static analysis...")
        
        try:
            files = state['files']
            
            # Run static analysis
            analysis_results = self.static_analyzer.analyze_pr(files)
            
            state['static_analysis'] = analysis_results
            state['step'] = 'static_analysis'
            
            total_issues = sum(len(r['issues']) for r in analysis_results)
            print(f"   ✓ Analyzed {len(analysis_results)} files, found {total_issues} issues")
            
        except Exception as e:
            state['error'] = f"Static analysis error: {str(e)}"
            print(f"   ✗ Error: {e}")
            state['static_analysis'] = []
        
        return state
    
    def generate_tests(self, state: PRReviewState) -> PRReviewState:
        """Generate unit tests using LLM"""
        print("🧪 Step 4: Generating unit tests...")
        
        try:
            files = state['files']
            
            # Generate tests (limit to prevent timeout)
            test_cases = self.test_generator.generate_tests_for_pr(files[:2])  # Limit to 2 files for demo
            
            state['test_cases'] = [tc for tc in test_cases]
            state['step'] = 'generate_tests'
            
            print(f"   ✓ Generated {len(test_cases)} test cases")
            
        except Exception as e:
            state['error'] = f"Test generation error: {str(e)}"
            print(f"   ✗ Error: {e}")
            state['test_cases'] = []
        
        return state
    
    def generate_mitigations(self, state: PRReviewState) -> PRReviewState:
        """Generate mitigation recommendations"""
        print("🛡️  Step 5: Generating mitigations...")
        
        try:
            risk_score_dict = state['risk_score']
            risk_score = RiskScore(**risk_score_dict)
            pr_data = state['pr_data']
            
            # Generate mitigations
            mitigations = self.mitigation_engine.generate_mitigations(risk_score, pr_data)
            
            state['mitigations'] = [m.model_dump() for m in mitigations]
            state['step'] = 'generate_mitigations'
            
            print(f"   ✓ Generated {len(mitigations)} mitigation actions")
            
        except Exception as e:
            state['error'] = f"Mitigation generation error: {str(e)}"
            print(f"   ✗ Error: {e}")
            state['mitigations'] = []
        
        return state
    
    def create_trace(self, state: PRReviewState) -> PRReviewState:
        """Create execution trace for auditability"""
        print("📝 Step 6: Creating execution trace...")
        
        try:
            pr_data = state['pr_data']
            
            trace = ExecutionTrace(
                pr_id=pr_data.get('pr_id', 'unknown'),
                inputs={
                    'repo': pr_data.get('repo_name'),
                    'branch': pr_data.get('branch_name'),
                    'author': pr_data.get('author'),
                    'files_count': len(state['files'])
                },
                signals=state['risk_signals'],
                score=state['risk_score']['score'],
                mitigations=[m['action_type'] for m in state['mitigations']],
                approval_state='awaiting_approval',
                sources=state['risk_score'].get('citations', []),
                confidence=state['risk_score'].get('confidence', 0.75),
                reasoning=state['risk_score'].get('explanation', '')
            )
            
            state['execution_trace'] = trace.model_dump()
            state['step'] = 'create_trace'
            
            print(f"   ✓ Created execution trace: {trace.trace_id}")
            
        except Exception as e:
            state['error'] = f"Trace creation error: {str(e)}"
            print(f"   ✗ Error: {e}")
        
        return state
    
    async def analyze_pr(self, pr_data: Dict[str, Any]) -> PRAnalysis:
        """Main entry point to analyze a PR"""
        print(f"\n{'='*60}")
        print(f"🚀 Starting PR Review Agent Analysis")
        print(f"{'='*60}\n")
        
        # Initialize state
        initial_state = {
            'pr_data': pr_data,
            'files': [],
            'risk_signals': {},
            'risk_score': {},
            'static_analysis': [],
            'test_cases': [],
            'mitigations': [],
            'execution_trace': {},
            'error': '',
            'step': ''
        }
        
        # Run workflow
        final_state = self.workflow.invoke(initial_state)
        
        # Build PRAnalysis result
        analysis = PRAnalysis(
            pr_id=pr_data.get('pr_id', 'unknown'),
            repo_name=pr_data.get('repo_name'),
            pr_number=pr_data.get('pr_number'),
            branch_name=pr_data.get('branch_name'),
            author=pr_data.get('author'),
            title=pr_data.get('title'),
            risk_score=RiskScore(**final_state['risk_score']),
            static_analysis=[StaticAnalysisResult(**sa) for sa in final_state['static_analysis']],
            test_cases=[TestCase(**tc) for tc in final_state['test_cases']],
            test_results=[],
            mitigations=[Mitigation(**m) for m in final_state['mitigations']],
            execution_trace_id=final_state['execution_trace'].get('trace_id', ''),
            trace_log=final_state['execution_trace']
        )
        
        print(f"\n{'='*60}")
        print(f"✅ PR Review Analysis Complete!")
        print(f"{'='*60}\n")
        
        return analysis
