import streamlit as st
import pandas as pd
import json
import requests
import os
from openai import OpenAI
import base64
import doc_util as du
import la_util as la
import key_summary as ks


DATA_PRTH = "/Users/hunkim/workspace/solar-paralegal/data/"
st.title("Paralegal AI with Solar")

solar_model = "solar-1-mini-chat"

if "messages" not in st.session_state:
    st.session_state.messages = {}

solar_llm = OpenAI(
    api_key=st.secrets["SOLAR_API_KEY"],
    base_url="https://api.upstage.ai/v1/solar",
)


def dirname2key(dirname):
    return "key_" + base64.b64encode(dirname.encode()).decode()

def show_summary_json(dirname):
    summary_json = f"{dirname}/summary.json"
    summary_json_str = ""
    if os.path.isfile(DATA_PRTH + summary_json):
        with open(DATA_PRTH + summary_json) as f:
            summary_json = json.load(f)
            summary_json_str = json.dumps(summary_json, indent=2)
            st.json(summary_json, expanded=False)
    return summary_json_str


def chat(dirname):
    dirname_key = dirname2key(dirname)

    summary_json_str = show_summary_json(dirname)
    if dirname_key not in st.session_state.messages:
        st.session_state.messages[dirname_key] = []

    for message in st.session_state.messages[dirname_key]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    place_user = st.empty()
    place_ai = st.empty()

    if prompt := st.chat_input(f"Ask anything about {dirname}", key="chat" + dirname):
        st.session_state.messages[dirname_key].append(
            {"role": "user", "content": prompt}
        )
        with place_user.chat_message("user"):
            st.markdown(prompt)

        with place_ai.chat_message("assistant"):
            stream = solar_llm.chat.completions.create(
                model=solar_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a paralegal AI. Based on the context please provide reasonable answer in English.",
                    },
                    {"role": "user", "content": summary_json_str},
                ]
                + [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[dirname_key]
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages[dirname_key].append(
            {"role": "assistant", "content": response}
        )


collection_name = st.text_input("New Case (Collection) Name:")
if collection_name:
    os.makedirs(DATA_PRTH + collection_name, exist_ok=True)
for dirname in os.listdir(DATA_PRTH):
    if not os.path.isdir(DATA_PRTH + dirname):
        continue

    with st.expander(dirname):
        uploaded_files = st.file_uploader(
            "Choose PDF and doc files",
            type=["pdf", "docx", "doc"],
            accept_multiple_files=True,
            key="upload" + dirname,
        )

        for uploaded_file in uploaded_files:
            bytes_data = uploaded_file.read()
            with st.spinner(f"Processing {uploaded_file.name}..."):
                # save the file
                with open(DATA_PRTH + dirname + "/" + uploaded_file.name, "wb") as f:
                    f.write(bytes_data)

                # process the file
                if uploaded_file.name.endswith(".doc") or uploaded_file.name.endswith(
                    ".docx"
                ):
                    du.process(DATA_PRTH + dirname + "/" + uploaded_file.name)
                else:
                    la.process(DATA_PRTH + dirname + "/" + uploaded_file.name)
        file_list = []
        for subfilename in os.listdir(DATA_PRTH + dirname):
            if os.path.isfile(DATA_PRTH + dirname + "/" + subfilename):
                if subfilename.endswith(".txt"):
                    continue

                is_processed = os.path.isfile(
                    DATA_PRTH + dirname + "/" + subfilename + ".txt"
                )
                file_list.append({"name": subfilename, "processed": str(is_processed)})

        file_list_df = pd.DataFrame(file_list)
        edited_df = st.data_editor(
            file_list_df, key="data_editor" + dirname, use_container_width=True
        )

        if st.button("Summarize", key=dirname):
            with st.spinner("Summarizing..."):
                summary_json = ks.process(DATA_PRTH + dirname, st.write)

        with st.container():
            chat(dirname)
