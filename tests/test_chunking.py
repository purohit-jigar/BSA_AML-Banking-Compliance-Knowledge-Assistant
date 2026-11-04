from bsa_aml.chunking import MAX_WORDS, Block, Section, chunk_section

DOC = {"doc_id": "d1", "source": "S", "title": "Doc", "url": "u", "retrieved_at": "t"}


def sec(blocks, path=("H1",)):
    return Section(doc=DOC, path=list(path), blocks=blocks, cite_base="Doc")


def para(n, tag="w"):
    return " ".join(f"{tag}{i}" for i in range(n)) + "."


def test_small_section_is_one_chunk_with_heading_prefix():
    ch = chunk_section(sec([Block(para(50), 3)]))
    assert len(ch) == 1
    assert ch[0]["text"].startswith("Doc \u203a H1\n\n")
    assert ch[0]["page_start"] == ch[0]["page_end"] == 3


def test_chunks_respect_cap_and_never_cross_sections():
    blocks = [Block(para(120, f"p{i}x"), 1) for i in range(6)]
    ch = chunk_section(sec(blocks))
    assert len(ch) > 1
    assert all(c["n_words"] <= MAX_WORDS + 40 for c in ch)  # cap + one overlap block
    assert all(c["section_path"] == ["Doc", "H1"] for c in ch)


def test_overlap_repeats_short_trailing_block():
    blocks = [Block(para(200, "a")), Block(para(30, "b")), Block(para(200, "c"))]
    ch = chunk_section(sec(blocks))
    assert "b0" in ch[0]["body"] and "b0" in ch[1]["body"]


def test_oversized_block_is_split():
    ch = chunk_section(sec([Block(" ".join(["Sentence number one is here."] * 200))]))
    assert len(ch) >= 2 and all(c["n_words"] <= MAX_WORDS for c in ch)


def test_tiny_chunks_dropped_and_labels_cited():
    assert chunk_section(sec([Block("[Reserved]")])) == []
    c = chunk_section(sec([Block(para(40), None, "(a)(1)")]))[0]
    assert c["citation"] == "Doc(a)(1)"
