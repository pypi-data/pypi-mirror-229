from pathlib import Path
from shutil import copy

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

HTML_FILENAME = "LoadTest.html"
HTML_FILEPATH = Path(__file__).parent / "static" / HTML_FILENAME


def copy_html(dst_dir) -> Path:
    dst_path = Path(dst_dir) / HTML_FILENAME
    copy(HTML_FILEPATH, str(dst_path))
    return dst_path


def load_url(fileurl: str):
    chrome_options = Options()
    # chrome_options.add_argument("--incognito")
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(fileurl)

    return driver
