"""
Parse out text, links, images, and more from an HTML file.

http://www.crummy.com/software/BeautifulSoup/bs4/doc/
"""

import copy
import json
import re
from urlparse import urljoin

import bs4
import requests

import secrets

def clarifai_tags(url):
    # TODO: Batch this so that we do one Clarifai request only.
    # Requires, like, deferreds.

    access_token = secrets.clarifai_access_token
    clarifai_url = "https://api.clarifai.com/v1/tag/?url="
    response = requests.get(clarifai_url + url,
        headers={'Authorization': ' Bearer %s' % access_token})
    return json.loads(response.text)['results'][0]['result']['tag']['classes']
    return ["space", "stars", "galaxy"]

class ParsedWebpage(object):
    def __init__(self, url):
        self.url = url

        # Raw HTML
        response = requests.get(url)
        self.html = response.text

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

        # Replace images with descriptions.
        def my_replace(match):
            raw_tag = match.group()
            img_soup = bs4.BeautifulSoup(raw_tag)
            src = img_soup.img.get("src")
            alt = img_soup.img.get("alt")

            retval = " An image"

            tags = []

            if alt:
                retval += " of %s" % alt
            if src:
                retval += "; it looks like "
                joined_url = urljoin(url, src)
                retval += ', '.join(clarifai_tags(joined_url)[:5])
            return retval + '. '

        new_html = re.sub("<img[^>]*\>[^>]*<\\img\>", my_replace, unicode(self.soup))
        new_html = re.sub("<img[^>]*\>", my_replace, new_html)
        self.soup = bs4.BeautifulSoup(new_html, "html.parser")



        # This should be a list of (link name, link href) pairs.
        links = self.soup.find_all('a')
        self.links = [(link.string, urljoin(url, link['href']))
                      for link in links
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
