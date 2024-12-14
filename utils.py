import streamlit as st
import pandas as pd
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import json
from sqlalchemy import create_engine
import fitz

with open("keys/db.json", 'r') as file:
    data = json.load(file)

def extract_text_from_pdf(pdf_file, page_start: int, page_end:int):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    i = page_start
    while i <= page_end:
        #print(f"Page {i}")
        page = doc.load_page(i)
        text += page.get_text('text')
        i += 1
    return text


def translate(openai_api_key, text_to_translate):
    response_schemas = [
        ResponseSchema(name="date", description="Transaction date in format MM/DD/YYYY"),
        ResponseSchema(name="month billed", description="Month of transaction date in English"),
        ResponseSchema(name="transaction", description="The transaction description"),
        ResponseSchema(name="charges", description="Amount of the transaction", optional=True),
        ResponseSchema(name="credits", description="Amount of the transaction", optional=True),
        ResponseSchema(name="bus./pers.", description="Category")
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

    prompt_template = """
        Extract transactions in JSON format with the following fields: "date", "month", "transaction", "charges", "credits".
        Exclude non-transactional data like summaries or balance information.

        Bank Statement:
        {text}

        Extracted Transactions:
        """
    transaction_prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["text"],
        output_parser=output_parser
    )

    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        max_tokens=4096,
        openai_api_key=openai_api_key
    )

    transaction_chain = LLMChain(
        llm=llm,
        prompt=transaction_prompt
    )

    all_predictions = []
    prediction = transaction_chain.predict(text=text_to_translate)
    try:
        parsed_transactions = json.loads(prediction)
        if isinstance(parsed_transactions, list):
            all_predictions.extend(parsed_transactions)
    except json.JSONDecodeError:
        pass
    #print(parsed_transactions[0:100])
    return all_predictions


def get_engine(database: str):
    user = data["user"]
    password = data["password"]
    host = data["host"]
    port = data["port"]

    connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)

    return engine


def insert(df: pd.DataFrame, database_: str):
    engine = get_engine(database=database_)
    df.to_sql('transactions', engine, if_exists='append', index=False)

    return engine


def remove_characters(word:str):
    new_word = word
    new_word = new_word.replace("`", "")
    new_word = new_word.replace("sql", "")
    new_word = new_word.replace("[", "")
    new_word = new_word.replace("]", "")
    return new_word
