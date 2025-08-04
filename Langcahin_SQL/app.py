import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os


st.set_page_config(page_title="SQL Agent with Groq", page_icon="🦜", layout="wide")
st.title("🦜SQL Agent with Groq")

LOCALDB="USE_LOCAL_DB"
MYSQL = "USE_MYSQL"

## creating some radio options 
rad_OPTIONS  = ["use SQLLITE3 students.db", "connect to your sql database"]

selected_option = st.sidebar.radio(label="Select which option you want to use:", options =rad_OPTIONS)

if rad_OPTIONS.index(selected_option) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide your MySQL host")
    mysql_user = st.sidebar.text_input("Provide your MySQL user")
    mysql_password = st.sidebar.text_input("Provide your MySQL password", type="password")
    mysql_db = st.sidebar.text_input("Provide your MySQL database name")
else:
    db_uri = LOCALDB

api_key= st.sidebar.text_input(label="Enter your Groq API Key", type="password")

if not db_uri:
    st.error("Please select a database option.")
if not api_key:
    st.error("Please provide your Groq API Key.")
    st.stop()
    
##LLM model 
llm = ChatGroq(groq_api_key=api_key, model="Llama3-8b-8192", streaming=True)

def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == LOCALDB:
        # Connect to SQLite database
        dbfile_path = (Path(__file__).parent / "students.db").absolute()   
        print(f"Database path: {dbfile_path}")
        # Use a direct connection string instead of lambda
        return SQLDatabase.from_uri(f"sqlite:///{dbfile_path}")
    elif db_uri == MYSQL:
        if not mysql_host or not mysql_user or not mysql_password or not mysql_db:
            st.error("Please provide all MySQL connection details.")
            st.stop()
        return SQLDatabase.from_uri(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}")
    
if db_uri == MYSQL:
    db = configure_db(db_uri, mysql_host=mysql_host, mysql_user=mysql_user, mysql_password=mysql_password, mysql_db=mysql_db)
else:
    db = configure_db(db_uri)

## Create SQL toolkit and agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

## Streamlit UI
st.subheader("Ask questions about your database")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What would you like to know about the database?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        try:
            response = agent.run(prompt, callbacks=[st_callback])
            st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})

# Add some helpful information
with st.sidebar:
    st.markdown("---")
    st.subheader("💡 Example Questions")
    st.markdown("""
    - How many records are in each table?
    - What are the column names in the students table?
    - Show me the first 5 rows of data
    - What is the average age of students?
    - How many students are there per grade?
    """)
    
    if st.button("Show Database Schema"):
        try:
            schema_info = db.get_table_info()
            st.text_area("Database Schema:", value=schema_info, height=200)
        except Exception as e:
            st.error(f"Error getting schema: {str(e)}")