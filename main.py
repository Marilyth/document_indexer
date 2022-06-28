import lucene
from indexer import Indexer

search_engine = Indexer()
#search_engine.store_document("some test text", "./images/text_image.jpg")
print(search_engine.search_document(input("Query:")))
