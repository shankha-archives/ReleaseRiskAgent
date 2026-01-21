from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
import logging
from backend.core.test_generator import TestGenerator
from backend.core.rag_system import RAGSystem

logger = logging.getLogger("TestAgent")

class TestAgentState(TypedDict):
    files: List[Dict[str, Any]]
    test_cases: List[Dict[str, Any]]
    error: str

class TestAgent:
    def __init__(self):
        self.test_generator = TestGenerator()
        self.rag_system = RAGSystem()
        self.workflow = self._build_workflow()
        
    def _build_workflow(self):
        workflow = StateGraph(TestAgentState)
        workflow.add_node("generate_tests", self.generate_tests)
        workflow.set_entry_point("generate_tests")
        workflow.add_edge("generate_tests", END)
        return workflow.compile()
        
    def generate_tests(self, state: TestAgentState) -> TestAgentState:
        try:
            logger.info("Generating tests...")
            files = state['files']
            
            # Simple logic: check RAG first (stub), then generate
            
            # Generate tests
            test_cases = self.test_generator.generate_tests_for_pr(files[:2])
            
            state['test_cases'] = [tc for tc in test_cases]
            
        except Exception as e:
            state['error'] = str(e)
            logger.error(f"Error generating tests: {e}")
            
        return state
