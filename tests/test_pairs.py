import json

from bsa_aml import pairs


def chunk(i, source="fincen", doc="d1", path=("H1", "H2")):
    return {"chunk_id": f"c{i}", "doc_id": doc, "source_type": source, "section_path": list(path),
            "text": f"text {i}", "body": f"body keyword {i}"}


def test_heldout_section_excludes_sibling_chunks_but_not_other_sections():
    chunks = [chunk(0), chunk(1), chunk(2, path=("H1", "Other")), chunk(3, doc="d2")]
    qs = [{"id": "q", "gold": [{"doc": "d1", "must": ["keyword 0"]}]}]
    # gold = c0; its section (d1, H1/H2) also holds c1
    assert pairs.eligible(chunks, qs) == [2, 3]


def test_sample_is_balanced_reproducible_and_redistributes_slack():
    chunks = [chunk(i, "fincen") for i in range(100)] + [chunk(100 + i, "ffiec") for i in range(3)]
    idxs = list(range(len(chunks)))
    a = pairs.sample(chunks, idxs, 30, seed=1)
    assert a == pairs.sample(chunks, idxs, 30, seed=1)
    assert len(a) == 30 and len(set(a)) == 30
    by = {s: sum(1 for i in a if chunks[i]["source_type"] == s) for s in ("ffiec", "fincen")}
    assert by["ffiec"] == 3 and by["fincen"] == 27  # ffiec exhausted, fincen takes the slack
    assert len(pairs.sample(chunks, idxs, 10_000)) == len(chunks)


def test_parse_question():
    assert pairs.parse_question('"What must a bank file within 30 days?"') == "What must a bank file within 30 days?"
    assert pairs.parse_question("Question: How long are records kept for?") == "How long are records kept for?"
    assert pairs.parse_question("Too short?") is None
    assert pairs.parse_question("Line one is here\nand line two is here too") is None


def test_parse_judge():
    assert pairs.parse_judge('ok {"score": 5, "reason": "direct"} done') == {"score": 5, "reason": "direct"}
    assert pairs.parse_judge('{"score": 9}') is None
    assert pairs.parse_judge("no json") is None


class Fake:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []

    def complete(self, model_id, prompt, **kw):
        self.calls.append((model_id, prompt))
        return self.replies.pop(0)


def test_generate_is_resumable_and_skips_bad_output(tmp_path):
    chunks = [chunk(i) for i in range(3)]
    out = tmp_path / "raw.jsonl"
    llm = Fake(["What does the rule require banks to do?", "bad", "How long must records be retained?"])
    assert pairs.generate(llm, "m", chunks, [0, 1, 2], out, limit=None) == 2
    llm2 = Fake([])
    assert pairs.generate(llm2, "m", chunks, [0, 2], out, limit=None) == 0  # both already done
    assert not llm2.calls


def test_filter_drops_low_scores_and_re_applies_current_heldout():
    chunks = [chunk(0), chunk(1, path=("H1", "Other")), chunk(2, path=("H1", "Third"))]
    judged = [
        {"chunk_id": "c0", "question": "q0 long enough here", "score": 5, "source_type": "fincen"},
        {"chunk_id": "c1", "question": "q1 long enough here", "score": 5, "source_type": "fincen"},
        {"chunk_id": "c2", "question": "q2 long enough here", "score": 3, "source_type": "fincen"},
    ]
    # the test set was edited after generation: c0's section is now held out
    qs = [{"id": "q", "gold": [{"doc": "d1", "must": ["keyword 0"]}]}]
    kept, stats = pairs.filter_pairs(chunks, qs, judged)
    assert [k["chunk_id"] for k in kept] == ["c1"]
    assert stats == {"heldout": 1, "kept": 1, "low_score": 1}
    assert json.dumps(kept[0])  # serialisable
