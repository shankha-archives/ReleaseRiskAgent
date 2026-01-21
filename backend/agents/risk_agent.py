from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph, END
import logging
import json
import os
from langchain_openai import ChatOpenAI
from backend.core.risk_engine import RiskEngine
from backend.models import RiskScore

logger = logging.getLogger("RiskAgent")

class RiskAgentState(TypedDict):
    pr_data: Dict[str, Any]
    files: List[Dict[str, Any]]
    risk_signals: Dict[str, float]
    risk_score: Dict[str, Any]
    error: str

class RiskAgent:
    def __init__(self):
        self.risk_engine = RiskEngine()
        self.workflow = self._build_workflow()
        
        # Initialize OpenAI for semantic analysis
        api_key = os.environ.get('OPENAI_API_KEY')
        self.llm = ChatOpenAI(api_key=api_key, model="gpt-5.1", temperature=0.2)
        
    def _build_workflow(self):
        workflow = StateGraph(RiskAgentState)
        workflow.add_node("compute_risk", self.compute_risk)
        workflow.set_entry_point("compute_risk")
        workflow.add_edge("compute_risk", END)
        return workflow.compile()
        
    def compute_risk(self, state: RiskAgentState) -> RiskAgentState:
        try:
            logger.info("Computing risk (Quantitative + Qualitative)...")
            
            # 1. Quantitative Analysis (Math/Regex)
            risk_data = {
                'files': state['files'],
                'is_near_freeze': state['pr_data'].get('is_near_freeze', False),
                'is_stacked': state['pr_data'].get('is_stacked', False)
            }
            signals = self.risk_engine.compute_signals(risk_data)
            base_risk_score = self.risk_engine.calculate_risk_score(signals)
            
            # 2. Qualitative Analysis (LLM)
            # We only use LLM if we have actual content (mock diffs might be too short)
            llm_analysis = self._analyze_with_llm(state['pr_data'], state['files'])
            
            # 3. Merge Results
            # If LLM detects HIGH conditional risk, we override or boost the score
            final_score, explanation = self._merge_risks(base_risk_score, llm_analysis)
            
            state['risk_signals'] = signals.model_dump()
            state['risk_score'] = final_score.model_dump()
            state['risk_score']['explanation'] = explanation 
            
        except Exception as e:
            state['error'] = str(e)
            logger.error(f"Error computing risk: {e}")
            
        return state

    def _analyze_with_llm(self, pr_data: Dict[str, Any], files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ask LLM to analyze business risk and intent"""
        try:
            # Prepare context
            diff_summary = "\n".join([f"File: {f.get('file_path')}\nChange: {f.get('changes')[:500]}" for f in files[:5]])
            
            prompt = f"""
            You are a Senior Technical Lead. Analyze this Pull Request for Risk.
            
            Context:
            - Title: {pr_data.get('title')}
            - Description: {pr_data.get('description', 'No description provided')}
            - Author: {pr_data.get('author')}
            
            Code Changes (snippet):
            {diff_summary}
            
            Assess the following:
            1. **Business Impact**: Does this touch critical logic (payments, auth, schema)?
            2. **Complexity**: Is the logic purely complex or just verbose?
            3. **Intent Match**: Does the code match the PR description?
            
            Return a JSON object:
            {{
                "risk_level": "low" | "medium" | "high",
                "reasoning": "One sentence summary of risk."
            }}
            """
            
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # Clean JSON (Naively)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            return json.loads(content)
            
        except Exception as e:
            logger.warning(f"LLM Analysis failed: {e}")
            return {"risk_level": "medium", "reasoning": "LLM analysis failed, defaulting to medium."}

    def _merge_risks(self, base_score: RiskScore, llm_analysis: Dict[str, Any]) -> tuple[RiskScore, str]:
        """Combine specific signals with LLM 'gut check'"""
        combined_score = base_score
        
        # Mapping level to numeric for comparison
        levels = {"low": 0.2, "medium": 0.5, "high": 0.8}
        llm_val = levels.get(llm_analysis.get('risk_level', 'medium'), 0.5)
        
        # Logic: If LLM thinks it's strictly HIGHER risk than math, we bump it up.
        # If LLM thinks lower, we trust the math (conservative).
        if llm_val > base_score.score:
            combined_score.score = (base_score.score + llm_val) / 2
            combined_score.level = llm_analysis['risk_level']
            
        final_explanation = f"{base_score.explanation} \n\n🤖 AI Assessment: {llm_analysis.get('reasoning')}"
        
        return combined_score, final_explanation
