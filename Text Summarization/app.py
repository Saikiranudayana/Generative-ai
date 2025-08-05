import validators
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader,UnstructuredURLLoader



##streamlit app
st.set_page_config(page_title="Langchain: Summarize text from YT or website", page_icon="📄", layout="wide")
st.title("Langchain: Summarize text from YT or website")
st.subheader("Summarize URL")

## GET the GROP API key and the Url 

with st.sidebar:
    groq_api_key = st.text_input("Enter your Groq API Key", type="password")
    
    st.markdown("---")
    st.markdown("### 💡 Tips:")
    st.markdown("""
    - **YouTube URLs work best** (high success rate)
    - Some websites may block automated requests
    - Try news articles, blogs, or public content
    """)
    
    st.markdown("### 📝 Example URLs:")
    st.markdown("""
    **YouTube:**
    - `https://www.youtube.com/watch?v=VIDEO_ID`
    
    **Websites that usually work:**
    - BBC News articles
    - Wikipedia pages
    - Medium articles
    - Public blog posts
    """)

genric_url = st.text_input("URL",label_visibility="collapsed")

prompt_template = """Summarize the content of the URL in 300 words:
context: {text}"""

prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

if st.button("Summarize the content"):
    ## Validate all the inputs
    if not groq_api_key.strip() or not genric_url.strip():
        st.error("Please provide the required information.")
    elif not validators.url(genric_url):
        st.error("Please enter a valid URL.IT can be a youtube video or a website.")
        
    else:
        try:
            with st.spinner("Loading..."):
                ## Initialize the LLM after validation
                llm = ChatGroq(groq_api_key=groq_api_key, model="Llama3-8b-8192")
                
                ## loading the website data 
                if "youtube.com" in genric_url or "youtu.be" in genric_url:
                    loader = YoutubeLoader.from_youtube_url(genric_url, add_video_info=True)
                else:
                    # Enhanced headers for better website compatibility
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1"
                    }
                    loader = UnstructuredURLLoader(
                        urls=[genric_url],
                        ssl_verify=False,
                        headers=headers
                    )
                docs = loader.load()
                
                if not docs:
                    st.error("No content could be extracted from the URL. Please check if the URL is accessible.")
                    st.stop()
                
                ## chain For summarization 
                chain = load_summarize_chain(
                    llm=llm,
                    chain_type="stuff",
                    prompt=prompt,
                    verbose=False  # Set to False to reduce console output
                )
                output_summary = chain.run(docs)

                st.success("Summary generated successfully!")
                st.write("### Summary:")
                st.write(output_summary)
                
        except Exception as e:
            error_msg = str(e)
            if "400" in error_msg or "Bad Request" in error_msg:
                st.error("❌ **HTTP 400 Error**: The website is blocking our request. This can happen when:")
                st.info("""
                - The website has anti-bot protection
                - The URL requires authentication
                - The website blocks automated requests
                
                **💡 Suggestions:**
                - Try a different website URL
                - Use YouTube URLs (they work well!)
                - Check if the URL is publicly accessible
                """)
            elif "403" in error_msg or "Forbidden" in error_msg:
                st.error("❌ **Access Forbidden**: The website doesn't allow automated access.")
            elif "404" in error_msg or "Not Found" in error_msg:
                st.error("❌ **Page Not Found**: Please check if the URL is correct.")
            else:
                st.error(f"❌ **An error occurred**: {error_msg}")
            
            # Don't stop the app, let user try again
    
        
        
        