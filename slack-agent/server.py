
# MCP implementation for the Slack agent using only code in @slack-agent
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from chains import generate_chain, reflect_chain
from medium_utils import get_medium_story_text
from langchain_core.messages import HumanMessage, AIMessage
import os

load_dotenv()

mcp = FastMCP(
    name="SlackAgentMCP",
    host="0.0.0.0",
    port=8050,
)

slack_token = os.getenv("SLACK_BOT_TOKEN")
if not slack_token:
    raise ValueError("SLACK_BOT_TOKEN not found in environment variables")
slack_client = WebClient(token=slack_token)

@mcp.tool()
def refine_medium_story(story_url: str) -> str:
    """Fetch a Medium story and return a refined version using the agent's chain."""
    try:
        content = get_medium_story_text(story_url)
        messages = [HumanMessage(content=f"Here is a story from Medium to refine:\n\n{content}")]
        result = generate_chain.invoke({"messages": messages})
        return result
    except Exception as e:
        return f"❌ Error refining Medium story: {str(e)}"

@mcp.tool()
def send_to_slack(message: str, channel: str = "#ai-notifications-medium") -> str:
    """Send a message to a Slack channel."""
    try:
        max_length = 3000
        if len(message) > max_length:
            message = message[:max_length] + "...\n\n[Message truncated due to length]"
        slack_client.chat_postMessage(
            channel=channel,
            text=message
        )
        return f"✅ Message sent to {channel}"
    except SlackApiError as e:
        return f"❌ Slack API Error: {e.response['error']}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
def refine_and_send_medium_blog(story_url: str, channel: str = "#ai-notifications-medium") -> str:
    """Fetch a Medium story, refine it, and send to Slack."""
    try:
        content = get_medium_story_text(story_url)
        messages = [HumanMessage(content=f"Here is a story from Medium to refine:\n\n{content}")]
        result = generate_chain.invoke({"messages": messages})
        max_length = 3000
        final_message = result
        if len(final_message) > max_length:
            final_message = final_message[:max_length] + "...\n\n[Message truncated due to length]"
        slack_client.chat_postMessage(
            channel=channel,
            text=f"📢 Final Medium blog refined:\n\n{final_message}"
        )
        return "✅ Blog refined and sent to Slack!"
    except SlackApiError as e:
        return f"❌ Slack API Error: {e.response['error']}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
def test_slack_connection(channel: str = "#general") -> str:
    """Send a test message to Slack."""
    try:
        slack_client.chat_postMessage(
            channel=channel,
            text="🧪 Test message from MCP Slack Agent"
        )
        return "✅ Slack test message sent!"
    except SlackApiError as e:
        return f"❌ Slack API Error: {e.response['error']}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")