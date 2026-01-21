# 🚀 Release Risk Radar (R³) - Quick Start Guide

## Overview
**Release Risk Radar** is an AI-powered PR review agent that analyzes code changes, scores risk, generates tests, and recommends mitigations using LangGraph and Azure OpenAI GPT-4o.

---

## ✅ System Status

All services are running and ready to use:
- ✅ **Backend API**: http://localhost:8001
- ✅ **Frontend UI**: http://localhost:3000
- ✅ **MongoDB**: Connected
- ✅ **Azure OpenAI**: Configured

---

## 🎯 Quick Demo (3 steps)

### Option 1: Using the Web UI

1. **Open the application**
   ```
   Navigate to: http://localhost:3000
   ```

2. **Submit a PR**
   - Click "Submit PR" in the navigation
   - Fill in the form:
     - Repo: `myorg/auth-service`
     - Branch: `feature/oauth-integration`
     - Author: `@yourname`
     - Title: `Add OAuth 2.0 authentication`
   - Click "Submit & Analyze"

3. **View Results**
   - Automatically redirected to PR analysis page
   - See risk score, signals, code quality, tests, and mitigations
   - Approve or reject recommended actions

### Option 2: Using the API

```bash
# 1. Submit a PR
PR_ID=$(curl -s -X POST http://localhost:8001/api/pr/submit \
  -H "Content-Type: application/json" \
  -d '{
    "repo_name": "myorg/payment-service",
    "branch_name": "feature/stripe-integration",
    "author": "@alice",
    "title": "Add Stripe payment gateway",
    "diff_content": "MOCK"
  }' | jq -r '.pr_id')

echo "PR ID: $PR_ID"

# 2. Trigger analysis
curl -X POST http://localhost:8001/api/pr/$PR_ID/analyze

# 3. Get results
curl -s http://localhost:8001/api/pr/$PR_ID/analysis | jq '.risk_score'
```

---

## 📊 What You'll See

### Risk Analysis
```json
{
  "score": 0.502,
  "level": "medium",
  "signals": {
    "churn": 0.236,
    "coverage_gap": 0.6,
    "incident_hotspot": 0.6,
    "flake_proximity": 0.2,
    "diff_risk": 1.0,
    "time_pressure": 0.1
  },
  "explanation": "Risk: MEDIUM (0.50). Why: low coverage (40%), incident-prone paths, changes in critical paths (auth/payment/infra).",
  "citations": ["coverage-report:#412", "incident:INC-231"]
}
```

### Generated Mitigations
1. **CI Run** - Run impacted test suite + safety regression tests
2. **Test Coverage** - Add unit tests for uncovered code paths (target 70%)
3. **Canary Deployment** - Deploy to canary environment for validation (12h)
4. **Extra Review** - Review by senior engineer or domain expert

---

## 🧪 Running Tests

```bash
cd /app/tests
python test_r3_agent.py
```

Expected output:
```
✅ Health check: PASSED
✅ PR submission & analysis: PASSED
✅ Mitigation approval: PASSED
✅ Dashboard stats: PASSED
✅ Release train: PASSED

🎉 ALL TESTS PASSED!
```

---

## 🎨 UI Pages

### 1. Home Page (`/`)
- Feature showcase
- Statistics
- Call-to-action buttons

### 2. Dashboard (`/dashboard`)
- Total PRs analyzed
- Risk distribution (high/medium/low)
- Recent analyses list

### 3. Submit PR (`/submit-pr`)
- PR submission form
- Real-time analysis progress
- Auto-redirect to results

### 4. PR Detail (`/pr/:prId`)
- Risk score with signal breakdown
- Code quality analysis
- AI-generated tests (with syntax highlighting)
- Mitigation approval workflow

### 5. Release Train (`/release-train`)
- Create release trains
- Monitor cumulative risk
- View PR breakdown per release

---

## 🔧 API Endpoints

### Core Endpoints

```bash
# Health check
GET /api/health

# Submit PR
POST /api/pr/submit

# Analyze PR
POST /api/pr/{pr_id}/analyze

# Get analysis
GET /api/pr/{pr_id}/analysis

# List PRs
GET /api/pr/list

# Dashboard stats
GET /api/dashboard/stats

# Approve mitigation
POST /api/mitigation/approve

# Create release train
POST /api/release/create

# Get release details
GET /api/release/{release_id}
```

Full API docs: See `/app/README.md`

---

## 🎓 Understanding the Agent

### LangGraph Workflow (6 Steps)

