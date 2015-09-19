import unittest
from extract import _get_links, _get_images, _get_text, _get_title

html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>


<img src="http://google.com/image1" />

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>

<img src="http://google.com/image2"></img>
"""

class TestExtract(unittest.TestCase):
    def test_get_links(self):
        self.assertEquals([i.text for i in _get_links(html_doc)],
                          ["Elsie", "Lacie", "Tillie"])
        self.assertEquals([i.href for i in _get_links(html_doc)],
                          ["http://example.com/elsie",
                           "http://example.com/lacie",
                           "http://example.com/tillie"])
    def test_get_title(self):
        self.assertEquals(_get_title(html_doc), "The Dormouse's story")

    def test_get_text(self):
        self.assertEquals(_get_text(html_doc), u"\nThe Dormouse's story\n\nThe Dormouse's story\n\nOnce upon a time there were three little sisters; and their names were\nElsie,\nLacie and\nTillie;\nand they lived at the bottom of a well.\n...\n\n")

    def test_get_images(self):
        self.assertEquals([i.src for i in _get_images(html_doc)],
            ["http://google.com/image1", "http://google.com/image2"])
