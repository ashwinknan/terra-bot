import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
if app.debug:
    # Development environment
    CORS(app, resources={r"/ask": {"origins": "http://localhost:3000"}})
else:
    # Production environment
    allowed_origin = os.environ.get('ALLOWED_ORIGIN', 'https://rag-game-assistant-frontend.onrender.com')
    CORS(app, resources={r"/ask": {"origins": allowed_origin}})

# Initialize OpenAI API
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model_name="gpt-4", temperature=0, openai_api_key=openai_api_key)

# Load and process documents
def load_documents():
    documents = []
    for filename in os.listdir('knowledge_base'):
        filepath = os.path.join('knowledge_base', filename)
        if filename.endswith('.pdf'):
            loader = PyPDFLoader(filepath)
        elif filename.endswith('.md'):
            loader = TextLoader(filepath)
        else:
            continue
        documents.extend(loader.load())
    return documents

documents = load_documents()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=250)
texts = text_splitter.split_documents(documents)

# Create vector store
embeddings = OpenAIEmbeddings()
db = Chroma.from_documents(texts, embeddings)

# Create conversation chain
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
qa = ConversationalRetrievalChain.from_llm(llm, db.as_retriever(), memory=memory)

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data['question']
    result = qa({"question": question})
    return jsonify({"answer": result['answer']})


#@app.route('/rate', methods=['POST'])
#def rate_response():
    #data = request.json
    #rating = data['rating']
    # Here you would typically store the rating in a database
    #return jsonify({"status": "Rating received"})

#@app.route('/update-index', methods=['POST'])
#def update_index():
    #if request.headers.get('X-Api-Key') != os.getenv('UPDATE_INDEX_API_KEY'):
        #return jsonify({"error": "Unauthorized"}), 401
       
    #try:
        #global documents, texts, db, qa
        #documents = load_documents()
        #texts = text_splitter.split_documents(documents)
        #db = Chroma.from_documents(texts, embeddings)
        #qa = ConversationalRetrievalChain.from_llm(llm, db.as_retriever(), memory=memory)
        #return jsonify({"status": "Index updated successfully"})
    #except Exception as e:
        #return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)