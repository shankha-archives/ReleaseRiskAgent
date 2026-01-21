from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
import logging
from backend.integrations.gitlab_client import GitLabClient

logger = logging.getLogger("GitLabAgent")

class GitLabAgentState(TypedDict):
    project_id: str
    mr_iid: int
    mr_data: Dict[str, Any]
    error: str

class GitLabAgent:
    def __init__(self):
        self.client = GitLabClient()
        self.workflow = self._build_workflow()
        
    def _build_workflow(self):
        workflow = StateGraph(GitLabAgentState)
        workflow.add_node("fetch_mr", self.fetch_mr)
        workflow.set_entry_point("fetch_mr")
        workflow.add_edge("fetch_mr", END)
        return workflow.compile()
        
    def fetch_mr(self, state: GitLabAgentState) -> GitLabAgentState:
        try:
            logger.info(f"Fetching MR {state['mr_iid']} from {state['project_id']}")
            mr = self.client.get_merge_request(state['project_id'], state['mr_iid'])
            
            # Enrich with diff content (simplified)
            diff_content = ""
            if 'changes' in mr:
                for change in mr['changes']:
                     diff_content += f"diff --git a/{change['old_path']} b/{change['new_path']}\n"
                     diff_content += f"--- a/{change['old_path']}\n"
                     diff_content += f"+++ b/{change['new_path']}\n"
                     diff_content += f"{change.get('diff', '')}\n"
            
            mr['diff_content'] = diff_content
            state['mr_data'] = mr
            
        except Exception as e:
            state['error'] = str(e)
            logger.error(f"Error fetching MR: {e}")
            
        return state
