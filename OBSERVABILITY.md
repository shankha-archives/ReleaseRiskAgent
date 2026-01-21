# Observability & Logging Guide

## 1. Where are tool calls logged?
Currently, the system uses **Standard Python Logging** (`logging` module).
- **Console**: All tool calls (`RiskAgent`, `TestAgent`, etc.) log their activity to `stdout` (your terminal).
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## 2. Execution Traces (Database)
The `PRReviewAgent` creates a structured **Execution Trace** for every run.
- **Storage**: Stored in MongoDB collection `execution_traces`.
- **Content**:
  - `trace_id`: Unique ID for the run.
  - `inputs`: Repo, Branch, Files.
  - `signals`: Raw risk signals (churn, coverage, etc.).
  - `decisions`: Mitigations and approvals.
  - `reasoning`: The AI's explanation.

## 3. How to view them?
### Option A: API Endpoint
You can fetch the trace via the API:
```bash
curl http://localhost:8002/api/pr/{pr_id}/analysis
```
The response contains the full `trace_log`.

### Option B: Terminal Logs
When running `uvicorn`, look for logs like:
```
INFO - PRReviewOrchestrator - Orchestrator: Calling RiskAgent...
INFO - RiskAgent - Computing risk (Quantitative + Qualitative)...
INFO - PRReviewOrchestrator - Trace created: <trace-id>
```

## 4. Future Enhancement (LangSmith)
To see a visual graph of tool calls (inputs/outputs), we can integrate **LangSmith** by adding `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` to your `.env`.
