# Download lucene here https://dlcdn.apache.org/lucene/pylucene
# https://lucene.apache.org/pylucene/install.html
# Requires java: https://adoptium.net/de/download

import sys
import requests
import tarfile
import os

def download_lucene():
    if not "pylucene" in [path.split("\\")[-1].split("/")[-1] for path in sys.path]:
        # Download and extract lucene.
        print("Downloading lucene...")
        file_content = requests.get("https://dlcdn.apache.org/lucene/pylucene/pylucene-9.1.0-src.tar.gz")
        with open("lucene.tar.gz", "wb") as f:
            f.write(file_content.content)

        print("Extracting lucene...")
        with tarfile.open("lucene.tar.gz") as tar:
            tar.extractall("./lucene_installation")
        os.remove("lucene.tar.gz")

        # Requires elevated access.
        # pushd jcc
        # export JCC_JDK="C:\Program Files\Eclipse Adoptium\jdk-17.0.3.7-hotspot"
        # python setup.py build
        # python setup.py install --user
        # popd
        # make
        # make test
        # make install
