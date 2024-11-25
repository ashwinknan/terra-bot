import logging
from typing import Any, Dict, List
from threading import Thread, Event
import time
from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import Chroma
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from app.config.settings import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    VECTOR_STORE_TOP_K,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS
)
from app.config.prompt_templates import PROMPT_TEMPLATES

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
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="history",
            output_key="answer"
        )
        
        self.output_parser = StrOutputParser()
        self.qa_chain = None
        self.code_chain = None
        self.error_chain = None
        self.retriever = None
        self.last_sources = []
        
        # Initialize thread pool executor
        self.executor = ThreadPoolExecutor(max_workers=1)

    def create_qa_chain(self, vector_store: Chroma) -> Any:
        """Create a conversational retrieval chain"""
        try:
            logger.info("Creating QA chain...")
            
            # Set up retriever
            self.retriever = vector_store.as_retriever(
                search_kwargs={"k": VECTOR_STORE_TOP_K}
            )

            # Define document formatting
            def format_docs(docs):
                self.last_sources = docs
                texts = [str(doc.page_content) for doc in docs]
                return "\n\n".join(texts)

            # Create context getter
            def get_context(inputs):
                question = str(inputs["question"])
                docs = self.retriever.invoke(question)
                return {"context": format_docs(docs), "question": question}

            # Create the specialized chains
            self.qa_chain = (
                RunnablePassthrough.assign(context=get_context) 
                | PROMPT_TEMPLATES["qa"] 
                | self.llm 
                | self.output_parser
            )

            self.code_chain = (
                RunnablePassthrough.assign(context=get_context)
                | PROMPT_TEMPLATES["code"] 
                | self.llm 
                | self.output_parser
            )

            self.error_chain = (
                RunnablePassthrough.assign(context=get_context)
                | PROMPT_TEMPLATES["error"] 
                | self.llm 
                | self.output_parser
            )

            logger.info("QA chain created successfully")
            return self.qa_chain

        except Exception as e:
            logger.error(f"Error creating QA chain: {str(e)}")
            raise

    def process_query(self, chain: Any, query: str) -> Dict[str, Any]:
        """Process a query using appropriate chain with timeout"""
        try:
            if not query or not isinstance(query, str) or not query.strip():
                return {
                    "answer": "Please provide a valid question.",
                    "sources": [],
                    "chat_history": []
                }

            # Clean query
            query = " ".join(query.strip().split())
            self.last_sources = []  # Reset sources

            # Select chain based on query type
            query_type = self.determine_query_type(query)
            selected_chain = getattr(self, f"{query_type}_chain", chain)

            try:
                # Submit query processing to thread pool with timeout
                future = self.executor.submit(self._process_query_internal, selected_chain, query)
                response = future.result(timeout=60)  # 60 second timeout
                
                return response

            except TimeoutError:
                logger.error("Query processing timed out")
                return {
                    "answer": "The request timed out. Please try a shorter or simpler question.",
                    "sources": [],
                    "chat_history": self.get_chat_history()
                }
            except Exception as e:
                logger.error(f"Chain error: {str(e)}")
                return {
                    "answer": f"Error processing query: {str(e)}",
                    "sources": [],
                    "chat_history": self.get_chat_history()
                }

        except Exception as e:
            logger.error(f"Error in process_query: {str(e)}", exc_info=True)
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "chat_history": self.get_chat_history()
            }

    def _process_query_internal(self, chain: Any, query: str) -> Dict[str, Any]:
        """Internal method to process query without timeout logic"""
        response = chain.invoke({"question": query})
        
        if isinstance(response, str):
            self.memory.chat_memory.add_user_message(query)
            self.memory.chat_memory.add_ai_message(response)
        
        return {
            "answer": response,
            "sources": [doc.metadata.get('source', 'Unknown') for doc in self.last_sources],
            "chat_history": self.get_chat_history()
        }

    def determine_query_type(self, query: str) -> str:
        """Determine the type of query to select appropriate chain"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['error', 'bug', 'fix', 'issue', 'debug', 'null']):
            return 'error'
        
        if any(word in query_lower for word in ['create', 'generate', 'write', 'code', 'implement']):
            return 'code'
        
        return 'qa'

    def get_chat_history(self) -> List[BaseMessage]:
        """Get chat history messages"""
        try:
            return self.memory.chat_memory.messages
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []

    def clear_memory(self) -> None:
        """Clear conversation memory"""
        try:
            self.memory.clear()
            logger.info("Conversation memory cleared")
        except Exception as e:
            logger.error(f"Error clearing memory: {str(e)}")

    def __del__(self):
        """Cleanup method"""
        try:
            self.executor.shutdown(wait=False)
        except:
            pass