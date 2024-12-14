import streamlit as st
import utils
import pandas as pd
import json
from openai import OpenAI

my_df = pd.DataFrame()
my_text = ""
clean_query = ""
with open("keys/openai.json", 'r') as file:
    data = json.load(file)
openai_api_key = data['openai_api_key']
output = ""
prompt_context = """
You generate ONLY SQL queries as plain text against the table 'transactions' with columns date 'mm/dd/yyyy', month, transaction, charges, credits
"""

st.title("📊 PDF Analyzer")
uploaded_file = st.file_uploader("📂 Upload your pdf file!", type="pdf")
my_page_start = st.number_input("Enter the initial page you want to analyse", min_value=1, max_value=21, step=1, key="my_page_start")-1
my_page_end = st.number_input("Enter the initial page you want to analyse", min_value=1, max_value=21, step=1, key="my_page_end")-1


if uploaded_file:
    print(f"From doc {my_page_start} to doc {my_page_end}")
    my_text = utils.extract_text_from_pdf(uploaded_file, page_start=my_page_start, page_end=my_page_end)

if st.button("Translate to a dataframe"):
    prediction_list = utils.translate(openai_api_key, my_text)
    my_df = pd.DataFrame(prediction_list).fillna(0)
    print(my_df.head())
    utils.insert(my_df, database_='exam')

st.title("Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAi")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": prompt_context}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    client = OpenAI(api_key=openai_api_key)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.messages, temperature=0.2, max_tokens=100)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
    
    print(f"Query generated... {msg}")
    clean_query=utils.remove_characters(str(msg))
    print(f"Query cleaned... {clean_query}")

    try:
        result_df = pd.read_sql(clean_query, utils.get_engine("exam"))
        st.dataframe(result_df)
    except Exception as e:
        print(f"Error running query: {e}")
