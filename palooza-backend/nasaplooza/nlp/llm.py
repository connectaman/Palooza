import os

from bs4 import BeautifulSoup
from langchain.agents.agent_types import AgentType
from langchain_anthropic import ChatAnthropic
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.language_models.llms import LLM
from langchain_core.embeddings.embeddings import Embeddings
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import (
    ChatOpenAI,
    AzureChatOpenAI,
    OpenAIEmbeddings,
    AzureOpenAIEmbeddings,
)
import pandas as pd
import requests
import tiktoken
from ydata_profiling import ProfileReport

from nasaplooza.schemas.BodyInput import DocumentQnABody

encoding = tiktoken.get_encoding("cl100k_base")
openai_api_key = os.getenv("LLM_API_KEY", "")


def create_llm(llm_provider: str, model: str, temperature: float = 0.0) -> LLM:
    if llm_provider == "anthropic":
        return ChatAnthropic(model=model, temperature=temperature)
    if llm_provider == "openai":
        return ChatOpenAI(model=model, temperature=temperature)
    if llm_provider == "azure":
        deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME", "")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        return AzureChatOpenAI(
            deployment_name=deployment_name,
            azure_endpoint=endpoint,
            model=model,
            temperature=temperature,
        )
    raise ValueError(f"Unknown LLM type: {llm_provider}")


def get_embeddings_model(llm_provider: str | None) -> Embeddings:
    if llm_provider is None:
        llm_provider = os.getenv("LLM_PROVIDER", "azure")
    if llm_provider == "openai":
        return OpenAIEmbeddings()
    if llm_provider == "azure":
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        if endpoint == "":
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set.")
        embeddings_model = os.getenv("AZURE_EMBEDDINGS_MODEL", "text-embedding-3-large")
        deployment = os.getenv("EMBEDDING_DEPLOYMENT_NAME", "")
        if deployment == "":
            raise ValueError(
                "EMBEDDING_DEPLOYMENT_NAME environment variable is not set."
            )
        return AzureOpenAIEmbeddings(
            azure_endpoint=endpoint,
            model=embeddings_model,
            deployment=deployment,
        )
    raise ValueError(f"Unknown LLM type: {llm_provider}")


def count_tokens(text: str) -> int:
    return len(encoding.encode(text))


def cut_text(text: str, max_tokens: int) -> str:
    tokens = encoding.encode(text)
    return encoding.decode(tokens[:max_tokens])


def get_doc_qna_answer(llm: LLM, data: DocumentQnABody) -> str:
    try:
        loader = PyPDFLoader("nasaplooza/data/pdf/" + str(data.filename))
        pages = loader.load_and_split()
        faiss_index = FAISS.from_documents(pages, get_embeddings_model())
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
        response = llm.invoke(prompt).content
        return response
    except Exception as e:
        print(e)
    return "Sorry! could not find answer."


def ask_dataset(dataset: str, llm: LLM, query: str) -> str:
    df = pd.read_csv("nasaplooza/data/dataset/space_corrected.csv")
    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model="gpt-4", openai_api_key=openai_api_key),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )
    response = agent.run(query)
    return response


def pandas_analysis(dataset: str) -> str:
    df = pd.read_csv("nasaplooza/data/dataset/space_corrected.csv")
    profile = ProfileReport(df, title="Dataset Analysis Report", minimal=True)
    text = profile.to_html()
    return text


def get_all_img_url(url: str) -> list[str]:
    response = requests.get(url)
    html_content = response.content
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    # Find all img tags and extract their src attributes
    img_tags = soup.find_all("img")
    img_urls = [img.get("src") for img in img_tags]
    return img_urls
