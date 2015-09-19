"""
Parse out text, links, images, and more from an HTML file.

http://www.crummy.com/software/BeautifulSoup/bs4/doc/
"""

import copy
import re
import urllib2

import bs4

class ParsedWebpage(object):
    def __init__(self, url):
        self.url = url

        # Raw HTML
        self.html = urllib2.urlopen(url).read()

        self.soup = bs4.BeautifulSoup(self.html, "html.parser")

        # Delete <script> and <style> tags
        [s.extract() for s in self.soup.find_all('script')]
        [s.extract() for s in self.soup.find_all('style')]
        [s.extract() for s in self.soup.find_all('form')]
        comments = self.soup.findAll(text=lambda text:isinstance(text, bs4.Comment))
        [comment.extract() for comment in comments]
        new_html = re.sub("<!--.*?-->", "", unicode(self.soup))
        self.soup = bs4.BeautifulSoup(new_html, "html.parser")

        # For some reason, a second round of this removes some sticky cases
        [s.extract() for s in self.soup.find_all('script')]
        [s.extract() for s in self.soup.find_all('style')]
        [s.extract() for s in self.soup.find_all('form')]
        comments = self.soup.findAll(text=lambda text:isinstance(text, bs4.Comment))
        [comment.extract() for comment in comments]
        new_html = re.sub("<!--.*?-->", "", unicode(self.soup))
        self.soup = bs4.BeautifulSoup(new_html, "html.parser")

        # This should be something acceptable to read to the user
        # as the webpage's title.
        self.title = self.soup.title.string

        # This should be a list of (link name, link href) pairs.
        links = self.soup.find_all('a')
        self.links = [(link.string, link['href']) for link in links
                      if link.string]

        # This should be a list of img srcs.
        imgs = self.soup.find_all('img')
        self.imgs = [img['src'] for img in imgs]

        texts = self.soup.find_all(text=True)

        # Add in link labels!
        link_index = 0
        new_texts = []
        for text in texts:
            if link_index < len(self.links) and text == self.links[link_index][0]:
                new_texts.append("Link %s" % str(link_index))
                link_index += 1
            new_texts.append(text)

        # This should be the human-readable text of the page.
        self.text = ' '.join(new_texts)
        self.texts = texts
        self.new_texts = new_texts


        # TODO: forms and related trappings
        # TODO: iframes?
        # TODO: music and videos
