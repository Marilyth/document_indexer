import lucene
from indexer import Indexer
from textreader import *
import argparse
import os
from datetime import datetime
import tika

parser = argparse.ArgumentParser()
parser.add_argument('--command', type=str, default="store", help="Whether to [store] or [query] the index.")
parser.add_argument("--files", type=str, help="The path to the files to be stored in the index, can also be a url, seperated by commas. May be a text file, an image or a pdf.")
parser.add_argument("--query", type=str, help="The Lucene query to apply to the index.")
args = parser.parse_args()

if not os.path.isdir("./index_files"):
    os.mkdir("./index_files")

search_engine = Indexer()
if args.command == "store":
    if args.files:
        for user_file in args.files.split(","):
            with open() as f:
                f.write()
        search_engine.store_document("some test text", "./images/text_image.jpg")
else if args.command == "query"
    print(search_engine.search_document(args.query))
