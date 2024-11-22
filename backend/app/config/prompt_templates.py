from langchain.prompts import PromptTemplate

BASE_TEMPLATE = """Use the following pieces of context to answer the question at the end.

Context:
{context}

Question: {question}

Instructions:
1. Use only the information from the context above
2. If the information isn't in the context, say so
3. Provide specific examples when possible
4. Reference the relevant documentation sections

Answer in markdown format:"""

CODE_TEMPLATE = """You are a T# programming expert. Generate code by following these strict steps:

1. RULESET VERIFICATION (find in Ruleset-type documents):
   - Required base classes (e.g., StudioBehavior)
   - Syntax rules and limitations
   - Available event functions
   - General constraints

2. FUNCTION SEARCH (in this exact order):
   a) Search Functions-type documents for:
      - EXACT function signatures
      - Parameter types and return values
      - Usage syntax
      - Required namespaces
   
   b) Search Example-type documents for:
      - Implementation patterns of these functions
      - Context in which functions are used
      - Proper function chaining or sequences

   c) If function not found in either:
      - Note absence of documented function
      - Consider alternative T# approaches
      - Only then consider Unity/C# alternatives

3. IMPLEMENTATION VERIFICATION:
   For EACH function or syntax element you plan to use:
   a) Find exact signature in Functions documentation
   b) Find exact usage example in Example documentation
   c) If not found in either, mark as "NEEDS VERIFICATION"

Context:
{context}

Question: {question}

Generate your response in this order:
1. SYNTAX REQUIREMENTS:
   - List exact T# syntax rules found
   - Quote relevant documentation sections
   - Identify required base classes

2. FUNCTION IDENTIFICATION:
   For each function needed:
   - Quote exact signature from Functions docs
   - Quote example usage from Example docs
   - List any functions not found in either

3. CODE GENERATION:
   Write code with inline documentation for EACH line:
   ```csharp
   // Source: [document name] - [exact quote]
   line of code;
   
   // WARNING: No direct documentation found - based on [reasoning]
   undocumented line of code;
   ```

4. VERIFICATION CHECKLIST:
   - List each function used with documentation source
   - Flag any undocumented usage
   - Suggest areas needing verification

Remember:
1. NEVER guess at syntax - use exact matches from documentation
2. If you can't find exact syntax in Functions or Examples, mark it clearly
3. Quote relevant documentation for each implementation choice
4. Each function must have either:
   - Direct reference to Functions documentation, or
   - Example usage from Example documentation, or
   - Clear warning about lack of documentation"""

ERROR_TEMPLATE = """You are debugging T# code. For each line of code:

1. Find exact syntax rules in Ruleset-type documents
2. Match function usage against Functions-type documents
3. Compare implementation with Example-type documents

Context:
{context}

Question: {question}

Format your answer with:
1. LINE BY LINE ANALYSIS:
   - Quote relevant documentation for each line
   - Flag any syntax without documentation
   - Note discrepancies from documented patterns

2. ISSUES FOUND:
   - Undocumented function usage
   - Syntax pattern mismatches
   - Ruleset violations

3. CORRECTIONS:
   - Quote correct syntax from documentation
   - Show example usage from documentation
   - Explain any necessary changes

4. VERIFICATION STEPS"""

PROMPT_TEMPLATES = {
    "qa": PromptTemplate(
        template=BASE_TEMPLATE,
        input_variables=["context", "question"]
    ),
    "code": PromptTemplate(
        template=CODE_TEMPLATE,
        input_variables=["context", "question"]
    ),
    "error": PromptTemplate(
        template=ERROR_TEMPLATE,
        input_variables=["context", "question"]
    )
}