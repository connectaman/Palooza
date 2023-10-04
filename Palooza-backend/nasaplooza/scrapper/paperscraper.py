import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep
import requests
import urllib
import traceback
from functools import lru_cache
from serpapi import GoogleSearch
import plotly.express as px
import plotly
import base64
import os
import json
import os
import pandas as pd
import json
import re
from serpapi import GoogleSearch
import pandas as pd
import plotly.express as px
import plotly
import base64
from pymed import PubMed
import pandas as pd

pubmed = PubMed(tool="Searcher", email="my@email.address")

headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

SERP_API_KEY = os.getenv("SERP_API_KEY","7e20f70d67b2b3a8932bce896123ef1612cefe63436dbc12ae21acd77d4cd6af")

def scrape_paper_info(paper_name):
    params = {
        "engine": "google_scholar",
        "q": paper_name,
        "api_key": SERP_API_KEY
    }
    year_pattern = r'\b\d{4}\b'
    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results.get("organic_results", [])
    if results.get("search_metadata", {}).get("status") == "Success":
        paper_info = {
            "Paper Title": [],
            "Paper Abstract": [],
            "Year": [],
            "Author": [],
            "Citation": [],
            "Publication": [],
            "Url of paper": [],
        }
        try:
            related_searches = [rs.get("query", None) for rs in results.get(
                "related_searches", [])]
        except Exception as e:
            print("related searches", e)
            related_searches = []
        author_ids = []
        for result in organic_results:
            title = result.get("title", "")
            authors = ", ".join([each_author.get("name")
                                 for each_author in result.get("publication_info").get("authors", [])])
            abstract = result.get("snippet", "").strip()
            link = result.get("link", "")
            year_matches = re.findall(year_pattern, result.get(
                "publication_info", {}).get("summary", ""))
            year = year_matches[0] if len(year_matches) > 0 else None
            paper_citations = result.get("inline_links", {}).get(
                "cited_by", {}).get("total", None)
            publication = result.get("publication_info", {}).get(
                "summary", "").split("-")[-1]
            paper_info['Paper Title'].append(title)
            paper_info['Author'].append(authors)
            paper_info['Paper Abstract'].append(abstract)
            paper_info['Url of paper'].append(link)
            paper_info['Year'].append(year)
            paper_info['Citation'].append(paper_citations)
            paper_info['Publication'] = publication
            try:
                author_ids += [each_author.get("author_id")
                               for each_author in result.get("publication_info").get("authors", [])]
            except Exception as E:
                print(E)
                author_ids += []
        df = pd.DataFrame(paper_info)
        author_profiles = []
        for each_author_id in author_ids:
            params = {
                "engine": "google_scholar_author",
                "author_id": each_author_id,
                "api_key": SERP_API_KEY
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            author = results.get("author")
            for row in results.get("cited_by").get("table"):
                if "citations" in row:
                    author["citations"] = row.get("citations").get("all")
                if "h_index" in row:
                    author["h_index"] = row.get("h_index").get("all")
                if "i10_index" in row:
                    author["i10_index"] = row.get("i10_index").get("all")
            author["graph"] = convert_graph_to_base64(px.bar(pd.DataFrame(results.get("cited_by").get("graph")), x='year', y='citations')) 
            author_profiles.append(author)
        return df, author_profiles, related_searches

def convert_graph_to_base64(fig):
    png = plotly.io.to_image(fig)
    png_base64 = base64.b64encode(png).decode('ascii')
    return png_base64

def get_total_papers_from_gs(query):
  query = query.replace(" ","+")
  base_url = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={query}&oq="
  response = requests.get(base_url)
  if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    total = doc.find_all('div',{"class" : "gs_ab_mdw"}).text.strip()
    total = total.replace(",","")
    total = re.findall(r'\d+', total)
    return int(total[0])
  return 0

def get_total_papers_from_arxiv(query):
  query = query.replace(" ","+")
  base_url = f"https://link.springer.com/search?query={query}"
  response = requests.get(base_url)
  if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    total = doc.find_all('div',{"class" : "gs_ab_mdw"}).text.strip()
    total = total.replace(",","")
    total = re.findall(r'\d+', total)
    return int(total[0])
  return 0

def scrape_arxiv(query):
    # Create the URL for the arXiv search
    query = query.replace(" ","+")
    base_url = f"https://arxiv.org/search/?query={query}&searchtype=all&abstracts=show&size=200"
    response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract data from the search results
        titles = []
        authors = []
        abstracts = []
        links = []  
        years = []
        for result in soup.find_all('li', class_='arxiv-result'):
            title = result.find('p', class_='title is-5 mathjax')
            author = result.find('p', class_='authors').find('a',href=True)
            abstract = result.find('span', class_='abstract-full')
            link = result.find('p', class_='list-title').find('a',href=True)
            year = result.find('p', class_='is-size-7')
            # if title and author and abstract and link:
            titles.append(title.text.strip())
            authors.append(author.text.strip())
            abstracts.append(abstract.text.strip().replace("△ Less",""))
            links.append(link['href'].replace("/abs/","/pdf/"))
            years.append(year.text.strip()[-5:])

        # Create a DataFrame
        data = {'Paper Title': titles, 'Author': authors, 'Paper Abstract': abstracts, 'Url of paper': links,"Year":years}
        df = pd.DataFrame(data)
        df["Publication"] = "arxiv"
        df["Citation"] = "-"
        return df.head(10)
    else:
        print("Error: Unable to fetch data from arXiv")
        return None


# this function for the getting inforamtion of the web page
def get_paperinfo(paper_url):

  #download the page
  response=requests.get(paper_url,headers=headers)

  # check successful response
  if response.status_code != 200:
    print('Status code:', response.status_code)
    raise Exception('Failed to fetch web page ')

  #parse using beautiful soup
  paper_doc = BeautifulSoup(response.text,'html.parser')

  return paper_doc

# this function for the extracting information of the tags
def get_tags(doc):
  paper_tag = doc.select('[data-lid]')
  cite_tag = doc.find_all('div',{"class" : "gs_fl"})  #doc.select('[title=Cite] + a')
  link_tag = doc.find_all('div',{"class" : "gs_or_ggsm"})
  author_tag = doc.find_all("div", {"class": "gs_a"})
  abstract_tag = doc.find_all('div',{"class" : "gs_rs"})
  return paper_tag,cite_tag,link_tag,author_tag,abstract_tag


# it will return the title of the paper
def get_papertitle(paper_tag):
  
  paper_names = []
  
  for tag in paper_tag:
    paper_names.append(tag.select('h3')[0].get_text())

  return paper_names



# it will return the number of citation of the paper
def get_citecount(cite_tag):
  cite_count = []
  for i in cite_tag:
    cite = i.text
    res = re.findall(r"Cited by\s*(-?\d+(?:\.\d+)?)",cite)
    cite_count.extend(res)
  return cite_count

# function for the getting link information
def get_link(link_tag):

  links = []

  for i in range(len(link_tag)) :
    links.append(link_tag[i].a['href']) 
  return links 

# function for the getting autho , year and publication information
def get_author_year_publi_info(authors_tag):
  years = []
  publication = []
  authors = []
  for i in range(len(authors_tag)):
      authortag_text = (authors_tag[i].text).split()
      year = int(re.search(r'\d+', authors_tag[i].text).group())
      years.append(year)
      publication.append(authortag_text[-1])
      author = ",".join(authors_tag[i].text.split(",")[:-1])
      #author = authortag_text[0] + ' ' + re.sub(',','', authortag_text[1])
      authors.append(author)
  
  return years , publication, authors


def get_paperabstract(abstract_tag):
  
  abstracts = []
  
  for i in range(len(abstract_tag)):
      abstract_text = (abstract_tag[i].text).split()
      abstracts.append(" ".join(abstract_text))

  return abstracts



def get_top_publication_topics():
  url = "https://scholar.google.com/citations?view_op=top_venues"
  response = requests.get(url,headers=headers)
  if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
      # Extract data from the search results
    publication = []
    h5index = []
    for result in soup.find_all('tr'):
      title = result.find('td', class_='gsc_mvt_t')
      index = result.find('td', class_='gsc_mvt_n').find('a',class_="gs_ibl gsc_mp_anchor")
      publication.append(title.text.strip())
      h5index.append(index.text.strip())

def get_all_papers_from_scholar(query,start):
    final_df = pd.DataFrame()
    # creating final repository
    paper_repos_dict = {
                        'Paper Title' : [],
                        'Paper Abstract' : [],
                        'Year' : [],
                        'Author' : [],
                        'Citation' : [],
                        'Publication' : [],
                        'Url of paper' : [] }

    query = query.replace(" ","+").lower()
    # get url for the each page
    url = "https://scholar.google.com/scholar?start={}&q={}&hl=en&as_sdt=0,10".format(start,query)
    #url = "https://scholar.google.com/scholar?&q={}+&hl=en".format(query)

    # function for the get content of each page
    doc = get_paperinfo(url)

    # function for the collecting tags
    paper_tag,cite_tag,link_tag,author_tag,abstract_tag = get_tags(doc)

    #print("Citation tag",cite_tag)
    # paper title from each page
    papername = get_papertitle(paper_tag)

    paperabstract = get_paperabstract(abstract_tag)

    # year , author , publication of the paper
    year , publication , author = get_author_year_publi_info(author_tag)

    # cite count of the paper 
    cite = get_citecount(cite_tag)

    # url of the paper
    link = get_link(link_tag)

    final_df = pd.concat([final_df,pd.DataFrame(
        {
        "Paper Title":pd.Series(papername),
        "Paper Abstract":pd.Series(paperabstract),
        "Year":pd.Series(year),
        "Author":pd.Series(author),
        "Citation":pd.Series(cite),
        "Publication":pd.Series(publication),
        "Url of paper":pd.Series(link)
        })],ignore_index=True)
    return final_df

def get_author_details(url):
  URL = f"https://scholar.google.com"
  page = requests.get(URL+url)
  soup = BeautifulSoup(page.content, "html.parser")
  print(soup)
  name = soup.find_all("div",{"class":"gsc_prf_in"})
  print(name)

def get_authors_profiles(query):
  keyword = urllib.parse.quote(query)
  URL = f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={keyword}"
  page = requests.get(URL)
  soup = BeautifulSoup(page.content, "html.parser")
  results = soup.find_all('div',{"class" : "gs_a"})
  authors = []
  for res in results:
    for author in res.find_all("a", href=True):
      authors.append(str(author)[str(author).find("href=")+6:str(author).find('\">')])
  print(authors)

def convert_graph_to_base64(fig):
  png = plotly.io.to_image(fig)
  png_base64 = base64.b64encode(png).decode('ascii')
  return png_base64


def get_timeseries_graph(trend_data):
  data = []

  for d in trend_data:
     data.append({"months":d["date"],"total_queries":d["values"][0]["extracted_value"]})
  df = pd.DataFrame(data)
  fig = px.line(df, x='months', y="total_queries")
  png_base64 = convert_graph_to_base64(fig)
  return png_base64

def get_trend_of_title(query):
  response = {}
  params = {
  "engine": "google_trends",
  "q": query,
  "data_type": "TIMESERIES",
  "api_key":SERP_API_KEY
  }
  search = GoogleSearch(params)
  response["TIMESERIES"] = search.get_dict()["interest_over_time"]
  timeseries_base = get_timeseries_graph(response["TIMESERIES"]["timeline_data"])

  response = {
   "timeseries" : timeseries_base,
   "reason" : response["TIMESERIES"]
  }
  return response

  

def get_citations_by_author(author_id, saved_authors: list = [], cited_papers: list = [], depth: int = 3):
    params = {
        "api_key":SERP_API_KEY,
        "engine": "google_scholar_author",
        "hl": "en",
        "author_id": author_id
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    artricles = results.get("articles")
    i = 0
    paper_details = []
    for temp in range(1,20):
        try:
            first_author = artricles[i]["authors"].split(",")[0]
            # print(cited_papers)
            # print(first_author, saved_authors)
            if first_author not in saved_authors:
                paper_details.append(
                    {"title": artricles[i]["title"], "link": artricles[i]["link"], "authors": artricles[i]["authors"]})
                cited_papers.append(artricles[i]["title"])
                saved_authors.append(first_author)
            i += 1
        except Exception as e:
            # print("Failure in get_citations_by_author")
            # print(e)
            continue
        if len(paper_details) >= depth or i >= len(artricles):
            # print(i)
            break
    return paper_details, cited_papers, saved_authors


def get_authorid_by_paper(paper_name: str, first_author: bool = True, return_url: bool = False, return_details: bool = False):
    params = {
        "engine": "google_scholar",
        "q": f"source: {paper_name}",
        "hl": "en",
        "api_key": SERP_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results.get("organic_results")[0]
    if first_author:
        author_id = results.get("organic_results")[
            0]['publication_info']["authors"][0]["author_id"]
        author_name = results.get("organic_results")[
            0]['publication_info']["authors"][0]["name"]
    else:
        author_id = results.get("organic_results")[
            0]['publication_info']["authors"][-1]["author_id"]
        author_name = results.get("organic_results")[
            0]['publication_info']["authors"][-1]["name"]
    if return_details:
        # print(organic_results['publication_info']["authors"])
        return author_id, author_name, organic_results["link"], ", ".join([i["name"] for i in organic_results['publication_info']["authors"]])
    return author_id, author_name


def create_node(name, author, url):
    # Helper function to create a node in the desired format
    return {
        "name": name,
        "attributes": {
            "author": author,
            # "url": url
        },
        "children": []
    }


def get_map_by_title(title: str, tree_width: int = 3, tree_depth: int = 3):
    saved_authors = []
    cited_papers = [title]
    author_id, author_name, init_links, init_authors = get_authorid_by_paper(
        title, return_details=True)
    saved_authors.append(author_name)
    mind_map = create_node(title, author_name, init_links)
    child_citations_papers, cited_papers, saved_authors = get_citations_by_author(
        author_id, saved_authors, cited_papers, tree_depth)
    for idx, each_child in enumerate(child_citations_papers):
        author_id, author_name = get_authorid_by_paper(each_child["title"])
        saved_authors.append(author_name)
        child_node = create_node(
            each_child["title"], author_name, each_child["link"])
        mind_map["children"].append(child_node)
        grand_child_citations_papers, cited_papers, saved_authors = get_citations_by_author(
            author_id, saved_authors, cited_papers, tree_depth)
        for each_grand_child in grand_child_citations_papers:
            print(each_grand_child, "\n\n\n\n")
            child_node = create_node(each_grand_child["title"], each_grand_child["title"].split(
                ",")[0], each_grand_child["link"])
            mind_map["children"][idx]["children"].append(child_node)
    return mind_map


def scrape_pubmed_paper_info(query: str):
    results = pubmed.query(query, max_results=10)
    results = list(results)

    if len(results) > 0:
        paper_info = {
            "Paper Title": [],
            "Paper Abstract": [],
            "Year": [],
            "Author": [],
            "Citation": [],
            "Publication": [],
            "Url of paper": [],
        }
        print("in if")
        for article in results:
            try:
                paper_info["Paper Title"].append(article.title)
                paper_info["Paper Abstract"].append(article.abstract)
                paper_info["Year"].append(article.publication_date.year)
                authors = [i["firstname"] + i["lastname"]
                           for i in article.authors]
                paper_info["Author"].append(authors)
                paper_info["Citation"].append("--")
                paper_info["Publication"].append(article.journal)
                paper_info["Url of paper"].append(None)
            except Exception as e:
                print(e)
                continue
        df = pd.DataFrame(paper_info)
        return df, None, None