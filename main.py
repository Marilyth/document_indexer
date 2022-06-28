import lucene
from indexer import Indexer
from textreader import *
import argparse
import os
from datetime import datetime
from tika import parser as tika_parser
import requests
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('--command', type=str, default="store", help="Whether to [store] or [query] the index.")
parser.add_argument("--files", type=str, help="The path to the files to be stored in the index, can also be a url, seperated by commas. May be a .txt file, an image or a .pdf.")
parser.add_argument("--query", type=str, help="The Lucene query to apply to the index.")
args = parser.parse_args()

if not os.path.isdir("./index_files"):
    os.mkdir("./index_files")

search_engine = Indexer()
if args.command == "store":
    print("Storing to index...")

    if args.files:
        for user_file in args.files.split(","):
            print(f"Processing {user_file}...")
            file_name = datetime.now().strftime("%d-%m-%Y-%H-%M-%S.%f")
            file_path = os.path.join("./index_files", file_name)

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
                text = read_image_text(processed_image)
                search_engine.store_document(text, file_path)
                print(f"Saved imaged with text:\n{text}")
                exit()
            except Exception as e:
                print(e)

            # Try raw text parsing.
            try:
                print("Trying text parsing...")
                with open(file_path, "r") as f:
                    text = f.read()
                    search_engine.store_document(text, file_path)
                    print(f"Saved textfile with text:\n{text}")
                    exit()
            except Exception as e:
                print(e)

            # Try .pdf parsing.
            try:
                parsed_pdf = tika_parser.from_file(file_path)
                text = parsed_pdf["content"].encode('ascii', errors='ignore')
                search_engine.store_document(text, file_path)
                print(f"Saved pdf with text:\n{text}")
                exit()
            except Exception as e:
                print(e)

elif args.command == "query":
    for result in search_engine.search_document(args.query):
        print(f"Score: {result[1]}, Matched {result[0]['path']} ({result[0]['date']}): {result[0]['text']}")
