from collections import defaultdict
from typing import Type, List, cast
import re
from collections_extended import RangeMap
from pydantic import BaseModel
from pymultirole_plugins.v1.processor import ProcessorParameters
from pymultirole_plugins.v1.schema import Document, Sentence, Span, Boundary
from pyprocessors_chunk_sentences.chunk_sentences import ChunkSentencesParameters, ChunkSentencesProcessor


class RFResegmentParameters(ChunkSentencesParameters):
    pass


def clean_renvois(document: Document):
    rtext = ""
    dtext = document.text
    start = 0
    spans = []
    matches = re.finditer("\\((voir|ex)[^)]+\\)", dtext)
    for matchNum, match in enumerate(matches, start=1):
        if match.group().endswith("*)"):
            rtext += dtext[start:match.start()]
            start = match.end()
            spans.append(Span(start=match.start(), end=match.end()))
    if start < len(dtext):
        rtext += dtext[start:]
    document.text = rtext
    offset = 0
    sentences = []
    for sent in document.sentences:
        soffset = 0
        for span in spans:
            if sent.start <= span.start and span.end <= sent.end:
                soffset += span.end - span.start
        sent2 = Sentence(start=sent.start - offset, end=sent.end - soffset - offset, metadata=sent.metadata)
        offset += soffset
        sentences.append(sent2)
    document.sentences = sentences
    return document


class RFResegmentProcessor(ChunkSentencesProcessor):
    """Recompute segments according to sections and eventually group sentences by chunks of given max length.
    To be used in a segmentation pipeline."""

    def process(
            self, documents: List[Document], parameters: ProcessorParameters
    ) -> List[Document]:
        params: RFResegmentParameters = cast(RFResegmentParameters, parameters)
        for document in documents:
            seen_offsets = RangeMap()
            sorted_boundaries = sorted(document.boundaries['SECTIONS'], key=left_shortest_match, reverse=True)
            for b in sorted_boundaries:
                ranges = seen_offsets.get_range(b.start, b.end)
                if not ranges:
                    seen_offsets[b.start: b.end] = b
                else:
                    for s in sentences_of_boundary(
                            document.sentences,
                            b):
                        sranges = seen_offsets.get_range(s.start, s.end)
                        if not sranges:
                            seen_offsets[s.start: s.end] = Boundary(name=b.name, start=s.start, end=s.end)
            boundaries = defaultdict(list)
            for b in sorted(seen_offsets.values(), key=natural_order, reverse=True):
                boundaries[b.name].append(b)
            # boundaries = {b.name: b for b in sorted(seen_offsets.values(), key=natural_order, reverse=True)}
            # titre = boundaries.pop('/DOCUMENT[1]/DOC_INTRO[1]/TITRE[1]', None)
            sur_titre = boundaries.pop('/DOCUMENT[1]/DOC_INTRO[1]/TITRE[1]', None)
            if not document.title and sur_titre:
                document.title = document.text[sur_titre[0].start: sur_titre[0].end]
            sentences = []
            for blst in boundaries.values():
                for b in blst:
                    btext = document.text[b.start:b.end]
                    if len(btext.strip()) > 0:
                        for cstart, cend in ChunkSentencesProcessor.group_sentences(document.text,
                                                                                    list(sentences_of_boundary(
                                                                                        document.sentences or [b],
                                                                                        b)),
                                                                                    params):
                            sentences.append(Sentence(start=cstart, end=cend, metadata={'xpath': b.name}))
            document.sentences = sentences
            document.boundaries = None
            document = clean_renvois(document)

        return documents

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return RFResegmentParameters


def left_shortest_match(a: Span):
    return a.start - a.end, -a.start


def natural_order(a: Span):
    return -a.start, a.end - a.start


def sentences_of_boundary(sentences, boundary):
    for sent in sentences:
        if sent.start >= boundary.start and sent.end <= boundary.end:
            yield sent
