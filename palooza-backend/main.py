import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

from nasaplooza.scrapper.paperscraper import (
    scrape_paper_info,
    scrape_pubmed_paper_info,
    scrape_arxiv,
    get_trend_of_title,
    get_map_by_title,
)
from nasaplooza.schemas.BodyInput import (
    ScrapeBody,
    TitleBody,
    ExtractWebBody,
    DocumentQnABody,
    PaperQnABody,
    DatasetBody,
    DatasetAnalysisBody,
    TrendBody,
    WebSearchBody,
    PaperContentBody,
)
from nasaplooza.utils.io_utils import (
    get_local_paper_title_abstract_author,
    get_paper_qna_answer,
    get_similarity_between_paper_and_query,
    perform_analysis_on_paper,
    ask_llm_to_write_literature_survey,
)
from nasaplooza.utils.log import logger
from nasaplooza.scrapper.webscrapper import extract_text_from_web
from nasaplooza.nlp.ner import get_ner_html
from nasaplooza.nlp.llm import (
    create_llm,
    ask_dataset,
    get_doc_qna_answer,
    pandas_analysis,
)

load_dotenv()


app = FastAPI()

logger.info("FastAPI server started")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


provider = os.getenv("LLM_PROVIDER", "openai")
model = os.getenv("LLM_MODEL", "")
llm = create_llm(provider, model)


@app.get("/")
async def health_check():
    logger.debug("health check pass")
    return {"message": "health check pass"}


@app.post("/scrape")
async def scrape_from_internet(data: ScrapeBody):
    if data.source == "scholar":
        logger.debug("scraping from scholar")
        df, author_profiles, related_searches = scrape_paper_info(data.query)
        df = json.loads(df.to_json(orient="records"))
    elif data.source == "pubmed":
        logger.debug("scraping from pubmed")
        df, _, _ = scrape_pubmed_paper_info(data.query)
        df = json.loads(df.to_json(orient="records"))
        author_profiles = []
        related_searches = []
    else:
        logger.debug("scraping from arxiv")
        df = scrape_arxiv(data.query)
        logger.debug("scraped from arxiv")
        df = json.loads(df.to_json(orient="records"))
        author_profiles = []
        related_searches = []
    return {"paper": df, "author": author_profiles, "related_search": related_searches}


@app.post("/get-title")
async def get_paper_title_and_abstract(data: TitleBody):
    logger.debug("getting paper title, abstract, author")
    response = get_local_paper_title_abstract_author(data)
    return response


@app.post("/extract")
async def extract_content_from_url(data: ExtractWebBody):
    response = extract_text_from_web(data.url)
    return response


@app.post("/ner")
async def get_ner_from_content(data: PaperContentBody):
    response = get_ner_html(data.content)
    return response


@app.post("/docqna")
async def document_qna(data: DocumentQnABody):
    response = get_doc_qna_answer(llm, data)
    return response


@app.post("/paperqna")
async def paper_qna(data: PaperQnABody):
    response = get_paper_qna_answer(llm, data)
    response = response.replace("\n", "")
    return response


@app.post("/paperanalysis")
async def get_paper_keyquestions(data: PaperContentBody):
    analysis = perform_analysis_on_paper(llm, data)
    similar = get_similarity_between_paper_and_query(llm, data)
    literature = ask_llm_to_write_literature_survey(llm, data)
    similar = similar.replace("\n", "")
    literature = literature.replace("\n", "")
    response = {"analysis": analysis, "similar": similar, "literature": literature}
    return response


@app.post("/dataset-qna")
async def talk_to_data(data: DatasetBody):
    response = ask_dataset(data.dataset, data.query)
    response = response.replace("\n", "")
    return response


@app.post("/dataset-analysis")
async def get_dataset_analysis(data: DatasetAnalysisBody):
    response = pandas_analysis(data.dataset)
    return response


@app.post("/get-trend")
async def get_trend_of_topic(data: TrendBody):
    logger.debug("getting trend of topic %s" % data.query)
    response = get_trend_of_title(data.query)
    logger.debug("received response from get_trend_of_title: %s", response)
    prompt = f"Write me a 5 line paragraph about {data.query} "
    logger.debug("getting summary of trend of topic")
    response["reason"] = llm.invoke(prompt).content
    logger.debug("received response from llm: %s", response["reason"])
    return response


@app.post("/mindmap")
async def get_mindmap_relavant_data(data: WebSearchBody):
    response = get_map_by_title(data.query)
    return response
