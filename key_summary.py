import os
import streamlit as st
from solar_util import Solar
import json

SOLAR_API_KEY = st.secrets["SOLAR_API_KEY"]

SUMMARY_PER_CHUNK = 200

solar = Solar(api_key=SOLAR_API_KEY)


def key_summary_lines(lines, key_name):
    line_str = "\n".join(lines)
    line_str = line_str[:10000]

    messages = [
        {
            "role": "system",
            "content": "You are a paralegal AI. You can help me summarize this document. Please response all in English.",
        },
        {
            "role": "user",
            "content": f"{key_name}\n---\n{line_str}",
        },
    ]

    response = solar.invoke(messages=messages)
    response_text = Solar.parse_response(response)

    print(response_text)
    return response_text


def key_summary_dir(dir_name, key_name, print_func=print):
    results = []
    for file_name in os.listdir(dir_name):
        if file_name.endswith(".txt"):
            with open(os.path.join(dir_name, file_name)) as f:
                lines = f.readlines()

                # divide by 100 linne chunks
                for i in range(0, len(lines), SUMMARY_PER_CHUNK):
                    chunk = lines[i : i + SUMMARY_PER_CHUNK]
                    result = key_summary_lines(chunk, key_name)
                    results.append(result)
                    print_func(result)
    return results


def get_key_prompt(key_name):
    return f"""Extract succient {key_name} (one word) in json format {{"{key_name}": value}} from the context if any. 
    Please produce ONLY VALID JSON formant. No other text should be included.
    If you can't find any, please return the value with "null" value."""


def get_key_summary_prompt(key_name):
    return f"""Summarize the context relevent to {key_name} in a few sentences. 
    if you can't find any, please return "null" value."""


def process(dir_name, print_func):
    summary_results = {}
    keys = ["person", "topic", "key issue", "date"]

    for key in keys:
        results = key_summary_dir(dir_name, get_key_prompt(key), print_func=print_func)
        for result in results:
            try:
                json_result = json.loads(result)
                if not json_result or type(json_result) != dict:
                    continue

                value = json_result.get(key, "null")

                key_summary_all = ""
                if value and value != "null" and value != "None":
                    print_func(f"{key}: {value}")
                    key_summary = key_summary_dir(dir_name, get_key_summary_prompt(key))
                    print_func(f"{key} summary: {key_summary}")
                    key_summary_all += "\n" + "\n".join(key_summary) + "\n"
                
                long_key = f"{key}__{value}"

                if long_key in summary_results:
                    summary_results[long_key] += key_summary_all
                else:
                    summary_results[long_key] = key_summary_all
            except json.JSONDecodeError:
                print(f"Error: {result}")
                continue

    print_func(json.dumps(summary_results, indent=2))

    # Final summary
    final_summary_results = {}

    for key, value in summary_results.items():
        final_sum = key_summary_lines([value], f"Summarize this content and make it easy to read for the key {key} in a few sentences.")
        final_summary_results[key] = final_sum
    
    print_func(json.dumps(final_summary_results, indent=2))
    #store it to the file
    with open(dir_name + "/summary.json", "w") as f:
        json.dump(final_summary_results, f, indent=4)

    return final_summary_results
    

if __name__ == "__main__":
    dir = "/Users/hunkim/workspace/solar-paralegal/data/kasey"
    process(dir, print)
   