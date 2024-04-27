from langchain.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper
import logging
from langchain_community.document_loaders import UnstructuredURLLoader
import re
import string
from functools import lru_cache


logging.basicConfig(
    format="%(asctime)s | %(levelname)s: %(message)s", level=logging.INFO
)
search = GoogleSearchAPIWrapper()


@lru_cache
def top5_results(query):
    return search.results(query, 5)


tool = Tool(
    name="Google Search Snippets",
    description="Search Google for recent results.",
    func=top5_results,
)


@lru_cache
def get_links(raw_command):
    sources = tool.run(raw_command)
    if len(sources) == 0:
        return " "
    try:
        prompt = ""
        for i, res in enumerate(sources):
            prompt += f""" Source [{i+1}] {res["link"]} \n {res["snippet"]}"""
        return prompt
    except:
        return " "


def clean_source_text(text):
    """
    clean_source_text(): Clean the text from a source

    Parameters
        text (str): The text to be cleaned.

    Returns
        cleaned_text (str): The cleaned text
    """
    # Remove newlines and replace multiple spaces with a single space
    cleaned_text = re.sub(r"\n", " ", text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)
    # Remove leading/trailing whitespaces
    cleaned_text = cleaned_text.strip()
    # Remove special characters and convert to lowercase
    cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text.lower())
    # Remove special characters
    printable = set(string.printable)
    cleaned_text = "".join(filter(lambda x: x in printable, cleaned_text))
    # Remove unparseable characters
    cleaned_text = cleaned_text.encode("unicode_escape").decode("utf-8")
    cleaned_text = re.sub(r"\\[a-z]{3}", "", cleaned_text)
    cleaned_text = cleaned_text.replace("\\", "")

    return cleaned_text


@lru_cache
def extract_text_from_web(url):
    print("Scrapping url ", url)
    if url:
        loader = UnstructuredURLLoader([url], verify_ssl=False)
        docs = loader.load()
        content = " ".join([doc.page_content for doc in docs])
        content = clean_source_text(content)
        return content
    return "NA"
