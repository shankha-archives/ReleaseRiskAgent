import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Add backend to path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from backend.agents.pr_review_agent import PRReviewAgent

load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SlackBot")

# Initialize App
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

if not SLACK_BOT_TOKEN:
    logger.warning("SLACK_BOT_TOKEN not found. Bot will not run.")

app = App(token=SLACK_BOT_TOKEN)

# Initialize Agent
agent = PRReviewAgent()

@app.event("app_mention")
def handle_app_mention_events(body, logger):
    logger.info(body)

@app.message("hello")
def message_hello(message, say):
    say(f"Hey there <@{message['user']}>! I'm the Release Risk Agent. I can help you review PRs.")

@app.message(r"^check pr\s+(\d+)")
def analyze_pr_command(message, say, context):
    pr_id = context['matches'][0]
    say(f"Starting analysis for PR #{pr_id}...")
    
    # Trigger analysis (Logic similar to poller or calling agent directly)
    # Note: Requires fetching PR data from GitLab first using the ID
    # For now, just a stub
    say(f"🔍 Analysis for PR #{pr_id} is queued. (Integration pending GitLab fetch)")

@app.message("risk")
def risk_explain(message, say):
    say("My risk scoring is based on: Churn, Coverage, Incidents, Flakiness, Critical Path Diff, and Time Pressure.")

def run_bot():
    if not SLACK_APP_TOKEN:
        logger.error("❌ SLACK_APP_TOKEN not found in .env (Required for Socket Mode).")
        logger.info("ℹ️  Please ensure you have an App-Level Token (starts with 'xapp-') enabled.")
        logger.info("   Script will exit without crashing.")
        return
    
    try:
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        handler.start()
    except Exception as e:
        logger.error(f"❌ Failed to start Slack Bot: {e}")

if __name__ == "__main__":
    run_bot()