```
1. Parse PR     → Extract files and diffs
2. Compute Risk → Calculate 6 risk signals
3. Static Analysis → Find code issues
4. Generate Tests → AI-powered test creation
5. Generate Mitigations → Context-aware recommendations
6. Create Trace → Audit trail for compliance
```

### Risk Signals

1. **Churn** (0.2 weight) - Code changes volume
2. **Coverage Gap** (0.25 weight) - Test coverage
3. **Incident Hotspot** (0.2 weight) - Historical failures
4. **Flake Proximity** (0.15 weight) - Test stability
5. **Diff Risk** (0.15 weight) - Critical path changes
6. **Time Pressure** (0.05 weight) - Freeze proximity

### Risk Levels

- **LOW** (0 - 0.3): Standard CI + smoke tests
- **MEDIUM** (0.3 - 0.6): Enhanced testing + optional canary
- **HIGH** (0.6 - 1.0): Full suite + mandatory canary + extra review

---

## 🔍 Inspecting Data

### View MongoDB Collections

```bash
mongosh
use test_database

# View PRs
db.prs.find().pretty()

# View analyses
db.analyses.find().pretty()

# View execution traces
db.execution_traces.find().pretty()

# View mitigations
db.mitigation_approvals.find().pretty()
```

### Check Backend Logs

```bash
# All logs
tail -f /var/log/supervisor/backend.err.log

# Filter for agent execution
tail -f /var/log/supervisor/backend.err.log | grep "Step"
```

---

## 🐛 Troubleshooting

### Backend not responding?
```bash
sudo supervisorctl restart backend
curl http://localhost:8001/api/health
```

### Frontend not loading?
```bash
sudo supervisorctl restart frontend
curl http://localhost:3000
```

### MongoDB connection issues?
```bash
sudo supervisorctl restart mongodb
mongosh --eval "db.runCommand({ ping: 1 })"
```

### Check all services
```bash
sudo supervisorctl status
```

---

## 📚 Key Files

### Backend
- `backend/server.py` - FastAPI application
- `backend/pr_review_agent.py` - LangGraph agent
- `backend/risk_engine.py` - Risk scoring
- `backend/test_generator.py` - AI test generation

### Frontend
- `frontend/src/App.js` - Main routing
- `frontend/src/pages/HomePage.js` - Landing page
- `frontend/src/pages/Dashboard.js` - PR dashboard
- `frontend/src/pages/PRDetail.js` - Analysis view

### Documentation
- `README.md` - Full project documentation
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `QUICK_START.md` - This guide

---

## 🎯 Demo Script (5 minutes)

1. **Open home page** (30s)
   - Show feature overview
   - Explain R³ concept

2. **Submit test PR** (1 min)
   - Navigate to Submit PR
   - Fill form with payment gateway example
   - Click Submit & Analyze

3. **Show analysis results** (2 min)
   - Point out MEDIUM risk score
   - Explain signal breakdown
   - Show static analysis issues
   - Display AI-generated tests

4. **Review mitigations** (1 min)
   - Go to Mitigations tab
   - Explain each recommendation
   - Demonstrate approval workflow

5. **Dashboard overview** (30s)
   - Show risk distribution
   - List recent PRs
   - Create release train

---

## 💡 Tips

- **Mock Data**: Currently using simulated data for coverage, incidents, and flakes
  - All mock sections clearly marked in code with `MOCK DATA NOTE`
  - See `README.md` for integration notes

- **Azure OpenAI**: Configured with your keys
  - Model: GPT-4o
  - Used for test generation only

- **Human-in-the-Loop**: All mitigations require approval
  - No auto-merge capability
  - Full audit trail in MongoDB

---

## 🚀 Next Steps

1. ✅ **Try the demo** - Submit a PR and see the analysis
2. ✅ **Review the code** - Check backend and frontend structure
3. ✅ **Run tests** - Verify everything works
4. 📖 **Read full docs** - See `README.md` for details
5. 🔮 **Plan integrations** - GitHub MCP, CI/CD, Jira, etc.

---

## 📞 Quick Reference

| Component | URL | Status |
|-----------|-----|--------|
| Frontend | http://localhost:3000 | ✅ Running |
| Backend API | http://localhost:8001 | ✅ Running |
| API Docs | http://localhost:8001/docs | ✅ Available |
| Health Check | http://localhost:8001/api/health | ✅ Healthy |
| MongoDB | localhost:27017 | ✅ Connected |

---

**Ready to start?** Open http://localhost:3000 in your browser! 🎉
