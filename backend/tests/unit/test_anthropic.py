# app/tests/unit/test_anthropic.py

import unittest
import logging
import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from app.config.settings import ANTHROPIC_API_KEY, CLAUDE_MODEL
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAnthropicChain(unittest.TestCase):
    """Test cases for ChatAnthropic functionality"""

    def setUp(self):
        """Set up test environment before each test"""
        self.llm = ChatAnthropic(
            model=CLAUDE_MODEL,
            anthropic_api_key=ANTHROPIC_API_KEY,
            temperature=0
        )

    def test_model_direct(self):
        """Test ChatAnthropic directly without chain"""
        try:
            response = self.llm.invoke("Say 'test successful' if you can read this.")
            logger.info(f"Direct model test result: {response}")
            self.assertIsNotNone(response)
        except Exception as e:
            logger.error(f"Direct model test failed: {str(e)}")
            raise

    def test_chat_messages(self):
        """Test ChatAnthropic with chat messages"""
        try:
            messages = [
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content="Say 'test successful' if you can read this.")
            ]
            response = self.llm.invoke(messages)
            logger.info(f"Chat message test result: {response}")
            self.assertIsNotNone(response)
        except Exception as e:
            logger.error(f"Chat message test failed: {str(e)}")
            raise

    def test_simple_chain(self):
        """Test simple chain with ChatAnthropic"""
        try:
            # Create a chat prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant."),
                ("human", "{input}")
            ])
            
            chain = prompt | self.llm
            
            result = chain.invoke({"input": "Say 'test successful' if you can read this."})
            logger.info(f"Simple chain test result: {result}")
            self.assertIsNotNone(result)
        except Exception as e:
            logger.error(f"Simple chain test failed: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            raise

def print_package_versions():
    """Print relevant package versions"""
    import pkg_resources
    packages = [
        'langchain',
        'langchain-anthropic',
        'langchain-core',
        'langchain-community',
        'anthropic'
    ]
    
    logger.info("\nInstalled package versions:")
    for package in packages:
        try:
            version = pkg_resources.get_distribution(package).version
            logger.info(f"{package}: {version}")
        except pkg_resources.DistributionNotFound:
            logger.warning(f"{package} not found")

if __name__ == '__main__':
    print_package_versions()
    unittest.main(verbosity=2)