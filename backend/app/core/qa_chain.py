import logging
from typing import Any, Dict, List

from langchain_anthropic import ChatAnthropic
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


from app.config.settings import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    VECTOR_STORE_TOP_K,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    RETRIEVAL_MODE,
    MMR_DIVERSITY_SCORE
)
from app.config.prompt_templates import SYSTEM_MESSAGES

logger = logging.getLogger(__name__)

class QAChainManager:
    def __init__(self):
        """Initialize QA Chain Manager with custom settings"""
        self.llm = ChatAnthropic(
            model=CLAUDE_MODEL,
            anthropic_api_key=ANTHROPIC_API_KEY,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS
        )
        
        # Initialize empty chat history
        self.chat_memory = ChatMessageHistory()

    def create_qa_chain(self, vector_store: Chroma) -> ConversationalRetrievalChain:
        """Create a conversational retrieval chain"""
        try:
            logger.info("Creating QA chain...")
            
            # Configure retriever
            search_kwargs = {"k": VECTOR_STORE_TOP_K}
            if RETRIEVAL_MODE == "mmr":
                search_kwargs["fetch_k"] = VECTOR_STORE_TOP_K * 2
                search_kwargs["lambda_mult"] = MMR_DIVERSITY_SCORE
            
            retriever = vector_store.as_retriever(
                search_type=RETRIEVAL_MODE,
                search_kwargs=search_kwargs
            )

            # Create the memory
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                output_key="answer",
                return_messages=True
            )

            # Create the QA prompt
            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", SYSTEM_MESSAGES["qa"]),
                ("human", "Using the following context, answer the question. Context: {context}\n\nQuestion: {question}")
            ])

            # Create the conversational chain
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory,
                get_chat_history=lambda h: h,  # Just return the history as is
                verbose=True,
                return_source_documents=True
            )

            logger.info(f"QA chain created successfully with {RETRIEVAL_MODE} retrieval")
            return qa_chain

        except Exception as e:
            logger.error(f"Error creating QA chain: {str(e)}")
            logger.error("Exception details:", exc_info=True)
            raise

    def process_query(self, chain: ConversationalRetrievalChain, query: str) -> Dict[str, Any]:
        """Process a query using the QA chain"""
        try:
            if not query or not isinstance(query, str) or not query.strip():
                return {
                    "answer": "Please provide a valid question.",
                    "source_documents": [],
                    "chat_history": []
                }

            # Add the user's question to chat history
            self.chat_memory.add_user_message(query)
            
            # Get current chat history as a list of messages
            current_history = []
            for i in range(0, len(self.chat_memory.messages), 2):
                if i + 1 < len(self.chat_memory.messages):
                    # Add pairs of messages (human and ai)
                    current_history.extend([
                        self.chat_memory.messages[i],
                        self.chat_memory.messages[i + 1]
                    ])

            # Process the query
            result = chain({
                "question": query,
                "chat_history": current_history
            })

            # Extract answer and sources
            answer = result.get("answer", "")
            sources = result.get("source_documents", [])

            # Add the assistant's response to chat history
            if answer:
                self.chat_memory.add_ai_message(answer)

            return {
                "answer": answer or "An error occurred while processing your question.",
                "source_documents": sources,
                "chat_history": self.chat_memory.messages
            }

        except Exception as e:
            logger.error(f"Error in process_query: {str(e)}")
            logger.error("Full exception details:", exc_info=True)
            self.clear_memory()
            return {
                "answer": f"An error occurred while processing your question: {str(e)}",
                "source_documents": [],
                "chat_history": []
            }

    def get_chat_history(self) -> List[BaseMessage]:
        """Get properly formatted chat history"""
        try:
            return self.chat_memory.messages
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []

    def clear_memory(self) -> None:
        """Clear conversation memory"""
        try:
            self.chat_memory.clear()
            logger.info("Conversation memory cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing memory: {str(e)}")