from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from nasaplooza.scrapper.paperscraper import *
from nasaplooza.schemas.BodyInput import *
from nasaplooza.schemas.ResponseBody import *
from nasaplooza.utils.io_utils import *
from nasaplooza.scrapper.webscrapper import extract_text_from_web
from nasaplooza.nlp.ner import get_ner_html
from nasaplooza.nlp.llm import *


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check():
    return {"message": "health check pass"}


@app.post("/scrape")
async def scrape_from_internet(data: ScrapeBody):
    if data.source == "scholar":
        print("scrapping from scholar")
        df, author_profiles, related_searches = scrape_paper_info(data.query)
        df = json.loads(df.to_json(orient="records"))
    elif data.source == "pubmed":
        print("scrapping from pubmed")
        df, _, _ = scrape_pubmed_paper_info(data.query)
        df = json.loads(df.to_json(orient="records"))
        author_profiles = []
        related_searches = []
    else:
        print("scrapping from arxiv")
        df = scrape_arxiv(data.query)
        df = json.loads(df.to_json(orient="records"))
        author_profiles = []
        related_searches = []
    return {"paper": df, "author": author_profiles, "related_search": related_searches}


@app.post("/get-title")
async def get_paper_title_and_abstract(data: TitleBody):
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
    response = get_doc_qna_answer(data)
    return response


@app.post("/paperqna")
async def paper_qna(data: PaperQnABody):
    response = get_paper_qna_answer(data)
    response = response.replace("\n", "")
    return response


@app.post("/paperanalysis")
async def get_paper_keyquestions(data: PaperContentBody):
    analysis = perform_analysis_on_paper(data)
    similar = get_similarity_between_paper_and_query(data)
    literature = ask_llm_to_write_literature_survey(data)
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
    response = get_trend_of_title(data.query)
    prompt = f"Write me a 5 line paragraph about {data.query} "
    response["reason"] = get_openai_response(prompt)
    return response


@app.post("/mindmap")
async def get_mindmap_relavant_data(data: WebSearchBody):
    response = get_map_by_title(data.query)
    return response
