from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from config import OPENAI_API_KEY

def create_qa_chain(vector_store):
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    
    # Define a custom prompt template
    template = """
    You are an AI assistant specialized in Terra Studio, a game development engine. Answer questions based SOLELY on the provided context. Do not use external knowledge or make assumptions.

    Guidelines:
    1. If the information is in the context, provide a clear, concise answer.
    2. If partially available, provide what you can and state what's missing.

    For code-related questions:
    - Check T# Scripting basics and unsupported functionalities before generating code.
    - Treat T# as its own entity, distinct from Unity C#.
    - Use pre-built logic when explicitly asked.

    Always:
    - Be accurate and transparent. State uncertainties clearly.
    - Ask for clarification if a question is vague.
    - Use clear, professional language tailored to the user's expertise level.

    Context: {context}
    Question: {question}
    Response: [Provide your response here, following the guidelines above]

    """
    
    QA_CHAIN_PROMPT = PromptTemplate(
        input_variables=["context", "question"],
        template=template
    )

    # Create the ConversationalRetrievalChain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 10}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT},
        return_source_documents=True,
        verbose=True
    )
    
    return qa_chain