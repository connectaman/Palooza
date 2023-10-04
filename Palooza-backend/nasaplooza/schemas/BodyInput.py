from pydantic import BaseModel
from typing import Optional

class ScrapeBody(BaseModel):
    query : str
    source : str = "scholar"

class WebSearchBody(BaseModel):
    query : str

class ExtractWebBody(BaseModel):
    url : str

class PaperContentBody(BaseModel):
    content : str
    query : Optional[str] = ""

class DocumentQnABody(BaseModel):
    query : str
    filename : str

class PaperQnABody(BaseModel):
    content : str
    query : str

class ChatBody(BaseModel):
    query : str

class DatasetBody(BaseModel):
    query : str
    dataset : str
    
class DatasetAnalysisBody(BaseModel):
    dataset : str

class TitleBody(BaseModel):
    filename : str

class TrendBody(BaseModel):
    query : str

class DownloadPaperBody(BaseModel):
    content : str
    query : str
    # title : str
    # author : str
    # abstract : str
    
