from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
import uuid

from models import (
    PRSubmission, PRAnalysis, MitigationApproval, 
    ReleaseTrain, ExecutionTrace
)
from pr_review_agent import PRReviewAgent

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Release Risk Radar API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize PR Review Agent
pr_agent = PRReviewAgent()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# PR Analysis Endpoints
# ============================================================================

@api_router.post("/pr/submit", response_model=dict)
async def submit_pr(pr_submission: PRSubmission):
    """Submit a PR for analysis"""
    try:
        logger.info(f"Received PR submission for {pr_submission.repo_name}/{pr_submission.branch_name}")
        
        # Create PR record
        pr_id = str(uuid.uuid4())
        pr_doc = pr_submission.model_dump()
        pr_doc['id'] = pr_id
        pr_doc['status'] = 'submitted'
        
        await db.prs.insert_one(pr_doc)
        
        return {
            "pr_id": pr_id,
            "status": "submitted",
            "message": "PR submitted successfully. Analysis will begin shortly."
        }
    
    except Exception as e:
        logger.error(f"Error submitting PR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/pr/{pr_id}/analyze", response_model=dict)
async def analyze_pr(pr_id: str):
    """Trigger PR analysis"""
    try:
        # Get PR data
        pr_doc = await db.prs.find_one({"id": pr_id}, {"_id": 0})
        if not pr_doc:
            raise HTTPException(status_code=404, detail="PR not found")
        
        logger.info(f"Starting analysis for PR {pr_id}")
        
        # Run PR Review Agent
        pr_data = {
            'pr_id': pr_id,
            'repo_name': pr_doc['repo_name'],
            'branch_name': pr_doc['branch_name'],
            'pr_number': pr_doc.get('pr_number'),
            'author': pr_doc['author'],
            'title': pr_doc['title'],
            'diff_content': pr_doc.get('diff_content', 'MOCK'),
            'is_near_freeze': False,  # TODO: Integrate with release calendar
            'is_stacked': False
        }
        
        analysis = await pr_agent.analyze_pr(pr_data)
        
        # Save analysis
        analysis_doc = analysis.model_dump()
        analysis_doc['timestamp'] = analysis_doc['timestamp'].isoformat()
        await db.analyses.insert_one(analysis_doc)
        
        # Save execution trace
        trace_doc = analysis.trace_log
        await db.execution_traces.insert_one(trace_doc)
        
        # Update PR status
        await db.prs.update_one(
            {"id": pr_id},
            {"$set": {"status": "analyzed", "analysis_id": analysis.id}}
        )
        
        logger.info(f"Analysis complete for PR {pr_id}")
        
        return {
            "pr_id": pr_id,
            "analysis_id": analysis.id,
            "trace_id": analysis.execution_trace_id,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Error analyzing PR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/pr/{pr_id}/analysis", response_model=dict)
async def get_pr_analysis(pr_id: str):
    """Get PR analysis results"""
    try:
        analysis = await db.analyses.find_one({"pr_id": pr_id}, {"_id": 0})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return analysis
    
    except Exception as e:
        logger.error(f"Error retrieving analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/pr/list", response_model=List[dict])
async def list_prs(limit: int = 50, skip: int = 0):
    """List all PRs"""
    try:
        prs = await db.prs.find({}, {"_id": 0}).sort("id", -1).skip(skip).limit(limit).to_list(limit)
        return prs
    except Exception as e:
        logger.error(f"Error listing PRs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Mitigation Endpoints
# ============================================================================

@api_router.post("/mitigation/approve", response_model=dict)
async def approve_mitigation(approval: MitigationApproval):
    """Approve or reject a mitigation"""
    try:
        # Get analysis
        analysis = await db.analyses.find_one(
            {"execution_trace_id": approval.trace_id},
            {"_id": 0}
        )
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Update mitigation status
        mitigations = analysis['mitigations']
        updated = False
        for m in mitigations:
            if m['id'] == approval.mitigation_id:
                m['status'] = 'approved' if approval.action == 'approve' else 'rejected'
                updated = True
                break
        
        if not updated:
            raise HTTPException(status_code=404, detail="Mitigation not found")
        
        # Save approval
        approval_doc = approval.model_dump()
        approval_doc['timestamp'] = approval_doc['timestamp'].isoformat()
        await db.mitigation_approvals.insert_one(approval_doc)
        
        # Update analysis
        await db.analyses.update_one(
            {"execution_trace_id": approval.trace_id},
            {"$set": {"mitigations": mitigations}}
        )
        
        logger.info(f"Mitigation {approval.mitigation_id} {approval.action}d")
        
        return {
            "status": "success",
            "message": f"Mitigation {approval.action}d successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing approval: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/mitigation/{trace_id}", response_model=List[dict])
async def get_mitigations(trace_id: str):
    """Get mitigations for a trace"""
    try:
        analysis = await db.analyses.find_one(
            {"execution_trace_id": trace_id},
            {"_id": 0, "mitigations": 1}
        )
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return analysis.get('mitigations', [])
    
    except Exception as e:
        logger.error(f"Error retrieving mitigations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Release Train Endpoints
# ============================================================================

@api_router.post("/release/create", response_model=dict)
async def create_release_train(release: ReleaseTrain):
    """Create a release train"""
    try:
        release_doc = release.model_dump()
        release_doc['created_at'] = release_doc['created_at'].isoformat()
        if release_doc.get('target_date'):
            release_doc['target_date'] = release_doc['target_date'].isoformat()
        
        await db.release_trains.insert_one(release_doc)
        
        return {
            "release_id": release.id,
            "status": "created"
        }
    
    except Exception as e:
        logger.error(f"Error creating release train: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/release/{release_id}", response_model=dict)
async def get_release_train(release_id: str):
    """Get release train details with cumulative risk"""
    try:
        release = await db.release_trains.find_one({"id": release_id}, {"_id": 0})
        
        if not release:
            raise HTTPException(status_code=404, detail="Release train not found")
        
        # Get all PR analyses for this release
        pr_ids = release.get('pr_ids', [])
        analyses = await db.analyses.find(
            {"pr_id": {"$in": pr_ids}},
            {"_id": 0, "risk_score": 1, "pr_id": 1}
        ).to_list(len(pr_ids))
        
        # Calculate cumulative risk
        if analyses:
            total_risk = sum(a['risk_score']['score'] for a in analyses)
            avg_risk = total_risk / len(analyses)
            release['cumulative_risk_score'] = round(avg_risk, 3)
        
        release['pr_analyses'] = analyses
        
        return release
    
    except Exception as e:
        logger.error(f"Error retrieving release train: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/release/list", response_model=List[dict])
async def list_release_trains(limit: int = 20):
    """List all release trains"""
    try:
        releases = await db.release_trains.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        return releases
    except Exception as e:
        logger.error(f"Error listing releases: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Dashboard Endpoints
# ============================================================================

@api_router.get("/dashboard/stats", response_model=dict)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Count PRs by risk level
        total_prs = await db.analyses.count_documents({})
        
        high_risk = await db.analyses.count_documents({"risk_score.level": "high"})
        medium_risk = await db.analyses.count_documents({"risk_score.level": "medium"})
        low_risk = await db.analyses.count_documents({"risk_score.level": "low"})
        
        # Recent analyses
        recent = await db.analyses.find(
            {},
            {"_id": 0, "pr_id": 1, "repo_name": 1, "title": 1, "risk_score": 1, "timestamp": 1}
        ).sort("timestamp", -1).limit(10).to_list(10)
        
        return {
            "total_prs": total_prs,
            "risk_distribution": {
                "high": high_risk,
                "medium": medium_risk,
                "low": low_risk
            },
            "recent_analyses": recent
        }
    
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Health Check
# ============================================================================

@api_router.get("/")
async def root():
    return {
        "service": "Release Risk Radar (R³) API",
        "version": "1.0.0",
        "status": "operational"
    }

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check MongoDB connection
        await db.command('ping')
        
        return {
            "status": "healthy",
            "database": "connected",
            "agent": "ready"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
