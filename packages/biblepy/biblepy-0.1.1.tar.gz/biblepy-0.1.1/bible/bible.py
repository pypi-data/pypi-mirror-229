import json
import pkg_resources


class Bible:
    def __init__(self, filename):
        self.verses = []
        self.verses_by_citation = {}

        with open(filename, "r") as f:
            for line in f:
                verse = json.loads(line)
                self.verses.append(verse)
                self.verses_by_citation[verse["citation"]] = verse

    def get_text(self, citation):
        verses = []
        for cite in self._expand_citation(citation):
            verses.append(self.verses_by_citation[cite])
        return " ".join([v["text"] for v in verses])

    def _expand_citation(self, citation):
        # expand a bible verse citation that might include more than one verse
        # (e.g. John 3:16-17) into a list of individual verses
        # e.g. "John 3:16-17" -> ["John 3:16", "John 3:17"]
        book_chapter, verses = citation.split(":")
        verses = verses.split("-")
        if len(verses) == 1:
            return [citation]

        start, stop = int(verses[0]), int(verses[1])
        citations = []
        for i in range(start, stop + 1):
            citations.append(f"{book_chapter}:{i}")
        return citations

    def __iter__(self):
        return iter(self.verses)


class KJV(Bible):
    def __init__(self):
        filename = pkg_resources.resource_filename(__name__, "data/kjv.jsonl")
        super().__init__(filename)
