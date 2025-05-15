from typing import List, Sequence
from dotenv import load_dotenv
from langgraph.graph import END, MessageGraph
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_community.tools.slack.send_message import SlackSendMessage

from chains import generate_chain, reflect_chain
from medium_utils import get_medium_story_text
import os

load_dotenv()

REFLECT = "reflect"
GENERATE = "generate"
SEND_SLACK = "send_slack"

# Ensure the Slack token is available
slack_token = os.getenv("SLACK_BOT_TOKEN")
if not slack_token:
    raise ValueError("SLACK_BOT_TOKEN not found in environment variables")

# Initialize Slack tool
slack_tool = SlackSendMessage(slack_token=slack_token)

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
    final_message = messages[-1].content
    slack_tool.invoke({
        "message": f"📢 Final Medium blog refined:\n\n{final_message}",
        "channel": "#ai-notifications-medium"
    })
    return messages

def should_continue(state: List[BaseMessage]):
    if len(state) > 6:
        return SEND_SLACK
    return REFLECT

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

if __name__ == "__main__":
    print("🟢 Running LangGraph Blog Refiner with Slack update...")
    response = graph.invoke([])
    print("\n✅ Final Improved Blog Post:\n")
    print(response[-1].content)