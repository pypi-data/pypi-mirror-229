import json
from pathlib import Path

from pymultirole_plugins.v1.schema import Document, DocumentList
from pyprocessors_chunk_sentences.chunk_sentences import ChunkingUnit, TokenModel

from pyprocessors_rf_resegment.rf_resegment import (
    RFResegmentProcessor,
    RFResegmentParameters)


def test_rf_resegment_():
    testdir = Path(__file__).parent
    source = Path(testdir, "data/batch3.json")
    with source.open("r") as fin:
        jdocs = json.load(fin)
    original_docs = [Document(**jdoc) for jdoc in jdocs]
    processor = RFResegmentProcessor()
    parameters = RFResegmentParameters(unit=ChunkingUnit.token, model=TokenModel.xlm_roberta_base, chunk_token_max_length=416)
    docs = processor.process(original_docs, parameters)
    for jdoc, doc in zip(jdocs, docs):
        assert len(jdoc['sentences']) >= len(doc.sentences)
    dl = DocumentList(__root__=docs)
    result = Path(testdir, "data/batch3_chunked.json")
    with result.open("w") as fout:
        print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)
