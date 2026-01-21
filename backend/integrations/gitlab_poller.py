import asyncio
import os
import logging
from typing import List, Dict, Any
import time
from dotenv import load_dotenv

# Add backend to path if running from here
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from backend.integrations.gitlab_client import GitLabClient
from backend.agents.pr_review_agent import PRReviewAgent
from backend.models import PRSubmission

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GitLabPoller")

load_dotenv()

class GitLabPoller:
    def __init__(self):
        self.gl_client = GitLabClient()
        self.project_id = os.environ.get('GITLAB_PROJECT_ID')
        self.pr_agent = PRReviewAgent()
        
        if not self.project_id:
            logger.error("GITLAB_PROJECT_ID not found in env")
            raise ValueError("GITLAB_PROJECT_ID missing")

    async def poll_and_analyze(self):
        logger.info(f"Polling GitLab project {self.project_id}...")
        
        try:
            # 1. Get Open MRs
            mrs = self.gl_client.list_merge_requests(self.project_id, state='opened')
            logger.info(f"Found {len(mrs)} open MRs")
            
            for mr in mrs:
                mr_iid = mr['mr_iid']
                logger.info(f"Checking MR !{mr_iid}: {mr['title']}")
                
                # 2. Get Full MR Details (Files, Diff)
                # Note: list_merge_requests returns brief info. 
                # gitlab_client.get_merge_request returns detailed info including changes
                full_mr = self.gl_client.get_merge_request(self.project_id, mr_iid)
                
                # 3. Check if we should analyze (TODO: Check DB if already analyzed this SHA)
                # For now, we'll just run analysis on the latest SHA if not flagged
                # In a real app, we'd query MongoDB here.
                
                # 4. Prepare data for Agent
                # Agent expects: repo_name, branch_name, pr_number, author, title, diff_content...
                # diff_content needs to be constructed from 'changes' or diffs
                
                # 4. Clone and Prepare Data
                # To act as Lead Engineer, we need FULL context, not just diffs.
                import tempfile
                import shutil
                from git import Repo
                
                # Clone to temp dir
                with tempfile.TemporaryDirectory() as temp_dir:
                    repo_url = self.gl_client.get_project(self.project_id).http_url_to_repo
                    # Inject token for auth: https://oauth2:TOKEN@gitlab.com/...
                    auth_url = repo_url.replace("https://", f"https://oauth2:{self.gl_client.token}@", 1)
                    
                    logger.info(f"Cloning {self.project_id} to {temp_dir}...")
                    try:
                        Repo.clone_from(auth_url, temp_dir, branch=full_mr['source_branch'])
                    except Exception as e:
                        logger.error(f"Failed to clone: {e}")
                        # Fallback to diff only if clone fails
                    
                    # Read modified files fully
                    files_context = []
                    if 'changes' in full_mr:
                        for change in full_mr['changes']:
                            path = change['new_path']
                            full_path = os.path.join(temp_dir, path)
                            content = ""
                            if os.path.exists(full_path):
                                try:
                                    with open(full_path, 'r') as f:
                                        content = f.read()
                                except:
                                    content = "(Binary or unreadable)"
                            
                            files_context.append({
                                'file_path': path,
                                'changes': change.get('diff', ''),
                                'content': content # Full file content
                            })

                    pr_data = {
                        'pr_id': str(full_mr['mr_iid']),
                        'repo_name': self.project_id,
                        'pr_number': full_mr['mr_iid'],
                        'branch_name': full_mr['source_branch'],
                        'author': full_mr['author'],
                        'title': full_mr['title'],
                        'description': full_mr['description'],
                        'files': files_context, # Rich context
                        'is_near_freeze': False,
                        'is_stacked': False
                    }
                    
                    logger.info(f"🚀 Triggering Deep Analysis for MR !{mr_iid}")
                    analysis = await self.pr_agent.analyze_pr(pr_data)
                    
                    logger.info(f"✅ Analysis Complete for MR !{mr_iid}. Risk: {analysis.risk_score.level}")
                    
                    # 5. Notify via GitLab Comment & Inline Discussions
                    try:
                        # General Summary
                        risks = [f"- {k}: {v:.2f}" for k, v in analysis.risk_score.signals.model_dump().items() if v > 0.1]
                        mitigations = [f"- [ ] {m.action_type}: {m.description} {'(Required)' if m.required else ''}" for m in analysis.mitigations]
                        
                        report = f"""
## 🛡️ Lead Engineer Review

**Risk Level**: `{analysis.risk_score.level.upper()}` ({analysis.risk_score.score})

### 🧠 Analysis
{analysis.risk_score.explanation}

### 🚩 Key Indicators
{chr(10).join(risks)}

### ✅ Recommended Actions
{chr(10).join(mitigations)}

---
*Analyzed by AI Release Agent*
"""
                        self.gl_client.post_mr_comment(self.project_id, mr_iid, report)
                        
                        # Inline Comments (Test Failures / Logic Gaps)
                        for test in analysis.test_cases:
                             # Check if it has a failure prediction
                             # Note: TestCase model needs to support this field or we map it from the raw agent output
                             # For now, let's assume valid output structure if we updated models.
                             pass 
                             # TODO: Iterate generated tests and if 'predicted_status' == 'fail', post a discussion.
                             # Currently 'TestCase' model in backend/models.py might not have 'predicted_status'.
                             # We will output this logic in the next step after updating the model.
                        
                        logger.info(f"📝 Posted analysis report to MR !{mr_iid}")
                        
                    except Exception as e:
                        logger.error(f"Failed to post comment: {e}")

        except Exception as e:
            logger.error(f"Error in polling cycle: {e}")

    async def run_loop(self, interval=300):
        while True:
            await self.poll_and_analyze()
            logger.info(f"Sleeping for {interval}s...")
            await asyncio.sleep(interval)

if __name__ == "__main__":
    poller = GitLabPoller()
    asyncio.run(poller.poll_and_analyze()) # Run once for test
    # asyncio.run(poller.run_loop()) # Run loop
