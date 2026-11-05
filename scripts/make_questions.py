"""One-off: writes the DRAFT eval/test_questions.jsonl. After the user edits the JSONL, this
script must not be re-run (it would overwrite their edits)."""

import json
import sys
from pathlib import Path

F = "ffiec-"
A = "AssessingTheBSAAMLComplianceProgram"
Q = [
    ("regulation", "Within how many calendar days must a bank file a SAR after it first detects facts that may constitute a basis for filing?", [("§ 1020.320", ["30 calendar days"])]),
    ("regulation", "What is the minimum dollar amount of a suspicious transaction that requires a bank to file a SAR?", [("§ 1020.320", ["$5,000"])]),
    ("regulation", "How long does a bank have to keep a copy of a filed SAR and the supporting documentation?", [("§ 1020.320", ["five years"])]),
    ("regulation", "What cash amount in a single day triggers a currency transaction report?", [("§ 1010.311", ["$10,000"])]),
    ("regulation", "What two prongs define who must be identified as a beneficial owner of a legal entity customer?", [("§ 1010.230", ["25 percent"])]),
    ("regulation", "Which identifying details must a bank collect from an individual before opening an account under its customer identification program?", [("§ 1020.220", ["date of birth"])]),
    ("regulation", "What minimum asset level makes an account a private banking account that needs enhanced due diligence?", [("§ 1010.605", ["$1,000,000"])]),
    ("regulation", "What records must a financial institution keep for funds transfers of $3,000 or more?", [("§ 1010.410", ["$3,000"])]),
    ("regulation", "What must a bank record when it sells cashier's checks or money orders for currency between $3,000 and $10,000?", [("§ 1010.415", ["$3,000"])]),
    ("regulation", "What must a financial institution do before sharing information with another institution under the voluntary information sharing provision?", [("§ 1010.540", ["notice"])]),
    ("regulation", "Who must report accounts held in a foreign country, and what types of accounts count as reportable?", [("§ 1010.350", ["financial interest"])]),
    ("regulation", "What amount of currency or monetary instruments carried across the U.S. border must be reported?", [("§ 1010.340", ["$10,000"])]),
    ("regulation", "What is the SAR filing threshold for a money services business?", [("§ 1022.320", ["$2,000"])]),
    ("regulation", "By when must a new money services business register with FinCEN?", [("§ 1022.380", ["180 days"])]),
    ("regulation", "What is the SAR dollar threshold for a casino?", [("§ 1021.320", ["$5,000"])]),
    ("regulation", "How soon after a business opens an account can the bank treat it as an exempt person for CTR purposes?", [("§ 1020.315", ["two months"])]),
    ("regulation", "Which parts of an AML program must a bank have at minimum, such as internal controls and a designated compliance person?", [("§ 1020.210", []), ("§ 1010.210", [])]),
    ("regulation", "What makes a bank a shell bank that U.S. covered institutions cannot hold correspondent accounts for?", [("§ 1010.630", ["shell bank"]), ("§ 1010.605", ["shell bank"])]),
    ("regulation", "How soon must a business that receives more than $10,000 in cash report it on Form 8300?", [("§ 1010.330", ["15 days"])]),
    ("regulation", "What does it mean to structure a transaction under the Bank Secrecy Act?", [("§ 1010.100", ["structure"]), ("§ 1010.314", ["structur"])]),
    ("exam", "What factors do examiners look at when judging whether a bank's BSA/AML risk assessment is adequate?", [(F + "03_", ["risk assessment"])]),
    ("exam", "What are the responsibilities and qualifications expected of a bank's BSA compliance officer?", [(F + "04_", ["compliance officer"])]),
    ("exam", "How frequently and how broadly should a bank's BSA/AML program be independently tested?", [(A + "-03", ["independent"])]),
    ("exam", "What should a good SAR narrative cover?", [(F + "10_Appendices-13", ["narrative"]), (F + "06_Assessing", ["narrative"])]),
    ("exam", "How should a bank handle continuing suspicious activity after it has already filed a SAR?", [(F + "06_Assessing", ["continuing"])]),
    ("exam", "Under what conditions can a bank rely on another financial institution to perform parts of its customer identification program?", [(F + "06_Assessing", ["rely", "customer identification"])]),
    ("exam", "What does ongoing monitoring mean as part of customer due diligence?", [(F + "06_Assessing", ["ongoing monitoring"])]),
    ("exam", "How should a bank treat the risk of customers who are politically exposed persons?", [(F + "09_", ["senior foreign political"])]),
    ("exam", "What transaction patterns are red flags for structuring?", [(F + "10_Appendices-0", ["structur"])]),
    ("exam", "What money laundering risks come with prepaid access products?", [(F + "09_", ["prepaid"])]),
    ("exam", "What makes third-party payment processors risky and how should a bank manage that risk?", [(F + "09_", ["payment processor"])]),
    ("exam", "What due diligence is expected for correspondent accounts held for foreign financial institutions?", [(F + "06_Assessing", ["correspondent account", "foreign"])]),
    ("exam", "What elements should an OFAC compliance program include?", [(F + "07_", ["compliance program"])]),
    ("exam", "Why is trade finance considered higher risk for money laundering?", [(F + "09_", ["trade finance"])]),
    ("exam", "How should a bank manage the risk of cash-intensive businesses?", [(F + "09_", ["cash-intensive"])]),
    ("exam", "What heightens money laundering or terrorist financing risk for charities and nonprofits?", [(F + "09_", ["nonprofit"])]),
    ("exam", "How do examiners use the bank's risk assessment to decide the scope of an exam?", [(F + "02_", ["risk assessment"])]),
    ("exam", "What factors determine which enforcement action is appropriate when a bank's BSA/AML program is deficient?", [(F + "10_Appendices-19", ["enforcement"])]),
    ("exam", "How long must different categories of BSA records be retained?", [(F + "10_Appendices-17", ["five years"])]),
    ("guidance", "What does FinCEN expect from banks that serve marijuana-related businesses when filing SARs?", [("marijuana", ["marijuana"])]),
    ("guidance", "How do FinCEN's regulations apply to administrators and exchangers of convertible virtual currency?", [("regulations-persons-admin", ["virtual currency"]), ("certain-business-models", ["virtual currency"])]),
    ("guidance", "Do banks have to update beneficial ownership information for existing customers on a regular schedule?", [("regarding-custome", ["beneficial owner"])]),
    ("guidance", "May a bank share a SAR with its parent or affiliates?", [("sharing-suspicious", ["affiliate"])]),
    ("guidance", "Who counts as a provider of prepaid access under FinCEN's final rule?", [("prepaid", ["provider"])]),
    ("guidance", "What information must travel with a funds transfer under the travel rule?", [("funds-travel", ["travel"])]),
    ("guidance", "Does a casino have to aggregate cash transactions across different gaming areas for CTR purposes?", [("casino", ["aggregat"])]),
    ("guidance", "Do SAR safe harbor protections hold up when a customer sues the bank?", [("federal-court-reaffirms", ["safe harbor"])]),
    ("guidance", "What AML program obligations apply to dealers in precious metals, stones, or jewels?", [("dealers-including-certain", ["precious"])]),
    ("guidance", "What red flags indicate an e-mail compromise fraud scheme?", [("e-mail-compr", ["e-mail"])]),
    ("guidance", "How should a bank fix errors in a batch of SARs it already filed electronically?", [("fin-2009-g005", ["batch"])]),
]
assert len(Q) == 50, len(Q)
out = Path(__file__).resolve().parents[1] / "eval" / "test_questions.jsonl"
if out.exists() and "--force" not in sys.argv:
    sys.exit("eval/test_questions.jsonl exists; pass --force to overwrite your edits")
out.parent.mkdir(exist_ok=True)
with out.open("w", encoding="utf-8") as f:
    for i, (t, q, g) in enumerate(Q, 1):
        row = {"id": f"q{i:02d}", "question": q, "type": t, "status": "draft",
               "gold": [{"doc": d, "must": m} for d, m in g]}
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
