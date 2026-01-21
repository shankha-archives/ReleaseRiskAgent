import sys
import os
import asyncio
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv('backend/.env')

from backend.agents.pr_review_agent import PRReviewAgent
from backend.models import RiskSignals, RiskScore, TestCase, Mitigation

# Mock responses
MOCK_RISK_SIGNALS = RiskSignals(
    churn=0.5,
    coverage_gap=0.3,
    incident_hotspot=0.8,
    flake_proximity=0.1,
    diff_risk=0.2,
    time_pressure=0.1
)

MOCK_RISK_SCORE = RiskScore(
    score=0.75,
    level='high',
    signals=MOCK_RISK_SIGNALS.model_dump(),
    explanation="Mock explanation"
)

# Mock the sub-agents or their engines
async def run_verification():
    print("🚀 Starting Logic Verification (Mocked LLM)...")
    
    # 1. Mock OpenAI in RiskEngine/Agent (if it calls LLM, though RiskEngine is mostly math)
    # RiskEngine seems to be math-based, so it might run real code!
    
    # 2. Mock TestGenerator (calls OpenAI)
    with patch('backend.core.test_generator.OpenAI') as MockOpenAI:
        mock_client = MockOpenAI.return_value
        mock_client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content='[{"test_name": "test_mock", "test_code": "pass", "description": "mock"}]'))
        ]
        
        # 3. Mock MitigationEngine (calls OpenAI? Let's assume it does or just mock the agent)
        # Actually, let's just run the Orchestrator and see how far it gets.
        # We might need to mock invoke on sub-agents if we want to isolate the Orchestrator.
        
        agent = PRReviewAgent()
        
        # Mocking internal agents to ensure we test the Graph flow, not the sub-agent implementation details
        # unless we want integration test. Let's do integration test but mock the LLM calls.
        
        # Mock LLM in MitigationEngine (if it exists there)
        # MitigationEngine usually uses LLM. Let's patch it globally for safety.
        with patch('backend.core.mitigation_engine.MitigationEngine.generate_mitigations') as mock_mitigate,\
             patch('backend.agents.risk_agent.ChatOpenAI') as MockRiskLLM:
            
            # Setup Mock for Risk Agent LLM
            mock_risk_llm_instance = MockRiskLLM.return_value
            mock_risk_llm_instance.invoke.return_value.content = '{"risk_level": "low", "reasoning": "Mock reasoning"}'
            
            mock_mitigate.return_value = [Mitigation(
                action_type="test", 
                description="Run mock tests", 
                required=True,
                priority="high",
                confidence=0.9
            )]
            
            # Setup Mock Data
            pr_data = {
                'pr_id': '123',
                'repo_name': 'test-repo',
                'pr_number': 1,
                'branch_name': 'feature/test',
                'author': 'tester',
                'title': 'Test PR',
                'diff_content': """diff --git a/main.py b/main.py
index 83db48f..bf0338f 100644
--- a/main.py
+++ b/main.py
@@ -1,5 +1,6 @@
 def hello():
-    print("Hello")
+    print("Hello World")
+    return True
"""
            }
            
            print("🔄 Invoking Orchestrator...")
            result = await agent.analyze_pr(pr_data)
            
            print("\n✅ Verification Result:")
            print(f"  - Risk Level: {result.risk_score.level}")
            print(f"  - Static Issues: {len(result.static_analysis)}")
            print(f"  - Test Cases Generated: {len(result.test_cases)}")
            print(f"  - Mitigations: {len(result.mitigations)}")
            
            if result.risk_score and len(result.test_cases) > 0:
                print("\n🎉 SUCCESS: The Multi-Agent Graph executed successfully!")
            else:
                print("\n⚠️ WARNING: Graph finished but results are empty. Check logs.")

if __name__ == "__main__":
    asyncio.run(run_verification())
