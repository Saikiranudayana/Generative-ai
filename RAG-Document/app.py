import streamlit as st 
import os
import time
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS 
from langchain_community.document_loaders import PyPDFDirectoryLoader 
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter  
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate 

import os.path
from dotenv import load_dotenv
## load groq api key 
# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_dir = os.path.dirname(current_dir)
# Specify the path to .env file
env_path = os.path.join(parent_dir, '.env')

# Load the environment variables from the specified path
load_dotenv(env_path)

# Get the API key
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("GROQ_API_KEY not found in .env file. Please make sure it's set correctly.")
    st.stop() 

llm = ChatGroq(groq_api_key=groq_api_key,model="Llama3-8b-8192")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant."),
    ("human", """
    Answer the question based on the provided context.
    Response to the best of your ability for the question.
    
    Context:
    {context}
    
    Question: {input}
    """)
])

def create_vector_embeddings():
    if "vectors" not in st.session_state:
        try:
            # Check if Research Papers directory exists
            research_papers_path = os.path.join(os.path.dirname(__file__), "Research Papers")
            if not os.path.exists(research_papers_path):
                st.error(f"Directory 'Research Papers' not found. Please create it and add PDF files.")
                st.stop()
            
            # Check if directory contains PDF files
            pdf_files = [f for f in os.listdir(research_papers_path) if f.lower().endswith('.pdf')]
            if not pdf_files:
                st.error("No PDF files found in the Research Papers directory. Please add some PDF files.")
                st.stop()
            
            # Try to use OllamaEmbeddings first, fallback to OpenAI if not available
            try:
                # Try with a more common model first
                st.session_state.embeddings = OllamaEmbeddings(model="nomic-embed-text")
            except Exception as e:
                st.warning("Ollama embeddings not available. Trying alternative model...")
                try:
                    st.session_state.embeddings = OllamaEmbeddings(model="llama3")
                except Exception as e2:
                    st.warning("Ollama not available. Using OpenAI embeddings instead...")
                    # Fallback to OpenAI embeddings
                    openai_api_key = os.getenv("OPENAI_API_KEY")
                    if openai_api_key:
                        st.session_state.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
                    else:
                        st.error("Neither Ollama nor OpenAI embeddings are available. Please install Ollama or set OPENAI_API_KEY in your .env file.")
                        st.stop()
            st.session_state.loader = PyPDFDirectoryLoader(research_papers_path)
            
            with st.spinner("Loading PDF documents..."):
                st.session_state.docs = st.session_state.loader.load()
                
            if not st.session_state.docs:
                st.error("No content could be extracted from the PDF files.")
                st.stop()
                
            st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs[:50])
            st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)
            
        except ImportError as e:
            st.error("Missing required packages for PDF processing. Please install: pypdf, pdf2image")
            st.stop()
        except Exception as e:
            st.error(f"An error occurred while processing documents: {str(e)}")
            st.stop()
         
         
st.title("Research Paper Query Assistant")

if st.button("Initialize Document Embedding"):
    create_vector_embeddings()
    st.success("Vector database is ready!")

user_query = st.text_input("Enter your query about the research paper:", key="user_query")

if st.button("Submit Query") and user_query:
    if "vectors" not in st.session_state:
        st.error("Please initialize document embedding first!")
    else:
        try:
            document_chain = create_stuff_documents_chain(llm, prompt)
            retriever = st.session_state.vectors.as_retriever()
            retrieval_chain = create_retrieval_chain(retriever, document_chain)
            
            with st.spinner("Processing your query..."):
                start = time.process_time()
                response = retrieval_chain.invoke({'input': user_query})
                process_time = time.process_time() - start
                
                st.write("### Answer:")
                st.write(response['answer'])  # Changed from 'write' to 'answer'
                st.info(f"Response time: {process_time:.2f} seconds")
            
            with st.expander("Related Document Sections"):
                for i, doc in enumerate(response['context']):
                    st.markdown(f"**Excerpt {i+1}:**")
                    st.write(doc.page_content)
                    st.divider()
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")