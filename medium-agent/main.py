from typing import List, Sequence

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph
from chains import generate_chain, reflect_chain
from langchain_core.messages import AIMessage
from medium_utils import get_medium_story_text

REFLECT = "reflect"
GENERATE = "generate"

def read_story_node(state):
    story_url = "https://medium.com/data-science/developers-documentation-to-openapi-specification-d73a0c19e86c"
    content = get_medium_story_text(story_url)
    return [HumanMessage(content=f"Here is a story from Medium to refine:\n\n{content}")]

def generation_node(state: Sequence[BaseMessage]):
    result = generate_chain.invoke({"messages": state})
    return [AIMessage(content=result)]  # `result` is already a string


def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    result = reflect_chain.invoke({"messages": messages})
    return [HumanMessage(content=result)]  # same here

builder = MessageGraph()
builder.add_node("read", read_story_node)
builder.add_node(GENERATE, generation_node)
builder.add_node(REFLECT, reflection_node)

builder.set_entry_point("read")
builder.add_edge("read", GENERATE)


def should_continue(state: List[BaseMessage]):
    if len(state) > 6:
        return END
    return REFLECT


builder.add_conditional_edges(GENERATE, should_continue)
builder.add_edge(REFLECT, GENERATE)

graph = builder.compile()
print(graph.get_graph().draw_mermaid())
graph.get_graph().print_ascii()

if __name__ == "__main__":
    print("🟢 Running LangGraph Blog Refiner...")
    response = graph.invoke([])  # Start with empty state
    print("\n✅ Final Improved Blog Post:\n")
    print(response[-1].content)