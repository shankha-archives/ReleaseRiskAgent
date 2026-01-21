"""GitLab API Client for fetching MR data"""
import os
import gitlab
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class GitLabClient:
    """GitLab API client for MR operations"""
    
    def __init__(self):
        self.token = os.environ.get('GITLAB_TOKEN')
        self.url = os.environ.get('GITLAB_URL', 'https://gitlab.com')
        
        if not self.token:
            raise ValueError("GITLAB_TOKEN not found in environment")
        
        self.gl = gitlab.Gitlab(self.url, private_token=self.token)
        self.gl.auth()
        logger.info(f"GitLab client initialized for {self.url}")
    
    def get_project(self, project_id: str):
        """Get GitLab project by ID or path"""
        try:
            return self.gl.projects.get(project_id)
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {e}")
            raise
    
    def get_merge_request(self, project_id: str, mr_iid: int) -> Dict[str, Any]:
        """Get merge request details"""
        try:
            project = self.get_project(project_id)
            mr = project.mergerequests.get(mr_iid)
            
            # Get additional data
            changes = mr.changes()
            commits = list(mr.commits())
            
            return {
                'mr_iid': mr.iid,
                'title': mr.title,
                'description': mr.description,
                'state': mr.state,
                'author': mr.author['username'],
                'source_branch': mr.source_branch,
                'target_branch': mr.target_branch,
                'web_url': mr.web_url,
                'created_at': mr.created_at,
                'updated_at': mr.updated_at,
                'sha': mr.sha,
                'changes': changes['changes'],
                'commits': [{
                    'id': c.id,
                    'short_id': c.short_id,
                    'message': c.message,
                    'created_at': c.created_at
                } for c in commits],
                'files_changed': len(changes['changes']),
                'additions': sum(f.get('additions', 0) for f in changes['changes']),
                'deletions': sum(f.get('deletions', 0) for f in changes['changes'])
            }
        except Exception as e:
            logger.error(f"Failed to get MR {project_id}!{mr_iid}: {e}")
            raise
    
    def get_file_content(self, project_id: str, file_path: str, ref: str) -> str:
        """Get file content at specific ref"""
        try:
            project = self.get_project(project_id)
            file_content = project.files.get(file_path=file_path, ref=ref)
            return file_content.decode().decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to get file {file_path} at {ref}: {e}")
            return ""
    
    def list_merge_requests(self, project_id: str, state: str = 'opened', per_page: int = 20) -> List[Dict[str, Any]]:
        """List merge requests for a project"""
        try:
            project = self.get_project(project_id)
            mrs = project.mergerequests.list(state=state, per_page=per_page)
            
            return [{
                'mr_iid': mr.iid,
                'title': mr.title,
                'author': mr.author['username'],
                'source_branch': mr.source_branch,
                'target_branch': mr.target_branch,
                'state': mr.state,
                'web_url': mr.web_url,
                'created_at': mr.created_at,
                'updated_at': mr.updated_at,
                'sha': mr.sha
            } for mr in mrs]
        except Exception as e:
            logger.error(f"Failed to list MRs for {project_id}: {e}")
            raise
    
    def get_projects(self, per_page: int = 50) -> List[Dict[str, Any]]:
        """List all accessible projects"""
        try:
            projects = self.gl.projects.list(membership=True, per_page=per_page)
            
            return [{
                'id': p.id,
                'name': p.name,
                'path_with_namespace': p.path_with_namespace,
                'description': p.description,
                'web_url': p.web_url,
                'default_branch': getattr(p, 'default_branch', 'main'),
                'last_activity_at': p.last_activity_at
            } for p in projects]
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            raise
    
    def has_new_commits_since(self, project_id: str, mr_iid: int, since_sha: str) -> bool:
        """Check if MR has new commits since given SHA"""
        try:
            project = self.get_project(project_id)
            mr = project.mergerequests.get(mr_iid)
            
            # Compare current SHA with provided SHA
            return mr.sha != since_sha
        except Exception as e:
            logger.error(f"Failed to check commits for {project_id}!{mr_iid}: {e}")
            return False
