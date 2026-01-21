import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv('backend/.env')

from backend.agents.pr_review_agent import PRReviewAgent

async def run_live_test():
    print("🚀 Starting LIVE Integration Test (Real OpenAI Call)...")
    
    # 1. Initialize Agent
    agent = PRReviewAgent()
    
    # 2. Mock PR Data (Simulating a risky change)
    pr_data = {
        'pr_id': 'LIVE-TEST-001',
        'repo_name': 'payment-service',
        'pr_number': 101,
        'branch_name': 'feature/fast-checkout',
        'author': 'intern_dev',
        'title': 'Optimize payment validation',
        'description': 'Removed some redundant checks to speed up the checkout process. Only small changes.',
        'diff_content': """diff --git a/src/payments/validator.py b/src/payments/validator.py
index abc..def 100644
--- a/src/payments/validator.py
+++ b/src/payments/validator.py
@@ -10,7 +10,7 @@
     
     def validate_amount(self, amount):
-        if amount <= 0:
-            raise ValueError("Amount must be positive")
-        if amount > 10000:
-            return self.fraud_check(amount)
-        return True
+        # Optimization: process all amounts directly
+        return True
"""
    }
    
    print("🔄 Invoking Orchestrator...")
    print(f"   Context: User is removing validation logic in {pr_data['repo_name']}")
    
    try:
        result = await agent.analyze_pr(pr_data)
        
        print("\n✅ Analysis Complete!")
        print(f"Risk Level: {result.risk_score.level.upper()}")
        print(f"Risk Score: {result.risk_score.score}")
        print("Reasoning (from AI):")
        print("-" * 40)
        print(result.risk_score.explanation)
        print("-" * 40)
        
        # Validation
        if "AI Assessment" in result.risk_score.explanation:
            print("\n🎉 SUCCESS: The Risk Agent successfully used OpenAI to explain the risk!")
        else:
            print("\n⚠️ WARNING: Risk explanation suggests AI might not have run.")
            
    except Exception as e:
        print(f"\n❌ FAIL: {e}")

if __name__ == "__main__":
    asyncio.run(run_live_test())
