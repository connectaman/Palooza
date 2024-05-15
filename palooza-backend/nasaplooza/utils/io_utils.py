import os
import traceback
from pypdf import PdfReader
from nasaplooza.nlp.llm import count_tokens, LLM
from nasaplooza.schemas.BodyInput import PaperContentBody


def get_paper_qna_answer(llm: LLM, data: PaperContentBody) -> str:
    if count_tokens(data.content) > 16000:
        data.content = data.content[:15000]
    prompt = (
        " PAPER CONTENT : "
        + data.content
        + f" Answer the Question: {data.query} based on the above PAPER CONTENT"
    )
    response = llm.invoke(prompt).content
    return response


def get_local_paper_title_abstract_author(
    llm: LLM, data: PaperContentBody
) -> dict[str, str | None]:
    try:
        reader = PdfReader(os.path.join("nasaplooza", "data", "pdf", data.filename))
        # meta = reader.metadata
        paperText = ""
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            paperText += page.extract_text()
            if i == 3:
                break
        prompt = paperText + "\n\n List down the Title, Authors name and Abstract"
        str_text = llm.invoke(prompt).content
        print(str_text)
        title_idx, authors_idx, abstract_idx = (
            str_text.find("Title:"),
            str_text.find("Authors:"),
            str_text.find("Abstract:"),
        )
        print(title_idx, authors_idx, abstract_idx)
        if authors_idx > 0:
            authors_idx = str_text.find("Authors:")
            title = (
                str_text[title_idx:authors_idx].replace("\n", "").replace("Title:", "")
            )
            authors = (
                str_text[authors_idx:abstract_idx]
                .replace("\n", "")
                .replace("Authors:", "")
            )
            abstract = (
                str_text[abstract_idx:].replace("\n", "").replace("Abstract:", "")
            )
            return {"title": title, "authors": authors, "abstract": abstract}
    except Exception:
        print(traceback.format_exc())
        return {"title": None, "authors": None, "abstract": None}


