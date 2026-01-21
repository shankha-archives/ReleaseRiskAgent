from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
import logging
from backend.core.mitigation_engine import MitigationEngine
from backend.models import RiskScore

logger = logging.getLogger("MitigationAgent")

class MitigationAgentState(TypedDict):
    risk_score: Dict[str, Any]
    pr_data: Dict[str, Any]
    mitigations: List[Dict[str, Any]]
    error: str

class MitigationAgent:
    def __init__(self):
        self.mitigation_engine = MitigationEngine()
        self.workflow = self._build_workflow()
        
    def _build_workflow(self):
        workflow = StateGraph(MitigationAgentState)
        workflow.add_node("generate_mitigations", self.generate_mitigations)
        workflow.set_entry_point("generate_mitigations")
        workflow.add_edge("generate_mitigations", END)
        return workflow.compile()
        
    def generate_mitigations(self, state: MitigationAgentState) -> MitigationAgentState:
        try:
            logger.info("Generating mitigations...")
            risk_score_obj = RiskScore(**state['risk_score'])
            mitigations = self.mitigation_engine.generate_mitigations(risk_score_obj, state['pr_data'])
            
            state['mitigations'] = [m.model_dump() for m in mitigations]
            
        except Exception as e:
            state['error'] = str(e)
            logger.error(f"Error generating mitigations: {e}")
            
        return state
