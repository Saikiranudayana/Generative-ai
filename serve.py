from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers  import StrOutputParser
from langchain_groq import ChatGroq
import os 
from langserve import add_routes
from dotenv import load_dotenv 
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
model = ChatGroq(model="Gemma2-9b-It",groq_api_key=groq_api_key)
##parser for getting the required output after fet response from llms
parser = StrOutputParser()
## create template
temp = "Translate the following into {language}"
##prompt
prompt = ChatPromptTemplate(
    [("system",temp),("user","{text}")]
    
)
## creating a chain for the model
chain = prompt|model|parser



app = FastAPI(title="langchain server",
              version= "1.0",
              description="A simple application for practising the functioning of langchain"
              )
add_routes(
    app,
    chain,
    path = "/chain"
    
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="localhost",port =8000)
    