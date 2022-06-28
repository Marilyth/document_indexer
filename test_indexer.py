from indexer import Indexer
import pytest
import shutil
import os
import unittest

class Test_Indexer(unittest.TestCase):
    search_engine = None

    @classmethod
    def setUpClass(cls):
        cls.search_engine = Indexer("./test_index")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree("./test_index")

    def test_image(self):
        self.search_engine.store_document("some test text", "./images/text_image.jpg")
        assert os.path.isdir("./test_index")
        assert len(self.search_engine.search_document("text:test")) > 0
        assert len(self.search_engine.search_document("text:dog")) == 0
