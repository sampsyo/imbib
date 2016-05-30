#!/usr/bin/env python3

import requests
import click
import re
from urllib.parse import urlparse, parse_qs
import bs4

CITE_RE = r'^\[@([^\]]+)\]:\s*(.*)$'


def fetch_acm(acm_id):
    req = requests.get(
        'http://dl.acm.org/exportformats.cfm',
        params={
            'id': acm_id,
            'expformat': 'bibtex',
        },
    )
    soup = bs4.BeautifulSoup(req.content, 'html.parser')
    for pre in soup.find_all('pre'):
        bib_entry = pre.get_text().strip()
        print(bib_entry)


def scrape_acm(url):
    # Check whether this is an ACM citation.
    parts = urlparse(url)
    if parts.netloc == 'dl.acm.org' and parts.path == '/citation.cfm':
        query = parse_qs(parts.query)
        if 'id' in query:
            cite_id = query['id'][0]
            return fetch_acm(cite_id)
    return None


SCRAPERS = [scrape_acm]


def url_to_bib(url):
    for scrape in SCRAPERS:
        scrape(url)


def convert(in_stream, out_stream):
    in_text = in_stream.read()
    for match in re.finditer(CITE_RE, in_text):
        key, url = match.groups()
        print(key, url_to_bib(url))


@click.command()
def imbibe():
    in_stream = click.get_text_stream('stdin')
    out_stream = click.get_text_stream('stdout')
    convert(in_stream, out_stream)


if __name__ == '__main__':
    imbibe()
