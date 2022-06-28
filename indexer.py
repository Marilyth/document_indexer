# Download lucene here https://dlcdn.apache.org/lucene/pylucene
# https://lucene.apache.org/pylucene/install.html
# Requires java: https://adoptium.net/de/download
import os
from datetime import datetime
import lucene

from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser

class Indexer:
    def __init__(self):
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        self.store = FSDirectory.open(Paths.get("./index"))
        analyzer = StandardAnalyzer()
        self.analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        self.config = IndexWriterConfig(self.analyzer)
        self.config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
        self.writer = IndexWriter(self.store, self.config)
        self.searcher = None

    def store_document(self, text, source_path, creation_time=None):
        if not creation_time:
            creation_time = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
        document = Document()

        text_field = FieldType()
        text_field.setTokenized(True)
        text_field.setStored(True)
        text_field.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        date_field = FieldType()
        date_field.setTokenized(True)
        date_field.setStored(True)
        date_field.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        path_field = FieldType()
        path_field.setTokenized(False)
        path_field.setStored(True)
        path_field.setIndexOptions(IndexOptions.DOCS_AND_FREQS)

        document.add(Field("text", text, text_field))
        document.add(Field("path", source_path, path_field))
        document.add(Field("date", creation_time, date_field))
        self.writer.addDocument(document)
        self.writer.commit()

    def search_document(self, query, default_field="text"):
        if not self.searcher:
            self.searcher = IndexSearcher(DirectoryReader.open(self.store))

        lucene_query = QueryParser(default_field, self.analyzer).parse(f"{query}")
        score_docs = self.searcher.search(lucene_query, 50).scoreDocs

        return [(self.searcher.doc(score_doc.doc), score_doc.score) for score_doc in score_docs]
