# from typing import List, Sequence
# from dotenv import load_dotenv
# from langgraph.graph import END, MessageGraph
# from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
# from langchain_community.tools.slack.send_message import SlackSendMessage

# from chains import generate_chain, reflect_chain
# from medium_utils import get_medium_story_text
# import os

# load_dotenv()

# REFLECT = "reflect"
# GENERATE = "generate"
# SEND_SLACK = "send_slack"

# # Ensure the Slack token is available
# slack_token = os.getenv("SLACK_BOT_TOKEN")
# if not slack_token:
#     raise ValueError("SLACK_BOT_TOKEN not found in environment variables")

# # Initialize Slack tool
# slack_tool = SlackSendMessage(slack_token=slack_token)

# def read_story_node(state):
#     story_url = "https://medium.com/data-science/developers-documentation-to-openapi-specification-d73a0c19e86c"
#     content = get_medium_story_text(story_url)
#     return [HumanMessage(content=f"Here is a story from Medium to refine:\n\n{content}")]

# def generation_node(state: Sequence[BaseMessage]):
#     result = generate_chain.invoke({"messages": state})
#     return [AIMessage(content=result)]

# def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
#     result = reflect_chain.invoke({"messages": messages})
#     return [HumanMessage(content=result)]

# def slack_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
#     try:
#         final_message = messages[-1].content
#         print("📤 Slack node reached! Sending message...")
        
#         # Truncate message if too long (Slack has message limits)
#         max_length = 3000  # Conservative limit
#         if len(final_message) > max_length:
#             truncated_message = final_message[:max_length] + "...\n\n[Message truncated due to length]"
#         else:
#             truncated_message = final_message
        
#         # Send to Slack
#         result = slack_tool.invoke({
#             "message": f"📢 Final Medium blog refined:\n\n{truncated_message}",
#             "channel": "#ai-notifications-medium"
#         })
        
#         print(f"✅ Slack message sent successfully: {result}")
#         return messages
        
#     except Exception as e:
#         print(f"❌ Error sending Slack message: {str(e)}")
#         print(f"Error type: {type(e).__name__}")
#         # Return messages anyway to continue the flow
#         return messages

# def should_continue(state: List[BaseMessage]):
#     print(f"🔍 should_continue: message count = {len(state)}")
    
#     # Add logic to determine when to reflect vs when to send to Slack
#     # For now, always go to Slack after first generation
#     # You might want to add reflection logic here based on your needs
    
#     return SEND_SLACK

# # Alternative should_continue with reflection logic (uncomment if needed)
# """
# def should_continue(state: List[BaseMessage]):
#     print(f"🔍 should_continue: message count = {len(state)}")
    
#     # If we have less than 4 messages, continue reflecting
#     # Adjust this logic based on your needs
#     if len(state) < 4:
#         return REFLECT
#     else:
#         return SEND_SLACK
# """

# builder = MessageGraph()
# builder.add_node("read", read_story_node)
# builder.add_node(GENERATE, generation_node)
# builder.add_node(REFLECT, reflection_node)
# builder.add_node(SEND_SLACK, slack_node)

# builder.set_entry_point("read")
# builder.add_edge("read", GENERATE)
# builder.add_conditional_edges(GENERATE, should_continue)
# builder.add_edge(REFLECT, GENERATE)
# builder.add_edge(SEND_SLACK, END)

# graph = builder.compile()
# print(graph.get_graph().draw_mermaid())
# graph.get_graph().print_ascii()

# # Test Slack connection separately (uncomment to test)
# """
# def test_slack_connection():
#     try:
#         print("🧪 Testing Slack connection...")
#         result = slack_tool.invoke({
#             "message": "🧪 Test message from LangGraph Blog Refiner",
#             "channel": "#ai-notifications-medium"
#         })
#         print(f"✅ Slack test successful: {result}")
#         return True
#     except Exception as e:
#         print(f"❌ Slack test failed: {str(e)}")
#         print(f"Error type: {type(e).__name__}")
#         return False

# # Uncomment to test Slack before running main flow
# # test_slack_connection()
# """

# if __name__ == "__main__":
#     print("🟢 Running LangGraph Blog Refiner with Slack update...")
    
#     try:
#         response = graph.invoke([])
#         print("\n✅ Final Improved Blog Post:\n")
#         print(response[-1].content)
#     except Exception as e:
#         print(f"❌ Error running graph: {str(e)}")
#         print(f"Error type: {type(e).__name__}")

from typing import List, Sequence
from dotenv import load_dotenv
from langgraph.graph import END, MessageGraph
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from chains import generate_chain, reflect_chain
from medium_utils import get_medium_story_text
import os

load_dotenv()

REFLECT = "reflect"
GENERATE = "generate"
SEND_SLACK = "send_slack"

# Debug environment variable loading
print("🔍 Debugging environment variables...")
print(f"Current working directory: {os.getcwd()}")
print(f"Looking for .env file at: {os.path.join(os.getcwd(), '.env')}")
print(f".env file exists: {os.path.exists('.env')}")