def perform_analysis_on_paper(llm: LLM, data: PaperContentBody) -> str:
    if count_tokens(data.content) > 16000:
        data.content = data.content[:14000]
    prompt = f"""From the below Paper Content : \n {data.content} \n Answer the following questions \n 
    1. Summarize the paper \n 
    2. Summarize the conclusion \n 
    3. Summarize The Introduction \n 
    4. Summarize The Proposed Method / Implementation \n 
    5. Summarize The Result \n 
    6. What is the Dataset Used \n 
    7. Does the abstract clearly describe the paper objectives? \n 
    8. Does the abstract correspond to the info presented in the research paper? \n 
    9. Does the abstract contain any information that is not investigated in the paper? \n 
    10. Does the author present the reasons for conducting the study? \n 
    11. Does the introduction include background information?
    12. Is there a clear thesis statement in the introduction?
    13. Are the methods presented clearly enough?
    14. Were the standard or modified methods used?
    15. If modified, were the changes explained effectively?
    16. Did the author indicate the limitations and the problems that arose while using the chosen methods?
    17. Are the findings adequate and logical?
    18. Is the data presented precisely?
    19. If there are any tables or diagrams, are they easily-understandable?
    20. Are the results helpful for the understanding of the topic?
    21. Did the author meet the objectives?
    22. If the author did not meet the objectives, do they provide any explanation for that?
    23. Do the findings interpreted adequately?
    24. Is the author biased?
    25. Does the author discuss the percent of errors that might occur while conducting the research?
    26. Are all of the outside sources cited?
    27. Does the author cite their own work in the research paper?
    28. Do the reference list and in-text citations correspond to the chosen formatting style?
    """
    response = llm.invoke(prompt).content
    model_response = {
        "Summarize the paper": response[response.find("1.") + 2 : response.find("2.")],
        "Summarize the conclusion": response[
            response.find("2.") + 2 : response.find("3.")
        ],
        "Summarize The Introduction": response[
            response.find("3.") + 2 : response.find("4.")
        ],
        "Summarize The Proposed Method / Implementation": response[
            response.find("4.") + 2 : response.find("5.")
        ],
        "Summarize The Result": response[response.find("5.") + 2 : response.find("6.")],
        "What is the Dataset Used": response[
            response.find("6.") + 2 : response.find("7.")
        ]
        + " \n ",  # + get_links(response[response.find("6.")+2:response.find("7.")]) ,
        "Does the abstract clearly describe the paper objectives": response[
            response.find("7.") + 2 : response.find("8.")
        ],
        "Does the abstract correspond to the info presented in the research paper": response[
            response.find("8.") + 2 : response.find("9.")
        ],
        "Does the abstract contain any information that is not investigated in the paper": response[
            response.find("9.") + 2 : response.find("10.")
        ],
        "Does the author present the reasons for conducting the study": response[
            response.find("10.") + 2 : response.find("11.")
        ],
        "Does the introduction include background information": response[
            response.find("11.") + 2 : response.find("12.")
        ],
        "Is there a clear thesis statement in the introduction": response[
            response.find("12.") + 2 : response.find("13.")
        ],
        "Are the methods presented clearly enough": response[
            response.find("13.") + 2 : response.find("14.")
        ],
        "Were the standard or modified methods used": response[
            response.find("14.") + 2 : response.find("15.")
        ],
        "If modified, were the changes explained effectively": response[
            response.find("15.") + 2 : response.find("16.")
        ],
        "Did the author indicate the limitations and the problems that arose while using the chosen methods": response[
            response.find("16.") + 2 : response.find("17.")
        ],
        "Are the findings adequate and logical": response[
            response.find("17.") + 2 : response.find("18.")
        ],
        "Is the data presented precisely": response[
            response.find("18.") + 2 : response.find("19.")
        ],
        "If there are any tables or diagrams, are they easily-understandable": response[
            response.find("19.") + 2 : response.find("20.")
        ],
        "Are the results helpful for the understanding of the topic": response[
            response.find("20.") + 2 : response.find("21.")
        ],
        "Did the author meet the objectives": response[
            response.find("21.") + 2 : response.find("22.")
        ],
        "If the author did not meet the objectives, do they provide any explanation for that": response[
            response.find("22.") + 2 : response.find("23.")
        ],
        "Do the findings interpreted adequately": response[
            response.find("23.") + 2 : response.find("24.")
        ],
        "Is the author biased": response[
            response.find("24.") + 2 : response.find("25.")
        ],
        "Does the author discuss the percent of errors that might occur while conducting the research": response[
            response.find("25.") + 2 : response.find("26.")
        ],
        "Are all of the outside sources cited": response[
            response.find("26.") + 2 : response.find("27.")
        ],
        "Does the author cite their own work in the research paper": response[
            response.find("27.") + 2 : response.find("28.")
        ],
        "Do the reference list and in-text citations correspond to the chosen formatting style": response[
            response.find("28.") + 2 :
        ],
    }
    return model_response


def get_similarity_between_paper_and_query(llm: LLM, data: PaperContentBody) -> str:
    if count_tokens(data.content) > 16000:
        data.content = data.content[:15000]
    prompt = f""" Content: {data.content} \n Question : {data.query} \n State Reason if Content and the Question is Similar or Dis-similar? """
    response = llm.invoke(prompt).content
    return response


def ask_llm_to_write_literature_survey(llm: LLM, data: PaperContentBody) -> str:
    prompt = "Generate a comprehensive literature review for a research paper and cite its sources  \n Paper Content:  "
    response = llm.invoke(prompt + data.content).content
    return response


def chat(llm: LLM, data: PaperContentBody) -> str:
    prompt = "Your name is Nasaplooza, a respectful and friendly chatbot to assist users in research questions and writing research thesis and report. \n "
    response = llm.invoke(prompt + data.query).content
    return response
