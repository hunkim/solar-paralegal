from docx import Document
import requests
import io


def get_text(fullfilename):
    doc = Document(fullfilename)

    all_text = ""
    for paragraph in doc.paragraphs:
        all_text += str(paragraph.text) + "\n"
    
    return all_text


def process(full_file_path):
    target_file = f"{full_file_path}.txt"
    with open(target_file, "w") as f:
        f.write(get_text(full_file_path))
        
if __name__ == "__main__":
    # check time spent
    import time

    start = time.time()
    fillfilename = "/Users/hunkim/workspace/solar-paralegal/data/bb.docx"
    response_text = get_text(fillfilename)
    print(time.time() - start, "seconds", response_text)
