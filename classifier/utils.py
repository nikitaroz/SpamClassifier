import tarfile
from urllib.request import urlopen, urlretrieve
from os import mkdir, listdir
from os.path import join, exists, isdir
from tempfile import gettempdir

from bs4 import BeautifulSoup

BASE_DATA_URL = "http://spamassassin.apache.org/old/publiccorpus/"

def get_data_urls(base_url=BASE_DATA_URL):
    data_urls = []
    with urlopen(base_url) as response:
        
        soup = BeautifulSoup(response, 'html.parser')
        for anchor in soup.find_all('a'):
            href = anchor.get("href")
            if href.endswith(".bz2"):
                data_urls.append((href, join(BASE_DATA_URL, href)))
    return data_urls

def fetch_data(data_urls, data_dir):
    temp_dir = gettempdir()
    if not exists(data_dir):
        mkdir(data_dir)
    for fname, url in data_urls:
        temp_file_path = join(temp_dir, fname)
        urlretrieve(url, filename=temp_file_path)

        tar = tarfile.open(temp_file_path, "r:bz2")
        # check if tar has already been extracted
        for name in tar.getnames():
            if not exists(join(data_dir, name)):
                tar.extract(name, path=data_dir)
        tar.close()

def get_labeled_files(data_dir):
    data_files = []
    class_labels = []
    for dir_ in listdir(data_dir):
        data_folder = join(data_dir, dir_)
        if not isdir(data_folder):
            continue

        if "spam" in data_folder:
            class_label = 1
        else:
            class_label = 0

        for data_file in listdir(data_folder):
            if data_file.endswith("cmds"):
                continue
            data_files.append(join(data_folder, data_file))
            class_labels.append(class_label)
   
    return data_files, class_labels