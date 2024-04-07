import streamlit as st
import requests
import os
import json

UPSTAGE_OCR_API_KEY = st.secrets["UPSTAGE_OCR_API_KEY"]


def get_layout(full_file_path):

    url = "https://api.upstage.ai/v1/document-ai/layout-analyzer"
    headers = {"Authorization": f"Bearer {UPSTAGE_OCR_API_KEY}"}

    files = {"document": open(full_file_path, "rb")}
    response = requests.post(url, headers=headers, files=files)
    response_json = response.json()

    print(response_json)

    response_html = ""
    for element in response_json["elements"]:
        response_html += element.get("html", "") + "<br>"

    return response_html

def process(full_file_path):
    target_file = f"{full_file_path}.txt"
    with open(target_file, "w") as f:
        f.write(get_layout(full_file_path))

if __name__ == "__main__":
    # check time spent
    import time

    start = time.time()
    full_file_path = "/Users/hunkim/workspace/solar-paralegal/data/aa.pdf"

    response_html = get_layout(full_file_path)
    print(time.time() - start, "seconds", response_html)
