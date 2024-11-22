import logging
from app.config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL
from langchain_anthropic import ChatAnthropic

logger = logging.getLogger(__name__)

def check_llm_connection():
    """Test the LLM connection and basic functionality"""
    try:
        llm = ChatAnthropic(
            model_name=CLAUDE_MODEL,
            anthropic_api_key=ANTHROPIC_API_KEY,
            temperature=0
        )
        response = llm.invoke("Say 'test successful' if you can read this.")
        
        if "test successful" in response.content.lower():
            logger.info("LLM test successful")
            return True
        else:
            logger.error("LLM test failed - unexpected response")
            return False
            
    except Exception as e:
        logger.error(f"LLM test failed with error: {str(e)}")
        return False