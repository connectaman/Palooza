import tiktoken
from openai import OpenAI

encoding = tiktoken.get_encoding("cl100k_base")
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
import pandas as pd
import os
import requests
from ydata_profiling import ProfileReport
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings

api_key = os.getenv("OPENAI_API_KEY", "")
client = OpenAI(api_key=api_key)


def count_tokens(text):
    return len(encoding.encode(text))


def get_doc_qna_answer(data):
    try:
        loader = PyPDFLoader("nasaplooza/data/pdf/" + str(data.filename))
        pages = loader.load_and_split()
        faiss_index = FAISS.from_documents(
            pages, OpenAIEmbeddings(openai_api_key=api_key)
        )
        docs = faiss_index.similarity_search(data.query, k=2)
        prompt = "Use the Below Sources to Answer the following question : "
        for doc in docs:
            prompt += (
                "Source Page Number "
                + str(doc.metadata["page"])
                + " : "
                + doc.page_content
                + "  \n \n "
            )
        response = get_openai_response(prompt)
        return response
    except Exception as e:
        print(e)
    return "Sorry! could not find answer."


def get_openai_response(prompt, temperature=0):
    if count_tokens(prompt) >= 8000:
        prompt = prompt[:7000]
    response = client.chat.completions.create(
        model="gpt-4",
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["choices"][0]["message"]["content"]


def ask_dataset(dataset, query):
    df = pd.read_csv("nasaplooza/data/dataset/space_corrected.csv")
    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model="gpt-4", openai_api_key=api_key),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )
    response = agent.run(query)
    return response


def pandas_analysis(dataset):
    df = pd.read_csv("nasaplooza/data/dataset/space_corrected.csv")
    profile = ProfileReport(df, title="Dataset Analysis Report", minimal=True)
    text = profile.to_html()
    return text


def get_all_img_url(url):
    response = requests.get(url)
    html_content = response.content
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    # Find all img tags and extract their src attributes
    img_tags = soup.find_all("img")
    img_urls = [img.get("src") for img in img_tags]
    return img_urls
