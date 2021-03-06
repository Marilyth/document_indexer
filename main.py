import lucene
from indexer import Indexer
from textreader import *
import argparse
import os
from datetime import datetime
from tika import parser as tika_parser
import requests
import shutil
from query_server import start_server

def process_file(user_file: str, indexer: Indexer, copy_directory:str = "./index_files", path:str = None, file_name:str = None, language:str = "eng"):
    """
    Takes a user provided file input, and stores it in the lucene index.
    This may be a url, an image, a text file or a pdf.
    """
    user_file = user_file.strip()
    print(f"Processing {user_file}...")

    if not file_name:
        file_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")

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
        image = image.convert("RGB")
        processed_image = process_image(image)
        text = read_image_text(processed_image, language=language).strip().replace("|", "I")
        extension = user_file.split(".")[-1]
        shutil.move(file_path, file_path + "." + extension)
        indexer.store_document(text, f"{file_path}.{extension}")
        print(f"Saved imaged with text:\n{text}")
        return
    except Exception as e:
        print(e)

    if ".pdf" in user_file:
        # Try .pdf parsing.
        try:
            print("Trying pdf parsing...")
            parsed_pdf = tika_parser.from_file(file_path)
            text = parsed_pdf["content"].encode('ascii', errors='ignore').decode("utf-8").strip().replace("|", "I")
            shutil.move(file_path, file_path + ".pdf")
            indexer.store_document(text, f"{file_path}.pdf")
            print(f"Saved pdf with text:\n{text}")
            return
        except Exception as e:
            print(e)

    # Try raw text parsing.
    try:
        print("Trying text parsing...")
        with open(file_path, "r") as f:
            text = f.read()
            shutil.move(path, path + ".txt")
            indexer.store_document(text, f"{path}.txt")
            print(f"Saved textfile with text:\n{text}")
            return
    except Exception as e:
        print(e)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', type=str, default="store", help="Whether to [store] or [query] the index.")
    parser.add_argument("--files", type=str, help="The path to the files to be stored in the index, can also be a url, seperated by commas. May be a .txt file, an image or a .pdf.\nMultiple files will point to each other in the path field.")
    parser.add_argument("--from-scanner", type=bool, default=False, help="Whether to use the scanner and add the image to the index.")
    parser.add_argument("--server", type=bool, default=False, help="Whether to start an interactive server.")
    parser.add_argument("--query", type=str, help="The Lucene query to apply to the index.")
    parser.add_argument("--search", type=str, help="The text to search for in the index. Overwrites --query.")
    parser.add_argument("--language", type=str, default="deu", help="The language of the image. Defaults to deu.")
    args = parser.parse_args()

    if not os.path.isdir("./index_files"):
        os.mkdir("./index_files")

    if args.server:
        start_server(args.language)
        exit()

    search_engine = Indexer()

    if args.search:
        text_query = "(" + " AND ".join([f"text:{word}" for word in args.search.split(" ")]) + "*)"
        stemmed_text_query = "(" + " AND ".join([f"stemmed_text:{word}" for word in args.search.split(" ")]) + "*)"
        stemmed_query = "(" + " AND ".join([f"stemmed_text:{search_engine.stem_text(word)}" for word in args.search.split(" ")]) + "*)"
        args.query = f"{text_query} OR {stemmed_text_query} OR {stemmed_query}"

    if args.command == "store" and not args.query:
        print("Storing to index...")

        file_name_prefix = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")

        if args.from_scanner:
            args.files = "temp.png"
            scan_image()
            
        if args.files:
            paths = ",".join([f"{file_name_prefix}_{i}" for i, file in enumerate(args.files.split(","))])
            for i, user_file in enumerate(args.files.split(",")):
                process_file(user_file, search_engine, file_name=f"{file_name_prefix}_{i}", path=paths, language=args.language)

    elif args.command == "query" or args.query:
        print(f"Searching for query: {args.query}")
        for result in search_engine.search_document(args.query):
            print(f"Score: {result[1]}, Matched {result[0]['path']} ({result[0]['date']}):\n{result[0]['text']}")
