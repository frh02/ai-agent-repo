from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# Instantiate the model
llm = OllamaLLM(model="mistral")

# Prompt for blog generation
generate_prompt = PromptTemplate.from_template("""
You are a professional blog writer. Rewrite the blog post to follow this structure:

- Title
- Introduction
- Main Content
- Conclusion
- Optional Call-to-Action

Improve clarity, flow, grammar, and engagement.

BLOG DRAFT:
{messages}
""")

# Prompt for blog reflection/refinement
reflect_prompt = PromptTemplate.from_template("""
Review the improved blog post and suggest a refinement or better phrasing if needed.

BLOG POST:
{messages}
""")

# Define chains as runnable sequences
generate_chain = generate_prompt | llm
reflect_chain = reflect_prompt | llm