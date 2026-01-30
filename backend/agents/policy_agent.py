"""
HR Policy RAG Agent
Handles questions about HR policies using RAG
"""
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from services.vector_store import HRVectorStore


class HRPolicyAgent:
    """Agent for answering HR policy questions using RAG"""

    def __init__(self, mistral_api_key: str, vector_store: HRVectorStore):
        self.llm = ChatMistralAI(
            model="mistral-large-latest",
            mistral_api_key=mistral_api_key,
            temperature=0.1,
            max_tokens=1024
        )
        self.vector_store = vector_store

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert HR Policy Assistant. Your role is to answer questions about company HR policies accurately and helpfully.

IMPORTANT INSTRUCTIONS:
1. Use ONLY the provided context to answer questions
2. If the information is not in the context, say "I don't have specific information about that in our policy documents. Please contact HR directly."
3. Be precise and cite specific policy details, numbers, and dates when available
4. If asked about procedures, provide clear step-by-step guidance
5. Format your response clearly with bullet points or numbered lists when appropriate
6. Be professional, helpful, and empathetic

CONTEXT FROM HR POLICIES:
{context}

Remember: Only use information from the context above. Do not make up policy details."""),
            ("human", "{query}")
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

    def get_relevant_context(self, query: str, k: int = 5) -> str:
        """Retrieve relevant policy context for the query"""
        docs = self.vector_store.search(query, k=k)

        if not docs:
            return "No relevant policy documents found."

        context_parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "Unknown")
            policy_type = doc.metadata.get("policy_type", "general")
            context_parts.append(
                f"[Document {i} - {source} ({policy_type})]:\n{doc.page_content}"
            )

        return "\n\n---\n\n".join(context_parts)

    async def answer(self, query: str) -> str:
        """Answer a policy question using RAG"""
        # Get relevant context
        context = self.get_relevant_context(query)

        # Generate response
        response = await self.chain.ainvoke({
            "context": context,
            "query": query
        })

        return response

    def answer_sync(self, query: str) -> str:
        """Synchronous version of answer"""
        context = self.get_relevant_context(query)

        response = self.chain.invoke({
            "context": context,
            "query": query
        })

        return response
