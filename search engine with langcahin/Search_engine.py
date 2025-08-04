import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.utilities import ArxivAPIWrapper,WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun,DuckDuckGoSearchRun 
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler
from dotenv import load_dotenv
import os 

## wikipedia api wrapper
api_wrapper_wiki = WikipediaAPIWrapper(top_k_results=1,content_length=1000)
wiki= WikipediaQueryRun(api_wrapper=api_wrapper_wiki)

## arxiv api wrapper
api_wrapper_arxiv = ArxivAPIWrapper(top_k_results=1,content_length=1000)
arxiv = ArxivQueryRun(api_wrapper=api_wrapper_arxiv)

search = DuckDuckGoSearchRun(name="search")

st.title("Search Engine with LangChain ")
""" IN this app, you can search for information using Wikipedia, Arxiv, and DuckDuckGo.i have also used streamlitcallback handler to stream the response from the LLM.
"""




## slider bar
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your Groq API Key", type="password") 

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role":"assistant",
            "content":"HI i am a chatbot, ican search throught the internet, How can i help you?"}
    ]
    
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])
    
if prompt:=st.chat_input(placeholder="What is Machine learning?"):
    st.session_state["messages"].append({"role":"user", "content":prompt})
    st.chat_message("user").write(prompt)
    llm= ChatGroq(
        groq_api_key=api_key,
        model_name="llama3-8b-8192",streaming=True)
    tools = [search, wiki, arxiv]
    
    
    search_agent = initialize_agent(tools=tools,llm=llm,agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,handle_parsing_errors=True)
    
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(),expand_new_thoughts=False)
        response= search_agent.run(prompt,callbacks=[st_cb])
        st.session_state.messages.append({"role":"assistant","content":response})
        st.write(response)
        