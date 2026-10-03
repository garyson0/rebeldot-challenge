"""Prompt templates used by the assistant"""

from langchain_core.prompts import ChatPromptTemplate

ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful customer support assistant for a software product. "
            "Answer the user's question about their account, security, billing or the app "
            "briefly and clearly. If the answer depends on the specific platform, say so.",
        ),
        ("human", "{question}"),
    ]
)
