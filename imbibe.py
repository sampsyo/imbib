#!/usr/bin/env python3

import requests
import click
import re

CITE_RE = r'^\[@([^\]]+)\]:\s*(.*)$'


def convert(in_stream, out_stream):
    in_text = in_stream.read()
    for match in re.finditer(CITE_RE, in_text):
        key, url = match.groups()
        print(key, url)


@click.command()
def imbibe():
    in_stream = click.get_text_stream('stdin')
    out_stream = click.get_text_stream('stdout')
    convert(in_stream, out_stream)


if __name__ == '__main__':
    imbibe()
