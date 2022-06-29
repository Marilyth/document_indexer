from crypt import methods
from flask import Flask, request, send_from_directory
from threading import Thread
from indexer import Indexer
from textreader import *
from datetime import datetime
import lucene

search_engine: Indexer = None
api = Flask(__name__)
current_file_name = None
current_scan = []
language = "deu"

def get_scan_page(relative_reverse_one=True):
    new_scan_href = f"<a href=/scan/new>New scan</a>"
    append_scan_href = f"<a href=/scan/append>Append to current scan</a>"
    finish_scan_href = f"<a href=/scan/finish>Finish scan</a>"
    abort_scan_href = f"<a href=/scan/abort>Abort scan</a>"

    if len(current_scan) > 0:
        return " ".join([append_scan_href, finish_scan_href, abort_scan_href])
    else:
        return " ".join([new_scan_href])

@api.route("/scan/new", methods=["GET"])
def begin_new_scan():
    global current_file_name, current_scan
    current_file_name = datetime.now().strftime("%d-%m-%Y-%H-%M-%S.%f.pdf")
    image = process_image(scan_image().convert("RGB"))
    current_scan = [(image, read_image_text(image, language=language))]

    return f"Scanned {len(current_scan)} page<br>{get_scan_page()}"

@api.route("/scan/append", methods=["GET"])
def append_to_scan():
    global current_scan
    image = process_image(scan_image().convert("RGB"))
    current_scan.append((image, read_image_text(image, language=language)))

    return f"Scanned {len(current_scan)} pages<br>{get_scan_page()}"

@api.route("/scan/finish", methods=["GET"])
def finish_scan():
    global current_scan, current_file_name
    lucene.getVMEnv().attachCurrentThread()
    current_file_path = os.path.join("./index_files", current_file_name)
    current_scan[0][0].save(current_file_path, "PDF" ,resolution=100.0, save_all=True, append_images=[scan[0] for scan in current_scan[1:]])
    search_engine.store_document("\n\n".join([scan[1] for scan in current_scan[:]]), current_file_path)

    current_scan = []
    current_file_name = None
    return f"Saved scan to index<br>{get_scan_page()}"

@api.route("/scan/abort", methods=["GET"])
def abort_scan():
    global current_file_name, current_scan
    current_scan = []
    current_file_name = None

    return f"Aborted scan<br>{get_scan_page()}"

@api.route("/scan", methods=["GET"])
def scan_page():
    return get_scan_page(False)

@api.before_first_request
def initialise_engine():
    global search_engine
    search_engine = Indexer()

def search_index_term(search_term: str):
    if len(search_term.split(" ")) == 1:
        search_term = "*" + search_term

    text_query = "(" + " AND ".join([f"text:{word}" for word in search_term.split(" ")]) + "*)"
    stemmed_text_query = "(" + " AND ".join([f"stemmed_text:{word}" for word in search_term.split(" ")]) + "*)"
    stemmed_query = "(" + " AND ".join([f"stemmed_text:{search_engine.stem_text(word)}" for word in search_term.split(" ")]) + "*)"
    query = f"{text_query} OR {stemmed_text_query} OR {stemmed_query}"

    return search_engine.search_document(query)

@api.route("/search/<search_term>", methods=["GET"])
def search_index(search_term):
    lucene.getVMEnv().attachCurrentThread()
    documents = search_index_term(search_term)
    return "<br>".join([f"Score: {document[1]} <a href=\"../document/{document[2]}\">{document[0].get('path')}</a>" for document in documents])

@api.route("/document/<document_id>", methods=["GET"])
def get_document(document_id):
    lucene.getVMEnv().attachCurrentThread()
    if not search_engine.searcher:
        search_index_term("asdffdsa")

    document = search_engine.searcher.doc(int(document_id))
    document_path = document.get("path").split(",")[0]
    print(f"Requested {document_path}")
    return send_from_directory(directory="./", path=document_path)


def start_server(lang:str = "deu"):
    global language
    language = lang
    print("Starting server...")
    Thread(target=api.run).start()