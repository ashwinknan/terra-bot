from langchain.prompts import PromptTemplate

BASE_TEMPLATE = """Use the following pieces of context to answer the question at the end.

Context:
{context}

Question: {question}

Instructions:
1. Use the information from the context above with 
2. If the information isn't in the context, say so
3. Provide specific examples when possible
4. Reference the relevant documentation sections
5. For code examples:
   - Use exact terms from documentation (transform, position, etc.)
   - Include all required components and base classes
   - Show complete code structure with proper function signatures
   - Keep class names and namespaces consistent

Answer in markdown format:"""

CODE_TEMPLATE = """You are a T# programming expert tasked with generating code for Unity-like environments while adhering to specific T# limitations. Your goal is to provide accurate, well-documented code that follows T# best practices and limitations.

First, review the following context and question:

Context:
<context>
{context}
</context>

Question:
<question>
{question}
</question>

Before generating code, carefully analyze the problem and consider T# limitations. Wrap your analysis inside <t_sharp_analysis> tags:

<t_sharp_analysis>
1. List all Unity functions mentioned in the context and question.
2. Identify the key Unity functions required for this task.
3. For each function, check if it's affected by T# limitations:
   - If affected, describe the T# alternative or modification needed.
   - If not affected, note that it can be used as in standard Unity.
4. Consider any potential performance implications or error handling requirements.
5. Identify potential edge cases and error scenarios.
6. Plan the overall structure of your code, including necessary comments and documentation.
7. List any additional T# specific considerations not covered in the previous steps.
</t_sharp_analysis>

Now, generate the T# code based on your analysis. Follow these guidelines:

1. Use standard Unity syntax unless a T# limitation applies.
2. Always ensure that the class inherits from 'StudioBehavior' and not 'MonoBehavior'
2. For each T# limitation, use the appropriate alternative:
   - Replace GetComponent<T>() with GetComponent(typeof(T))
   - Wait for 1 frame after GameObject instantiation
   - Use alternative methods for Destroy() and Instantiate() as T# overrides are missing
   - Avoid onEnable() and Awake()
   - Use StartCoroutine() instead of InvokeRepeating()
   - Use "as" keyword instead of casting
   - Use TerraList instead of IList derivatives
   - Use TerraDictionary for key-value pairs
   - Don't store component references in TerraDictionary

3. Format your code as follows:
   ```csharp
   // Source: [document name] - [exact quote or 'Based on T# limitation']
   // Purpose: [Brief explanation of the code's function]
   [Your code here]

   // WARNING: No direct documentation found (if applicable)
   // Based on: [detailed reasoning]
   // Needs verification: [specific aspects]
   [Undocumented or adapted code]
   ```

4. After the code block, provide a verification checklist:

Verification Checklist:
a) Documented Elements:
   - [List each function with documentation source]
   - [Show example usage references]
   - [Note any version requirements]

b) Undocumented Elements:
   - [List any functions without direct docs]
   - [Explain implementation reasoning]
   - [Provide verification steps]

Remember:
1. Always check Unity functions against T# limitations before use.
2. Provide detailed comments and documentation for all code.
3. Flag any undocumented usage explicitly.
4. Include relevant error handling and performance considerations.
5. Ensure all T# specific syntax and limitations are correctly applied."""


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