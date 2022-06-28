curl -o pylucene.tar.gz https://dlcdn.apache.org/lucene/pylucene/pylucene-9.1.0-src.tar.gz
tar -xvzf pylucene.tar.gz
rm pylucene.tar.gz

# curl -OL https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.3%2B7/OpenJDK17U-jdk_x64_linux_hotspot_17.0.3_7.tar.gz
# tar -xvzf OpenJDK17U-jdk_x64_linux_hotspot_17.0.3_7.tar.gz
# rm OpenJDK17U-jdk_x64_linux_hotspot_17.0.3_7.tar.gz

sudo apt update
sudo apt-get install -y python3-dev
sudo apt-get install -y python3-pip
sudo apt-get install -y libpython3-dev
sudo apt-get install -y tesseract-ocr
sudo apt-get install -y temurin-17-jdk

cd pylucene-9.1.0
cd jcc
NO_SHARED=1 python3 setup.py install
cd ..
sudo make all install JCC='python3 -m jcc' PYTHON=python3 NUM_FILES=16

cd ..
rm -r pylucene-9.1.0
