import streamlit as st
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.document_loaders import PyPDFLoader
import os

from dotenv import load_dotenv
load_dotenv()

## fetching in the environment variables
os.environ["HF_TOKEN"]= os.getenv("HF_TOKEN")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

## setting the streamlit app
st.title("Document Q&A chatbot with message history")
st.write("Upload PDF and chart with the content ")

## input for the api key 
api_key = st.text_input("Enter your Groq API Key: ", type="password")

## check the api key
if api_key:
    llm = ChatGroq(groq_api_key=api_key, model="Gemma2-9b-It")
    
    ## chat interface 
    session_id = st.text_input("session_id", value = "default_session")
    ## Manage chat history
    if 'store' not in st.session_state:
        st.session_state.store ={}
    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
    
    ## process the uploaded files
    if uploaded_files:
        documents = []
        for uploaded_file in uploaded_files:
            temp_file = f"./temp.pdf"
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getvalue())
                f_name= uploaded_file.name
            loader = PyPDFLoader(file_path=temp_file)
            docs=  loader.load()
            documents.extend(docs)
            
        ## split and create the embeddings 
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
        split_docs = text_splitter.split_documents(documents)  
        
        # Create FAISS vector store (more compatible than Chroma)
        vector_store = FAISS.from_documents(
            documents=split_docs, 
            embedding=embeddings
        )
        retriever = vector_store.as_retriever()
        
        ## contextualize the chat history
        contextual_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        contextual_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextual_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        history_aware_retriever = create_history_aware_retriever(llm,retriever, contextual_q_prompt)
        ## Answer question prompt 
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "\n\n"
            "{context}"
        )
        q_a_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        question_answer_chain = create_stuff_documents_chain(llm,q_a_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        def get_session_history(session_id: str) -> BaseChatMessageHistory:
            """Retrieve the chat history for a given session."""
            if session_id not in st.session_state.store:
                st.session_state.store[session_id] = ChatMessageHistory()
            return st.session_state.store[session_id]
        
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )
        user_input = st.text_input("Ask a question about the document:")
        if user_input:
            response = conversational_rag_chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}}
            )
            st.write("Assistant:", response['answer'])
            
            # Display chat history
            session_history = get_session_history(session_id)
            if st.checkbox("Show Chat History"):
                st.write("Chat History:")
                for message in session_history.messages:
                    if hasattr(message, 'type'):
                        st.write(f"**{message.type.capitalize()}:** {message.content}")
                    else:
                        st.write(f"**Message:** {message.content}")

else:

    st.warning("Please enter a valid API key.")
