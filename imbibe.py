#!/usr/bin/env python3

import requests
import click
import re
from urllib.parse import urlparse, parse_qs
import bs4
from pybtex.database.input import bibtex
import pybtex.database
from collections import OrderedDict

CITE_RE = r'^\[@([^\]]+)\]:\s*(.*)$'


def parse_bibtex(text):
    """Parse a BibTeX document with Pybtex and return a
    `BibliographyData` object.
    """
    parser = bibtex.Parser()
    return parser.parse_string(text)


def parse_bibtex_single(text):
    """Parse an individual BibTeX entry and return an `Entry` object.
    """
    doc = parse_bibtex(text)
    return doc.entries.values()[0]


def dump_bibtex_entry(key, entry):
    """Serialize an `Entry` object as a BibTeX string.
    """
    data = pybtex.database.BibliographyData({key: entry})
    return data.to_string('bibtex')


def scrape_acm_bibtex(acm_id):
    """Scrape the BibTeX entries from an ACM DL page. Generate a
    sequence of BibTeX strings.
    """
    req = requests.get(
        'http://dl.acm.org/exportformats.cfm',
        params={
            'id': acm_id,
            'expformat': 'bibtex',
        },
    )
    soup = bs4.BeautifulSoup(req.content, 'html.parser')
    for pre in soup.find_all('pre'):
        yield pre.get_text().strip()


def acm_fetch(acm_id):
    """Get an `Entry` object for an ACM DL page.
    """
    entries = [parse_bibtex_single(e) for e in scrape_acm_bibtex(acm_id)]

    if len(entries) == 1:
        # A single citation option.
        return entries[0]

    else:
        # Multiple options. This happens a lot when a conference also
        # publishes a "notices"-style journal, which is never the right
        # thing to cite.
        for entry in entries:
            if entry.type == 'inproceedings':
                return entry
        return entries[0]


def acm_simplify(entry):
    """Given an `Entry` object from ACM, produce a simpler, less-wrong
    `Entry` object.
    """
    if entry.type == 'inproceedings':
        # For conference proceedings, the most reasonable conference
        # title is typically hiding in the "series" field.
        conf_title, _ = entry.fields['series'].split()
        fields = OrderedDict([
            ('title', entry.fields['title']),
            ('year', entry.fields['year']),
            ('booktitle', conf_title),
        ])
        return pybtex.database.Entry(entry.type, fields, persons=entry.persons)

    else:
        # TODO: Simplify journals and such.
        return entry


def scrape_acm(url):
    # Check whether this is an ACM citation.
    parts = urlparse(url)
    if parts.netloc == 'dl.acm.org' and parts.path == '/citation.cfm':
        query = parse_qs(parts.query)
        if 'id' in query:
            cite_id = query['id'][0]
            return acm_simplify(acm_fetch(cite_id))
    return None


SCRAPERS = [scrape_acm]


def url_to_entry(url):
    for scrape in SCRAPERS:
        entry = scrape(url)
        if entry:
            return entry


def convert(in_stream, out_stream):
    in_text = in_stream.read()
    for match in re.finditer(CITE_RE, in_text):
        key, url = match.groups()
        entry = url_to_entry(url)
        if entry:
            out_stream.write(dump_bibtex_entry(key, entry))


@click.command()
def imbibe():
    in_stream = click.get_text_stream('stdin')
    out_stream = click.get_text_stream('stdout')
    convert(in_stream, out_stream)


if __name__ == '__main__':
    imbibe()
