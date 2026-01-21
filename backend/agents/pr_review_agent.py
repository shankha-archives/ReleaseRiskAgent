"""LangGraph-based PR Review Orchestrator (Supervisor)"""
import os
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import logging
import json
from datetime import datetime

# Import Sub-Agents
from backend.agents.gitlab_agent import GitLabAgent
from backend.agents.risk_agent import RiskAgent
from backend.agents.test_agent import TestAgent
from backend.agents.mitigation_agent import MitigationAgent

from backend.core.static_analyzer import StaticAnalyzer
from backend.models import (
    PRAnalysis, RiskScore, StaticAnalysisResult, 
    TestCase, Mitigation, ExecutionTrace
)

logger = logging.getLogger("PRReviewOrchestrator")

class PRReviewState(TypedDict):
    """
    Global State passed between agents.
    """
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
    """
    Supervisor Agent that orchestrates the review process.
    Refactored from monolithic agent to use sub-agents.
    """
    
    def __init__(self):
        # Initialize Sub-Agents
        self.risk_agent = RiskAgent()
        self.test_agent = TestAgent()
        self.mitigation_agent = MitigationAgent()
        
        # Tools kept in orchestrator for simple linear steps (can be moved later)
        self.static_analyzer = StaticAnalyzer()
        
        # LLM for Orchestration (if needed for dynamic routing later)
        api_key = os.environ.get('OPENAI_API_KEY')
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-5.1", temperature=0)
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(PRReviewState)
        
        # Add Nodes (Delegate to Sub-Agents)
        workflow.add_node("parse_pr", self.parse_pr_node)
        workflow.add_node("compute_risk", self.call_risk_agent)
        workflow.add_node("static_analysis", self.run_static_analysis)
        workflow.add_node("generate_tests", self.call_test_agent)
        workflow.add_node("generate_mitigations", self.call_mitigation_agent)
        workflow.add_node("create_trace", self.create_trace)
        
        # Linear Flow for now (Supervisor Logic would go here for conditional branching)
        workflow.set_entry_point("parse_pr")
        workflow.add_edge("parse_pr", "compute_risk")
        workflow.add_edge("compute_risk", "static_analysis")
        workflow.add_edge("static_analysis", "generate_tests")
        workflow.add_edge("generate_tests", "generate_mitigations")
        workflow.add_edge("generate_mitigations", "create_trace")
        workflow.add_edge("create_trace", END)
        
        return workflow.compile()
    
    def parse_pr_node(self, state: PRReviewState) -> PRReviewState:
        """Parse raw PR data"""
        logger.info("Orchestrator: Parsing PR...")
        try:
            pr_data = state['pr_data']
            # Reusing the simple logic here or delegate to GitLabAgent if we had raw ID
            # For now, we assume pr_data is populated by caller (e.g. Poller)
            
            # Simplified diff parse
            diff = pr_data.get('diff_content', '')
            state['files'] = self._parse_diff(diff)
            state['step'] = 'parse_pr'
        except Exception as e:
            state['error'] = str(e)
            logger.error(f"Error parsing PR: {e}")
        return state

    def call_risk_agent(self, state: PRReviewState) -> PRReviewState:
        """Delegate to RiskAgent"""
        logger.info("Orchestrator: Calling RiskAgent...")
        try:
            # Adapt state for RiskAgent
            sub_state = {
                'pr_data': state['pr_data'],
                'files': state['files'],
                'risk_signals': {},
                'risk_score': {},
                'error': ''
            }
            result = self.risk_agent.workflow.invoke(sub_state)
            
            # Merge back
            state['risk_signals'] = result['risk_signals']
            state['risk_score'] = result['risk_score']
            if result.get('error'):
                state['error'] = result['error']
                
            state['step'] = 'compute_risk'
        except Exception as e:
            state['error'] = str(e)
            logger.error(f"Error calling RiskAgent: {e}")
        return state

    def run_static_analysis(self, state: PRReviewState) -> PRReviewState:
        """Run Static Analysis (Local Tool)"""
        logger.info("Orchestrator: Running Static Analysis...")
        try:
            results = self.static_analyzer.analyze_pr(state['files'])
            state['static_analysis'] = results
            state['step'] = 'static_analysis'
        except Exception as e:
            state['error'] = str(e)
        return state

    def call_test_agent(self, state: PRReviewState) -> PRReviewState:
        """Delegate to TestAgent"""
        logger.info("Orchestrator: Calling TestAgent...")
        try:
            sub_state = {
                'files': state['files'],
                'test_cases': [],
                'error': ''
            }
            result = self.test_agent.workflow.invoke(sub_state)
            
            state['test_cases'] = result['test_cases']
            state['step'] = 'generate_tests'
        except Exception as e:
            state['error'] = str(e)
        return state

    def call_mitigation_agent(self, state: PRReviewState) -> PRReviewState:
        """Delegate to MitigationAgent"""
        logger.info("Orchestrator: Calling MitigationAgent...")
        try:
            sub_state = {
                'risk_score': state['risk_score'],
                'pr_data': state['pr_data'],
                'mitigations': [],
                'error': ''
            }
            result = self.mitigation_agent.workflow.invoke(sub_state)
            
            state['mitigations'] = result['mitigations']
            state['step'] = 'generate_mitigations'
        except Exception as e:
            state['error'] = str(e)
        return state

    def create_trace(self, state: PRReviewState) -> PRReviewState:
        """Create Execution Trace"""
        logger.info("Orchestrator: Creating Trace...")
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
                score=state['risk_score'].get('score', 0),
                mitigations=[m['action_type'] for m in state['mitigations']],
                approval_state='awaiting_approval',
                sources=state['risk_score'].get('citations', []),
                confidence=state['risk_score'].get('confidence', 0.75),
                reasoning=state['risk_score'].get('explanation', '')
            )
            state['execution_trace'] = trace.model_dump()
            state['step'] = 'create_trace'
            logger.info(f"Trace created: {trace.trace_id}")
        except Exception as e:
            state['error'] = str(e)
            logger.error(f"Error creating trace: {e}")
        return state

    def _parse_diff(self, diff_content: str) -> List[Dict[str, Any]]:
        """Helper to parse raw diff string into file objects"""
        # (Same minimal parser logic as before)
        files = []
        if not diff_content or diff_content == "MOCK":
             # Return mock files for demo reliability if actual content missing
            return [
                {
                    'file_path': 'src/payment/processor.py',
                    'additions': 150,
                    'deletions': 45,
                    'changes': 'def process_payment(amount):\n    pass',
                    'content': 'def process_payment(amount):\n    if amount <= 0: raise ValueError'
                }
            ]
        
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

    async def analyze_pr(self, pr_data: Dict[str, Any]) -> PRAnalysis:
        """Main Entry Point"""
        logger.info(f"🚀 Orchestrator: Starting Analysis for PR {pr_data.get('pr_id')}")
        
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
        
        final_state = self.workflow.invoke(initial_state)
        
        if final_state.get('error'):
            logger.error(f"❌ Analysis Failed: {final_state['error']}")
        
        # Construct Final Result Object
        analysis = PRAnalysis(
            pr_id=pr_data.get('pr_id', 'unknown'),
            repo_name=pr_data.get('repo_name'),
            pr_number=pr_data.get('pr_number'),
            branch_name=pr_data.get('branch_name'),
            author=pr_data.get('author'),
            title=pr_data.get('title'),
            risk_score=RiskScore(**final_state['risk_score']) if final_state['risk_score'] else RiskScore(score=0, level='low', signals={}),
            static_analysis=[StaticAnalysisResult(**sa) for sa in final_state['static_analysis']],
            test_cases=[TestCase(**tc) for tc in final_state['test_cases']],
            test_results=[],
            mitigations=[Mitigation(**m) for m in final_state['mitigations']],
            execution_trace_id=final_state['execution_trace'].get('trace_id', ''),
            trace_log=final_state['execution_trace']
        )
        return analysis
