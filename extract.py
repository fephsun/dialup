"""
Parse out text, links, images, and more from an HTML file.

http://www.crummy.com/software/BeautifulSoup/bs4/doc/


For example:
    import extract
    e = extract.ParsedWebpage("http://en.wikipedia.org/wiki/Frog")
    print e.title
    print e.text
    print e.links
"""

import copy
import json
import re
from urlparse import urljoin

import bs4
import requests

import secrets

def _clarifai_tags(url):
    # TODO: Batch this so that we do one Clarifai request only.
    # Requires, like, deferreds.

    access_token = secrets.clarifai_access_token
    clarifai_url = "https://api.clarifai.com/v1/tag/?url="
    response = requests.get(clarifai_url + url,
        headers={'Authorization': ' Bearer %s' % access_token})

    # Consult https://developer.clarifai.com/docs/tag
    retval = json.loads(response.text)['results'][0]['result']['tag']['classes']

    # Sometimes Clarifai returns [["tag1", "tag2", "tag3"]] instead of
    # just ["tag1", "tag2", "tag3"].
    if len(retval) == 1 and type(retval[0]) == list:
        return retval[0]

    return retval

class ParsedWebpage(object):
    def __init__(self, url):
        self.url = url

        # Raw HTML
        response = requests.get(url)
        self.html = response.text

        self.soup = bs4.BeautifulSoup(self.html, "html.parser")

        # Delete <script> and <style> tags, comments, and <!DOCTYPE>.
        # For some reason, doing this twice removes some sticky cases.
        for i in range(2):
            [s.extract() for s in self.soup.find_all('script')]
            [s.extract() for s in self.soup.find_all('style')]
            [s.extract() for s in self.soup.find_all('form')]
            comments = self.soup.findAll(text=lambda text:isinstance(text, bs4.Comment))
            [comment.extract() for comment in comments]
            new_html = re.sub("<!--.*?-->", "", unicode(self.soup))
            new_html = re.sub("<!DOCTYPE[^>]*>", "", new_html)
            self.soup = bs4.BeautifulSoup(new_html, "html.parser")

        # This should be something acceptable to read to the user
        # as the webpage's title.
        self.title = self.soup.title.string

        # Replace images with descriptions of those images.
        def my_replace(match):
            raw_tag = match.group()
            img_soup = bs4.BeautifulSoup(raw_tag, "html.parser")
            src = img_soup.img.get("src")
            alt = img_soup.img.get("alt")

            retval = " An image"
            if alt:
                retval += " of %s" % alt
            if src:
                retval += " that looks like "
                joined_url = urljoin(url, src)
                tags = _clarifai_tags(joined_url)[:5]
                if len(tags) > 1:
                    tags[-1] = "and " + tags[-1]
                retval += ', '.join(tags)
            return retval + '. '

        new_html = re.sub("<img[^>]*\>[^>]*<\\img\>", my_replace, unicode(self.soup))
        new_html = re.sub("<img[^>]*\>", my_replace, new_html)
        self.soup = bs4.BeautifulSoup(new_html, "html.parser")



        # This should be a list of (link name, link href) pairs.
        links = self.soup.find_all('a')
        self.links = [(link.string, urljoin(url, link.get('href', '')))
                      for link in links
                      if link.string]

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
        self.text = '. '.join(new_texts)


        # TODO: forms and related trappings
        # TODO: iframes?
        # TODO: music and videos
