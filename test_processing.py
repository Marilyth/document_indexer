from indexer import Indexer
import pytest
import shutil
import os
import unittest
import main

class Test_Indexer(unittest.TestCase):
    search_engine = None

    @classmethod
    def setUpClass(cls):
        cls.search_engine = Indexer("./test_index")
        if not os.path.isdir("./test_index_files"):
            os.mkdir("./test_index_files")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree("./test_index")
        shutil.rmtree("./test_index_files")

    def test_store_pdf(self):
        main.process_file("http://www.africau.edu/images/default/sample.pdf", self.search_engine, "./test_index_files")
        assert len(self.search_engine.search_document("And more text.")) > 0

    def test_store_image(self):
        main.process_file("https://www.maxqda.com/wp/wp-content/uploads/sites/2/18-En-Mixed-Methods-transform-code.png", self.search_engine, "./test_index_files")
        assert len(self.search_engine.search_document("relationship")) > 0

    def test_store_txt(self):
        main.process_file("https://raw.githubusercontent.com/Marilyth/document_indexer/main/README.md", self.search_engine, "./test_index_files")
        assert len(self.search_engine.search_document("search engine")) > 0
