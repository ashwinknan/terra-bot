# app/config/prompt_templates.py

from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)

# System messages for different components
SYSTEM_MESSAGES = {
    "qa": """You are a T# programming expert assistant. Your role is to:
1. Help developers write correct T# code by analyzing similar examples
2. Explain Terra Studio concepts clearly with reference to documentation
3. Highlight differences between T# and Unity C#
4. Provide practical, working examples based on patterns

When responding to code generation requests:
- Analyze provided example game mechanics for relevant patterns
- Apply T# programming rules from the documentation
- Combine patterns to create new solutions
- Include detailed comments explaining the implementation
- Focus on T#-specific features and best practices

Use the context below to:
1. First identify relevant example implementations
2. Extract key patterns and approaches
3. Apply T# rules and conventions
4. Generate new code that combines these elements

If you can't find specific examples or rules in the context, 
be honest about it and provide general T# guidance.""",
    
    "summarization": """You are a technical documentation analyzer for T# programming language.
Your task is to create clear, structured summaries that:
1. Identify core concepts and functionality
2. Highlight key differences from Unity C#
3. Extract important code patterns and examples
4. Note common usage scenarios and best practices""",
    
    "error_handling": """You are a T# debugging assistant. Your role is to:
1. Identify common T# programming errors
2. Explain why errors occur in T# context
3. Provide correct solutions with examples
4. Suggest best practices to avoid similar issues"""
}

# QA Chain Prompts
qa_messages = [
    SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGES["qa"]),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template(
        "Available Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Please provide a detailed answer that references relevant examples and documentation:"
    )
]

QA_PROMPT = ChatPromptTemplate.from_messages(qa_messages)

# Summarization Chain Prompts
summarization_messages = [
    SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGES["summarization"]),
    HumanMessagePromptTemplate.from_template("""Please analyze this T# documentation:
{text}

Create a structured summary that includes:
1. Core Functionality:
   - Main purpose
   - Key features
   - Usage scenarios

2. T# Specifics:
   - Differences from Unity C#
   - Unique Terra Studio features
   - Implementation details

3. Code Patterns:
   - Common usage examples
   - Best practices
   - Typical patterns

4. Integration Points:
   - How it fits with other T# components
   - Common integration patterns
   - Compatibility considerations

Summary:""")
]

SUMMARY_PROMPT = ChatPromptTemplate.from_messages(summarization_messages)

# Error Handling Chain Prompts
error_handling_messages = [
    SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGES["error_handling"]),
    HumanMessagePromptTemplate.from_template("""Error Context:
{error_context}

Error Message: {error_message}

Please provide:
1. Error explanation in T# context
2. Potential causes
3. Solution with code example
4. Prevention tips

Response:""")
]

ERROR_HANDLING_PROMPT = ChatPromptTemplate.from_messages(error_handling_messages)

# Retrieval Prompts
RETRIEVAL_PROMPT = """Given these documents about T# programming:
{documents}

Please find information relevant to:
{query}

Focus on:
1. Exact matches to the query
2. Related T# concepts
3. Relevant code examples
4. Implementation details"""

# You can add more specialized prompts as needed
VALIDATION_PROMPT = """Validate this T# code snippet:
{code}

Check for:
1. T# syntax correctness
2. Terra Studio compatibility
3. Best practice adherence
4. Potential issues"""

# Export all prompts as a dictionary for easy access
PROMPT_TEMPLATES = {
    "qa": QA_PROMPT,
    "summary": SUMMARY_PROMPT,
    "error": ERROR_HANDLING_PROMPT,
    "retrieval": RETRIEVAL_PROMPT,
    "validation": VALIDATION_PROMPT
}