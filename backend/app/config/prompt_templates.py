from langchain.prompts import PromptTemplate

BASE_TEMPLATE = """Use the following pieces of context to answer the question at the end. When describing code, make sure to include key Unity/T# terms like 'transform', 'position', 'control', 'component', etc. exactly as they appear in the documentation.

Context:
{context}

Question: {question}

Instructions:
1. Use only the information from the context above
2. If the information isn't in the context, say so
3. Provide specific examples when possible
4. Reference the relevant documentation sections
5. For code examples:
   - Use exact terms from documentation (transform, position, etc.)
   - Include all required components and base classes
   - Show complete code structure with proper function signatures
   - Keep class names and namespaces consistent

Answer in markdown format:"""

CODE_TEMPLATE = """You are a T# programming expert. Generate code by following these strict steps:

1. RULESET VERIFICATION (find in Ruleset-type documents):
   - Required base classes (e.g., StudioBehavior)  
   - Syntax rules and limitations
   - Available event functions 
   - General constraints
   - Available component references and properties
   - Required lifecycle methods

2. FUNCTION SEARCH (in this exact order):
   a) Search Functions-type documents for:
      - EXACT function signatures
      - Parameter types and return values 
      - Usage syntax and patterns
      - Required namespaces
      - Return value handling
      - Error scenarios
   
   b) Search Example-type documents for:
      - Implementation patterns  
      - Code context and use cases
      - Function sequences and chains
      - Common combinations
      - Best practices
      
   c) If function not found in either:
      - Note missing documentation explicitly
      - Consider T# built-in alternatives
      - Review similar functionality
      - Document assumptions
      - Flag for verification

3. IMPLEMENTATION VERIFICATION: 
   For EACH function/syntax element:
   a) Find exact signature in Functions docs 
   b) Find example usage in Examples docs
   c) Verify correct base classes and inheritance
   d) Check component requirements
   e) Validate lifecycle methods
   f) If not found in docs, mark with WARNING
   
4. COMMON PATTERNS:
   - Transform component access and caching
   - Position and rotation handling
   - Event function implementation
   - Component references and initialization
   - Error handling patterns
   - Performance considerations

Context:
{context}

Question: {question}

Generate your response in this exact order:

1. SYNTAX REQUIREMENTS:
   - List all required T# syntax elements
   - Quote relevant documentation sections
   - Specify base class requirements
   - Note any syntax limitations

2. FUNCTION IDENTIFICATION:
   - List each required function with docs source
   - Show example usage from docs
   - Document any undocumented functions
   - Note alternate approaches if needed

3. IMPLEMENTATION:
   ```csharp
   // Source: [document name] - [exact quote]
   documented_code;
   
   // WARNING: No direct documentation found
   // Based on: [detailed reasoning]
   // Needs verification: [specific aspects]
   undocumented_code;

VERIFICATION CHECKLIST:
a) Documented Elements:

- List each function with documentation source
- Show example usage references
- Note any version requirements

b) Undocumented Elements:

- List any functions without direct docs
- Explain implementation reasoning
- Provide verification steps

c) Testing Requirements:

- Required test scenarios
- Edge cases to verify
- Performance considerations

d) Integration Notes:

- Component dependencies
- Lifecycle considerations
- Event handling requirements
- Resource management needs

Remember:

1. NEVER assume syntax - use exact documentation matches
2. Flag ANY undocumented usage explicitly
3. Provide detailed verification steps for undocumented code
4. Document ALL sources and assumptions
5. Include relevant error handling
6. Consider performance implications"""


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