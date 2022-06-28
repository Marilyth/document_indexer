import lucene
from indexer import Indexer
from textreader import *
import argparse
import os
from datetime import datetime
from tika import parser as tika_parser
import requests
import shutil

def process_file(user_file: str, indexer: Indexer, copy_directory:str = "./index_files", path:str = None, file_name:str = None):
    """
    Takes a user provided file input, and stores it in the lucene index.
    This may be a url, an image, a text file or a pdf.
    """
    user_file = user_file.strip()
    print(f"Processing {user_file}...")

    if not file_name:
        file_name = datetime.now().strftime("%d-%m-%Y-%H-%M-%S.%f")

    file_path = os.path.join(copy_directory, file_name)

    if not path:
        path = file_path

    # Download from url.
    if user_file.startswith("http"):
        print(f"Downloading {user_file}...")
        file_content = requests.get(user_file, timeout=5)
        print("Writing to file...")
        with open(file_path, "wb") as temp_file:
            temp_file.write(file_content.content)

    # Copy from local.
    elif os.path.exists(user_file):
        shutil.copy2(user_file, file_path)

    # Try image parsing.
    try:
        print("Trying image parsing...")
        image = open_image(file_path)
        processed_image = process_image(image)
        text = read_image_text(processed_image).strip()
        indexer.store_document(text, path)
        print(f"Saved imaged with text:\n{text}")
        return
    except Exception as e:
        print(e)

    # Try raw text parsing.
    try:
        print("Trying text parsing...")
        with open(file_path, "r") as f:
            text = f.read()
            indexer.store_document(text, path)
            print(f"Saved textfile with text:\n{text}")
            return
    except Exception as e:
        print(e)

    # Try .pdf parsing.
    try:
        parsed_pdf = tika_parser.from_file(file_path)
        text = parsed_pdf["content"].encode('ascii', errors='ignore').strip()
        indexer.store_document(text, path)
        print(f"Saved pdf with text:\n{text}")
        return
    except Exception as e:
        print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', type=str, default="store", help="Whether to [store] or [query] the index.")
    parser.add_argument("--files", type=str, help="The path to the files to be stored in the index, can also be a url, seperated by commas. May be a .txt file, an image or a .pdf.\nMultiple files will point to each other in the path field.")
    parser.add_argument("--query", type=str, help="The Lucene query to apply to the index.")
    args = parser.parse_args()

    if not os.path.isdir("./index_files"):
        os.mkdir("./index_files")

    search_engine = Indexer()
    if args.command == "store":
        print("Storing to index...")

        file_name_prefix = datetime.now().strftime("%d-%m-%Y-%H-%M-%S.%f")

        if args.files:
            paths = ",".join([f"{file_name_prefix}_{i}" for i, file in enumerate(args.files.split(","))])
            for i, user_file in enumerate(args.files.split(",")):
                process_file(user_file, search_engine, file_name=f"{file_name_prefix}_{i}", path=paths)

    elif args.command == "query":
        for result in search_engine.search_document(args.query):
            print(f"Score: {result[1]}, Matched {result[0]['path']} ({result[0]['date']}):\n{result[0]['text']}")
