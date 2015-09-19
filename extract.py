"""
Parse out text, links, images, and more from an HTML file.

http://www.crummy.com/software/BeautifulSoup/bs4/doc/
"""

from bs4 import BeautifulSoup
import urllib2



def get_metadata(url):
    html = _get_html(url)
    return {
        "title": _get_title(html),
        "text": _get_text(html),
        "links": _get_links(html),
        "images": _get_images(html)
    }

def _get_html(url):
    return urllib2.urlopen(url).read()

def _get_title(html):
    soup = BeautifulSoup(html, "html.parser")
    if soup.title.string:
        return soup.title.string
    elif soup.h1.string:
        return soup.h1.string
    else:
        return None

def _get_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

class Link(object):
    def __init__(self, text, href):
        self.text = text
        self.href = href

def _get_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all('a')
    return [Link(link.string, link['href']) for link in links]

class Image(object):
    def __init__(self, src):
        self.src = src

def _get_images(html):
    soup = BeautifulSoup(html, "html.parser")
    imgs = soup.find_all('img')
    return [Image(img['src']) for img in imgs]
