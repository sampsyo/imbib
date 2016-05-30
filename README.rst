Imbib: Cite by URL
==================

Imbib lets you cite papers using their URLs. It translates these citations to
BibTeX by scraping the corresponding databases.

Cite with Markdown-like syntax::

    [@threads]: http://dl.acm.org/citation.cfm?id=1065042

Imbibe::

    imbib < example.md > example.bib

Enjoy your BibTeX::

    @inproceedings{threads,
        author = "Boehm, Hans-J.",
        title = "Threads Cannot Be Implemented As a Library",
        year = "2005",
        booktitle = "PLDI"
    }
