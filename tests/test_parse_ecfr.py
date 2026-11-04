from bsa_aml.chunking import chunk_section
from bsa_aml.parse_ecfr import parse_ecfr

LONG = " ".join(["word"] * 40)
XML = f"""<?xml version="1.0"?>
<DIV5 N="1020" TYPE="PART"><HEAD>PART 1020</HEAD>
<DIV6 N="C" TYPE="SUBPART"><HEAD>Subpart C-Reports</HEAD>
<DIV8 N="1020.320" TYPE="SECTION"><HEAD>&#xA7; 1020.320 Reports.</HEAD>
<P>(a) General. (1) First {LONG}.</P>
<P>(1) Sub one {LONG}.</P>
<P>(h) Eighth {LONG}.</P>
<P>(i) Ninth, not roman numeral {LONG}.</P>
<P>(1) Under i {LONG}.</P>
</DIV8>
<DIV8 N="1020.999" TYPE="SECTION"><HEAD>&#xA7; 1020.999 Gone.</HEAD><P>[Reserved]</P></DIV8>
</DIV6></DIV5>"""


def test_labels_and_reserved_sections(tmp_path):
    f = tmp_path / "p.xml"
    f.write_text(XML, encoding="utf-8")
    secs = parse_ecfr(f, {"doc_id": "d", "source": "s", "retrieved_at": "t"}, "Part 1020")
    assert [s.cite_base for s in secs] == ["31 CFR \u00a7 1020.320"]  # reserved section dropped
    labels = [b.label for b in secs[0].blocks]
    assert labels == ["(a)", "(a)(1)", "(h)", "(i)", "(i)(1)"]  # (i) follows (h): a letter, not roman
    assert chunk_section(secs[0])[0]["citation"] == "31 CFR \u00a7 1020.320(a)"