# List all environment variables starting with SLACK
slack_vars = {k: v for k, v in os.environ.items() if 'SLACK' in k.upper()}
print(f"Slack-related env vars: {list(slack_vars.keys())}")

# Ensure the Slack token is available
slack_token = os.getenv("SLACK_BOT_TOKEN")
if not slack_token:
    print("❌ SLACK_BOT_TOKEN not found!")
    print("Please check:")
    print("1. .env file exists in current directory")
    print("2. .env file contains: SLACK_BOT_TOKEN=your_token_here")
    print("3. No spaces around the = sign")
    print("4. Token starts with 'xoxb-'")
    raise ValueError("SLACK_BOT_TOKEN not found in environment variables")
else:
    print(f"✅ SLACK_BOT_TOKEN found (starts with: {slack_token[:10]}...)")
    print(f"Token length: {len(slack_token)}")

# Initialize Slack client
slack_client = WebClient(token=slack_token)

def read_story_node(state):
    story_url = "https://medium.com/data-science/developers-documentation-to-openapi-specification-d73a0c19e86c"
    content = get_medium_story_text(story_url)
    return [HumanMessage(content=f"Here is a story from Medium to refine:\n\n{content}")]

def generation_node(state: Sequence[BaseMessage]):
    result = generate_chain.invoke({"messages": state})
    return [AIMessage(content=result)]

def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    result = reflect_chain.invoke({"messages": messages})
    return [HumanMessage(content=result)]

def slack_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    try:
        final_message = messages[-1].content
        print("📤 Slack node reached! Sending message...")
        
        # Truncate message if too long (Slack has message limits)
        max_length = 3000  # Conservative limit
        if len(final_message) > max_length:
            truncated_message = final_message[:max_length] + "...\n\n[Message truncated due to length]"
        else:
            truncated_message = final_message
        
        # Send to Slack using the Slack SDK directly
        response = slack_client.chat_postMessage(
            channel="#ai-notifications-medium",
            text=f"📢 Final Medium blog refined:\n\n{truncated_message}"
        )
        
        print(f"✅ Slack message sent successfully!")
        print(f"   Channel: {response['channel']}")
        print(f"   Timestamp: {response['ts']}")
        return messages
        
    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
        print(f"   Details: {e.response.get('message', 'No additional details')}")
        # Common error explanations
        if e.response['error'] == 'channel_not_found':
            print("   → Make sure the channel exists and the bot is added to it")
        elif e.response['error'] == 'not_in_channel':
            print("   → Add the bot to the channel with: /invite @YourBotName")
        elif e.response['error'] == 'invalid_auth':
            print("   → Check your bot token is correct")
        return messages
        
    except Exception as e:
        print(f"❌ Unexpected error sending Slack message: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return messages

def should_continue(state: List[BaseMessage]):
    print(f"🔍 should_continue: message count = {len(state)}")
    
    # Add logic to determine when to reflect vs when to send to Slack
    # For now, always go to Slack after first generation
    # You might want to add reflection logic here based on your needs
    
    return SEND_SLACK

# Alternative should_continue with reflection logic (uncomment if needed)
"""
def should_continue(state: List[BaseMessage]):
    print(f"🔍 should_continue: message count = {len(state)}")
    
    # If we have less than 4 messages, continue reflecting
    # Adjust this logic based on your needs
    if len(state) < 4:
        return REFLECT
    else:
        return SEND_SLACK
"""

builder = MessageGraph()
builder.add_node("read", read_story_node)
builder.add_node(GENERATE, generation_node)
builder.add_node(REFLECT, reflection_node)
builder.add_node(SEND_SLACK, slack_node)

builder.set_entry_point("read")
builder.add_edge("read", GENERATE)
builder.add_conditional_edges(GENERATE, should_continue)
builder.add_edge(REFLECT, GENERATE)
builder.add_edge(SEND_SLACK, END)

graph = builder.compile()
print(graph.get_graph().draw_mermaid())
graph.get_graph().print_ascii()

# Test Slack connection separately (uncomment to test)
def test_slack_connection():
    try:
        print("🧪 Testing Slack connection...")
        response = slack_client.chat_postMessage(
            channel="#general",  # Use a channel you know exists
            text="🧪 Test message from LangGraph Blog Refiner"
        )
        print(f"✅ Slack test successful!")
        print(f"   Channel: {response['channel']}")
        print(f"   Timestamp: {response['ts']}")
        return True
    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
        print(f"   Details: {e.response.get('message', 'No additional details')}")
        return False
    except Exception as e:
        print(f"❌ Slack test failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

# Uncomment to test Slack before running main flow
# test_slack_connection()

if __name__ == "__main__":
    print("🟢 Running LangGraph Blog Refiner with Slack update...")
    
    try:
        response = graph.invoke([])
        print("\n✅ Final Improved Blog Post:\n")
        print(response[-1].content)
    except Exception as e:
        print(f"❌ Error running graph: {str(e)}")
        print(f"Error type: {type(e).__name__}")