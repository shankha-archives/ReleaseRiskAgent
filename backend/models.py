from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid

# MR Models (GitLab)
class MRSubmission(BaseModel):
    """MR submission request"""
    project_id: str  # GitLab project ID or path (e.g., "username/repo")
    mr_iid: int  # Merge Request internal ID
    
class MRData(BaseModel):
    """MR data from GitLab"""
    project_id: str
    mr_iid: int
    title: str
    description: Optional[str] = None
    author: str
    source_branch: str
    target_branch: str
    state: str
    web_url: str
    sha: str  # Current commit SHA
    created_at: str
    updated_at: str
    files_changed: int
    additions: int
    deletions: int

# PR Models (Legacy - for backward compatibility)
class PRSubmission(BaseModel):
    """PR submission request"""
    pr_url: Optional[str] = None
    repo_name: str
    branch_name: str
    pr_number: Optional[int] = None
    diff_content: str  # Actual code diff
    author: str
    title: str
    description: Optional[str] = None

class CodeFile(BaseModel):
    """Individual file in PR"""
    file_path: str
    additions: int
    deletions: int
    changes: str
    file_type: str  # python, javascript, etc

class RiskSignals(BaseModel):
    """Risk signals computed for PR"""
    churn: float = Field(ge=0, le=1, description="Normalized code churn")
    coverage_gap: float = Field(ge=0, le=1, description="1 - coverage")
    incident_hotspot: float = Field(ge=0, le=1, description="Prior incidents in paths")
    flake_proximity: float = Field(ge=0, le=1, description="Historical failure rate")
    diff_risk: float = Field(ge=0, le=1, description="Risky directories")
    time_pressure: float = Field(ge=0, le=1, description="Commits near freeze")

class RiskScore(BaseModel):
    """Risk score calculation"""
    score: float = Field(ge=0, le=1, description="Final risk score")
    level: str = Field(description="low, medium, or high")
    signals: RiskSignals
    explanation: str
    citations: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1, default=0.75)

class StaticAnalysisResult(BaseModel):
    """Static code analysis results"""
    file_path: str
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    complexity_score: float
    maintainability_index: float
    loc: int  # Lines of code

class TestCase(BaseModel):
    """Generated test case"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    file_path: str
    test_code: str
    test_type: str  # unit, integration, e2e
    description: str

class TestResult(BaseModel):
    """Test execution result"""
    test_id: str
    status: str  # passed, failed, skipped
    duration_ms: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None

class Mitigation(BaseModel):
    """Mitigation action"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str  # ci_run, canary, extra_review, test_coverage
    description: str
    required: bool
    status: str = "draft"  # draft, pending_approval, approved, rejected, completed
    confidence: float = Field(ge=0, le=1)

class TestImpactAnalysis(BaseModel):
    """Test impact analysis results"""
    impacted_tests: List[str] = Field(default_factory=list)
    impact_count: int = 0
    total_tests: int = 0
    impact_ratio: float = 0.0
    impact_by_file: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)

class RegressionTest(BaseModel):
    """Regression test recommendation"""
    category: str  # impacted_tests, smoke_tests, integration_tests
    priority: str  # critical, high, medium, low
    test_count: Optional[int] = None
    description: str
    tests: List[str] = Field(default_factory=list)
    estimated_duration: Optional[str] = None

class PRAnalysis(BaseModel):
    """Complete PR analysis result"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pr_id: str
    repo_name: str
    pr_number: Optional[int] = None
    branch_name: str
    author: str
    title: str
    
    # GitLab specific
    project_id: Optional[str] = None
    mr_iid: Optional[int] = None
    current_sha: Optional[str] = None  # Track commit SHA for change detection
    is_outdated: bool = False  # Flag if new commits since last analysis
    
    # Analysis components
    risk_score: RiskScore
    static_analysis: List[StaticAnalysisResult] = Field(default_factory=list)
    test_cases: List[TestCase] = Field(default_factory=list)
    test_results: List[TestResult] = Field(default_factory=list)
    mitigations: List[Mitigation] = Field(default_factory=list)
    
    # RAG-based analysis
    test_impact: Optional[TestImpactAnalysis] = None
    regression_tests: List[RegressionTest] = Field(default_factory=list)
    
    # Metadata
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    execution_trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Audit trail
    trace_log: Dict[str, Any] = Field(default_factory=dict)

class ExecutionTrace(BaseModel):
    """Audit trail for agent execution"""
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent: str = "ReleaseRiskRadar"
    pr_id: str
    inputs: Dict[str, Any]
    signals: Dict[str, float]
    score: float
    mitigations: List[str]
    approval_state: str
    sources: List[str]
    confidence: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reasoning: str = ""

class MitigationApproval(BaseModel):
    """Approval/rejection of mitigation"""
    trace_id: str
    mitigation_id: str
    action: str  # approve, reject
    approver: str
    comment: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReleaseTrain(BaseModel):
    """Release train view"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    release_version: str
    branch: str
    pr_ids: List[str] = Field(default_factory=list)
    cumulative_risk_score: float
    status: str  # planning, in_progress, completed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    target_date: Optional[datetime] = None
