# Test-question review checklist

Goal: you own the 50 questions and their gold labels. Work through each block, edit `eval/test_questions.jsonl` directly, tick the boxes.

## Per question
- [ ] Wording is natural (how a compliance analyst would ask it), in your own words
- [ ] Answerable from the corpus (not from outside knowledge)
- [ ] Each gold chunk below actually answers the question (not just mentions a keyword)
- [ ] No valid answer chunk is missing from gold (try `uv run python -m bsa_aml.retrieval query "<question>" --mode dense`)
- [ ] Gold is not so broad that any hit counts (aim for fewer than ~10 chunks)

## Before freezing
- [ ] Rewrote 10-15 questions in your own words
- [ ] Reviewed every item flagged below
- [ ] `uv run python -m bsa_aml.evalset` reports 0 unresolved
- [ ] Recorded each question's gold section (needed to exclude them from the fine-tuning split)
- [ ] Set every `status` to `"frozen"`, then `uv run python -m bsa_aml.evaluate --label baseline`

Ranks are from the draft run (dense / BM25 / hybrid; `-` = not in top 10). Do not tune the questions to improve these.

---

### q01 · regulation · gold chunks: 1 · ranks 2 / 3 / 2

**Within how many calendar days must a bank file a SAR after it first detects facts that may constitute a basis for filing?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1020.320(b)`: …y FinCEN, as indicated in the instructions to the SAR. (3) When to file. A bank is required to file a SAR no later than 30 calendar days after the date of initial detection by the bank of facts that may constitute a basis for filing a SAR. If no suspect was identified on the date of the detection of…

---

### q02 · regulation · gold chunks: 2 · ranks 3 / - / 6

**What is the minimum dollar amount of a suspicious transaction that requires a bank to file a SAR?**

> ⚠ **Check:** gold includes a generic financial-institution advisory for a bank question

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1020.320(a)`: …e terms of this section if it is conducted or attempted by, at, or through the bank, it involves or aggregates at least $5,000 in funds or other assets, and the bank knows, suspects, or has reason to suspect that: (i) The transaction involves funds derived from illegal activities or is intended or c…
  - `FinCEN, FinCEN Advisory FIN-2019-A005 (July 16, 2019), Suspicious Activity Reporting (PDF pp. 9–10)`: … to suspect a transaction conducted or attempted by, at, or through the financial institution involves or aggregates to $5,000 or more in funds or other assets and involves funds derived from illegal activity, or attempts to disguise funds derived from illegal activity; is designed to evade regulati…

---

### q03 · regulation · gold chunks: 1 · ranks 2 / 9 / 1

**How long does a bank have to keep a copy of a filed SAR and the supporting documentation?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1020.320(d)`: … a copy of any SAR filed and the original or business record equivalent of any supporting documentation for a period of five years from the date of filing the SAR. Supporting documentation shall be identified, and maintained by the bank as such, and shall be deemed to have been filed with the SAR. A…

---

### q04 · regulation · gold chunks: 2 · ranks 2 / - / 3

**What cash amount in a single day triggers a currency transaction report?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Currency Transaction Reporting, Aggregation of Currency Transactions (PDF p. 2)`: …nsactions must be aggregated. Multiple currency transactions resulting in either cash in or cash out totaling more than $10,000 during any one business day must be treated as a single transaction, if the bank has knowledge that they are conducted by or on behalf of any person. Deposits made at night…
  - `31 CFR § 1010.311`: …ayment or transfer, by, through, or to such financial institution which involves a transaction in currency of more than $10,000, except as otherwise provided in this section. In the case of the U.S. Postal Service, the obligation contained in the preceding sentence shall not apply to payments or tra…

---

### q05 · regulation · gold chunks: 1 · ranks 3 / 5 / 3

**What two prongs define who must be identified as a beneficial owner of a legal entity customer?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1010.230(d)(1)`: … if any, who, directly or indirectly, through any contract, arrangement, understanding, relationship or otherwise, owns 25 percent or more of the equity interests of a legal entity customer; and (2) A single individual with significant responsibility to control, manage, or direct a legal entity cust…

---

### q06 · regulation · gold chunks: 2 · ranks 5 / 3 / 2

**Which identifying details must a bank collect from an individual before opening an account under its customer identification program?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1020.220(a)`: … bank must obtain, at a minimum, the following information from the customer prior to opening an account: (1) Name; (2) Date of birth, for an individual; (3) Address, which shall be: (i) For an individual, a residential or business street address;…
  - `31 CFR § 1020.220(ii)(5)`: …ach person who opens an account. What this means for you: When you open an account, we will ask for your name, address, date of birth, and other information that will allow us to identify you. We may also ask to see your driver's license or other identifying documents. (6) Reliance on another financ…

---

### q07 · regulation · gold chunks: 3 · ranks 3 / - / 6

**What minimum asset level makes an account a private banking account that needs enhanced due diligence?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1010.605(ii)(3)`: … covered financial institution that: (1) Requires a minimum aggregate deposit of funds or other assets of not less than $1,000,000; (2) Is established on behalf of or for the benefit of one or more non-U.S. persons who are direct or beneficial owners of the account; and (3) Is assigned to, or is adm…
  - `FinCEN, Application of the Regulations Requiring Special Due Diligence Programs for Certain Foreign Accounts to Certain Introduced Accounts and Give-Up Arrangements in the Futures Industries (June 07, 2006)`: …covered financial institution that . . . requires a minimum aggregate deposit of funds or other assets of not less than $1,000,000 . . . [i]s established on behalf of or for the benefit of one or more non-U.S. persons who are direct or beneficial owners of the account [and is] assigned to, or is adm…
  - `FinCEN, Application of the Regulations Requiring Special Due Diligence Programs for Certain Foreign Accounts to the Securities and Futures Industries (May 10, 2006)`: When a clearing firm does not impose aggregate minimum account requirements of not less than $1,000,000 on an introduced account for a non-U.S. person and does not assign an officer, employee, or agent to act as a liaison between the clearing firm and such an account, the introduced account will not…

---

### q08 · regulation · gold chunks: 7 · ranks 1 / 6 / 2

**What records must a financial institution keep for funds transfers of $3,000 or more?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Funds Transfers Record Keeping — Overview, Funds Transfers Recordkeeping — Overview (PDF p. 1)`: …ach bank involved in funds transfers111 to collect and retain certain information in connection with funds transfers of $3,000 or more.112 The information required to be collected and retained depends on the bank’s role in the particular funds transfer (originator’s bank, intermediary bank, or benef…
  - `FFIEC BSA/AML Examination Manual, Funds Transfers Record Keeping — Overview, Responsibilities of Originator’s Banks (PDF p. 2)`: Recordkeeping Requirements For each payment order in the amount of $3,000 or more that a bank accepts as an originator’s bank, the bank must obtain and retain the following records (31 CFR 1020.410(a)(1)(i): • Name and address of the originator. • Amount of the payment order. • Date of the payment o…
  - `FFIEC BSA/AML Examination Manual, Funds Transfers Record Keeping — Overview, Payment Orders Not Made in Person (PDF p. 3)`: …er (31 CFR 1020.410(a)(4). Records must be maintained for five years. Travel Rule Requirement For funds transmittals of $3,000 or more, the transmittor’s financial institution must include the following information in the transmittal order at the time that a transmittal order is sent to a receiving …
  - …and 4 more gold chunks

---

### q09 · regulation · gold chunks: 2 · ranks 2 / 2 / 2

**What must a bank record when it sells cashier's checks or money orders for currency between $3,000 and $10,000?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1010.415(a)`: … No financial institution may issue or sell a bank check or draft, cashier's check, money order or traveler's check for $3,000 or more in currency unless it maintains records of the following information, which must be obtained for each issuance or sale of one or more of these instruments to any ind…
  - `31 CFR § 1010.415(ii)(2)`: …e and number of driver's license). (b) Contemporaneous purchases of the same or different types of instruments totaling $3,000 or more shall be treated as one purchase. Multiple purchases during one business day totaling $3,000 or more shall be treated as one purchase if an individual employee, dire…

---

### q10 · regulation · gold chunks: 2 · ranks 3 / - / 5

**What must a financial institution do before sharing information with another institution under the voluntary information sharing provision?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1010.540(b)(2)`: (2) Notice requirement. A financial institution or association of financial institutions that intends to share information as described in paragraph (b)(1) of this section shall submit to FinCEN a notice described on FinCEN's Internet Web site, http://www.fincen.gov. Each notice provided pursuant to…
  - `31 CFR § 1010.540(b)(4)`: …uant to paragraph (b) of this section shall be protected from liability for such sharing, or for any failure to provide notice of such sharing, to an individual, entity, or organization that is identified in such sharing, to the full extent provided in subsection 314(b) of Public Law 107-56. (ii) Li…

---

### q11 · regulation · gold chunks: 5 · ranks 2 / 1 / 1

**Who must report accounts held in a foreign country, and what types of accounts count as reportable?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1010.350(a)`: (a) In general. Each United States person having a financial interest in, or signature or other authority over, a bank, securities, or other financial account in a foreign country shall report such relationship to the Commissioner of Internal Revenue for each year in which such relationship exists a…
  - `31 CFR § 1010.350(iv)`: …gn country includes all geographical areas located outside of the United States as defined in 31 CFR 1010.100(hhh). (e) Financial interest. A financial interest in a bank, securities or other financial account in a foreign country means an interest described in this paragraph (e): (1) Owner of recor…
  - `31 CFR § 1010.350(e)(2)`: …t not limited to a corporation, partnership, or trust, to be created for a purpose of evading this section shall have a financial interest in any bank, securities, or other financial account in a foreign country for which the entity is the owner of record or holder of legal title.…
  - …and 2 more gold chunks

---

### q12 · regulation · gold chunks: 1 · ranks 2 / - / 4

**What amount of currency or monetary instruments carried across the U.S. border must be reported?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1010.340(a)`: …o be physically transported, mailed or shipped, currency or other monetary instruments in an aggregate amount exceeding $10,000 at one time from the United States to any place outside the United States, or into the United States from any place outside the United States, shall make a report thereof. …

---

### q13 · regulation · gold chunks: 6 · ranks 4 / 8 / 2

**What is the SAR filing threshold for a money services business?**

> ⚠ **Check:** one added MSB-guide chunk may mention $2,000 only in passing

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1022.320(a)`: …ted or attempted by, at, or through a money services business, involves or aggregates funds or other assets of at least $2,000 (except as provided in paragraph (a)(3) of this section), and the money services business knows, suspects, or has reason to suspect that the transaction (or a pattern of tra…
  - `FinCEN, Bank Secrecy Act Requirements - A Quick Reference Guide for MSBs, Summary of BSA Requirements for MSBs (PDF p. 1)`: …reason to suspect that any transaction or activity is suspicious and it involves or aggregates funds or other assets of $2,000 or more, ($5,000 or more if identified by issuers from a review of clearance records), it must file a SAR. 1 Anti-Money Laundering (AML) compliance program – All MSBs are re…
  - `FinCEN, Bank Secrecy Act Requirements - A Quick Reference Guide for MSBs, Suspicious Activity Reporting Requirements (PDF p. 2)`: … – must report suspicious activity involving any transaction or pattern of transactions at or above a certain amount: 1 $2,000 or more; 1 $5,000 or more for issuers reviewing clearance records. You have 30 calendar days to file a SAR after becoming aware of any suspicious transaction that is require…
  - …and 3 more gold chunks

---

### q14 · regulation · gold chunks: 3 · ranks 1 / 1 / 1

**By when must a new money services business register with FinCEN?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1022.380(iii)(4)`: …he money services business must be re-registered under this section. The registration form must be filed not later than 180 days after such change in ownership, transfer of voting power or equity interests, or increase in agents. The calendar year in which the change, transfer, or increase occurs is…
  - `FinCEN, Interagency Interpretive Guidance on Providing Banking Services to Money Services Businesses Operating in the United States (guidance04262005) (April 26, 2005) (PDF p. 11)`: …he location of supporting documentation. Additionally, under existing FinCEN regulations, a money services business has 180 days in which to register from the time that it begins performing the functions that subject it to the money services business regulations.11 Therefore, it is possible that a m…
  - `FinCEN, Registration and De-Registration of Money Services Businesses (February 03, 2006)`: …usiness. Money services businesses established after December 31, 2001 are required to register initially by the end of 180 days after the day they are established as money services businesses and to renew their registrations at the end (by December 31st ) of the two-calendar year period beginning w…

---

### q15 · regulation · gold chunks: 3 · ranks 4 / - / 7

**What is the SAR dollar threshold for a casino?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1021.320(a)`: … terms of this section if it is conducted or attempted by, at, or through a casino, and involves or aggregates at least $5,000 in funds or other assets, and the casino knows, suspects, or has reason to suspect that the transaction (or a pattern of transactions of which the transaction is a part): (i…
  - `FinCEN, Suspicious Activity Reporting Guidance for Casinos (December 15, 2003) (PDF p. 5)`: …AR (SARC) for any transaction conducted or attempted by, at, or through a casino, and involving or aggregating at least $5,000 in funds or other assets, that the casino knows, suspects, or has reason to suspect: • involves funds derived from illegal activity or is intended or conducted in order to h…
  - `FinCEN, Suspicious Activity Reporting Guidance for Casinos (December 15, 2003) (PDF pp. 17–19)`: … activity – they are only required to file a SARC if they believe the activity is suspicious and involves or aggregates $5,000 or more. Urgency: If a situation seems to require immediate attention, a casino should contact the appropriate law enforcement authority immediately; then file a SARC. If a …

---

### q16 · regulation · gold chunks: 6 · ranks 4 / - / 9

**How soon after a business opens an account can the bank treat it as an exempt person for CTR purposes?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1020.315(b)(5)`: …on, that: (i) Maintains a transaction account, as defined in paragraph (e)(9) of this section, at the bank for at least two months, except as provided in paragraph (c)(2)(ii) of this section; (ii) Frequently engages in transactions in currency with the bank in excess of $10,000; and (iii) Is incorpo…
  - `31 CFR § 1020.315(ii)`: … of this section, as an exempt person before the customer has maintained a transaction account at the bank for at least two months if the bank conducts and documents a risk-based assessment of the customer and forms a reasonable belief that the customer has a legitimate business purpose for conducti…
  - `FinCEN, FinCEN Guidance (FIN-2009-G003) on Determining Eligibility for Exemption from Currency Transaction Reporting Requirements (August 31, 2009), Type of Customer Transaction Frequency Waiting Period Ineligible activity File DOEP Form Annual Review Phase I Banks operating in the U.S. N/A None N/A No No Federal, state, local, or inter- state governmental departments, agencies, or authorities N/A None N/A No No Entities listed on the major national stock exchanges N/A None N/A Yes Yes Subsidiaries (at least 51% owned) of entities listed on the major national stock exchanges N/A None N/A Yes Yes Phase II Non-listed businesses Five or more transactions per year Two months; or less after risk-based analysis No more than 50% of gross revenues derived from ineligible activity Yes Yes Payroll Customers Regularly conducts large cash withdrawals for payroll Two months; or less after risk-based analysis N/A Yes Yes (PDF pp. 3–4)`: …customer has conducted five or more transactions within the previous year, has been a customer of the bank for at least two months (or less time on a risk-assessed basis), and derives no more than 50% of its gross revenues from any ineligible business activity.9 Before treating a payroll customer as…
  - …and 3 more gold chunks

---

### q17 · regulation · gold chunks: 2 · ranks - / - / -

**Which parts of an AML program must a bank have at minimum, such as internal controls and a designated compliance person?**

> ⚠ **Check:** misses in every mode

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1020.210(a)`: …Complies with the requirements of §§ 1010.610 and 1010.620 of this chapter; (2) Includes, at a minimum: (i) A system of internal controls to assure ongoing compliance; (ii) Independent testing for compliance to be conducted by bank personnel or by an outside party; (iii) Designation of an individual…
  - `31 CFR § 1020.210(b)(2)`: (2) Includes, at a minimum: (i) A system of internal controls to assure ongoing compliance with the Bank Secrecy Act and the regulations set forth in 31 CFR Chapter X; (ii) Independent testing for compliance to be conducted by bank personnel or by an outside party; (iii) Designation of an individual…

---

### q18 · regulation · gold chunks: 3 · ranks 1 / 3 / 1

**What makes a bank a shell bank that U.S. covered institutions cannot hold correspondent accounts for?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1010.605(ii)`: …oreign exchange or a money transmitter if such transactions are merely incidental to the person's business. (g) Foreign shell bank means a foreign bank without a physical presence in any country. (h) Non-United States person or non-U.S. person means a natural person who is neither a United States ci…
  - `31 CFR § 1010.605(ii)(3)`: …he direct or beneficial owner of the account. (n) Regulated affiliate. (1) The term regulated affiliate means a foreign shell bank that: (i) Is an affiliate of a depository institution, credit union, or foreign bank that maintains a physical presence in the United States or a foreign country, as app…
  - `31 CFR § 1010.630(a)`: (a) Requirements for covered financial institutions—(1) Prohibition on correspondent accounts for foreign shell banks. (i) A covered financial institution shall not establish, maintain, administer, or manage a correspondent account in the United States for, or on behalf of, a foreign shell bank. (ii…

---

### q19 · regulation · gold chunks: 4 · ranks 6 / - / -

**How soon must a business that receives more than $10,000 in cash report it on Form 8300?**

> ⚠ **Check:** misses in every mode; '15 days' not in any top-10 chunk

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1010.330(ii)(3)`: …under this section. (ii) Exception. An agent who receives currency from a principal and uses all of the currency within 15 days in a currency transaction (the “second currency transaction”) which is reportable under section 5312 of title 31, or 31 U.S.C. 5331 and this section, and who discloses the …
  - `31 CFR § 1010.330(iii)`: …n: Example.B, the principal, gives D, an attorney, $75,000 in currency to purchase real property on behalf of B. Within 15 days D purchases real property for currency from E, a real estate developer, and discloses to E, B's name, address, and taxpayer identification number. Because the transaction q…
  - `31 CFR § 1010.330(b)(1)`: …ment in excess of $10,000. If the initial payment exceeds $10,000, the recipient must report the initial payment within 15 days of its receipt. (2) Initial payment of $10,000 or less. If the initial payment does not exceed $10,000, the recipient must aggregate the initial payment and subsequent paym…
  - …and 1 more gold chunks

---

### q20 · regulation · gold chunks: 3 · ranks - / - / -

**What does it mean to structure a transaction under the Bank Secrecy Act?**

> ⚠ **Check:** misses in every mode; definition answered poorly

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `31 CFR § 1010.100(vv)`: …, such as a card, code, electronic serial number, mobile identification number, or personal identification number. (xx) Structure (structuring). For purposes of § 1010.314, a person structures a transaction if that person, acting alone, or in conjunction with, or on behalf of, other persons, conduct…
  - `31 CFR § 1010.100(ii)`: …an that is secured by a mortgage, deed of trust, or other equivalent consensual security interest on: (A) A residential structure that contains one to four units, including, if used as a residence, an individual condominium unit, cooperative unit, mobile home or trailer; or (B) Residential real esta…
  - `31 CFR § 1010.314`: …ns in currency reporting requirements of this chapter that contains a material omission or misstatement of fact; or (c) Structure (as that term is defined in § 1010.100(xx)) or assist in structuring, or attempt to structure or assist in structuring, any transaction with one or more domestic financia…

---

### q21 · exam · gold chunks: 9 · ranks 1 / 1 / 1

**What factors do examiners look at when judging whether a bank's BSA/AML risk assessment is adequate?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, BSA/AML Risk Assessment (PDF p. 1)`: Objective: Review the bank’s BSA/AML risk assessment process, and determine whether the bank has adequately identified the ML/TF and other illicit financial activity risks within its banking operations. Examiners must develop an understanding of the bank’s ML/TF and other illicit financial activity …
  - `FFIEC BSA/AML Examination Manual, BSA/AML Risk Assessment, BSA/AML Risk Assessment Process (PDF p. 1)`: … structure their compliance programs to be risk-based. While not a specific legal requirement, a well-developed BSA/AML risk assessment assists the bank in identifying ML/TF and other illicit financial activity risks and in developing appropriate internal controls (i.e., policies, procedures, and pr…
  - `FFIEC BSA/AML Examination Manual, BSA/AML Risk Assessment, BSA/AML Risk Assessment Process (PDF pp. 1–2)`: Identification of Specific Risk Categories Generally, the first step in developing the risk assessment is to identify the bank’s risk categories. Money laundering, terrorist financing, or other illicit financial activities can occur through any number of different methods or channels. A spectrum of …
  - …and 6 more gold chunks

---

### q22 · exam · gold chunks: 6 · ranks 1 / 6 / 1

**What are the responsibilities and qualifications expected of a bank's BSA compliance officer?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Assessing the BSA/AML Compliance Program Introduction, ASSESSING THE BSA/AML COMPLIANCE PROGRAM (PDF p. 1)`: …y. • Designation of an individual or individuals responsible for coordinating and monitoring day-to-day compliance (BSA compliance officer). • Training for appropriate personnel. In addition, the BSA/AML compliance program must include a customer identification program (CIP) with risk-based procedur…
  - `FFIEC BSA/AML Examination Manual, BSA/AML Independent Testing (PDF p. 2)`: …endent testing should contain sufficient information for the reviewer (e.g., board of directors, senior management, BSA compliance officer, review auditor, or an examiner) to reach a conclusion about the overall adequacy of the BSA/AML compliance program. To contain sufficient information to reach t…
  - `FFIEC BSA/AML Examination Manual, BSA Compliance Officer (PDF p. 1)`: Objective: Confirm that the bank’s board of directors has designated a qualified individual or individuals (BSA compliance officer) responsible for coordinating and monitoring day-to-day compliance with BSA regulatory requirements. Assess whether the BSA compliance officer has the appropriate author…
  - …and 3 more gold chunks

---

### q23 · exam · gold chunks: 4 · ranks 1 / 10 / 2

**How frequently and how broadly should a bank's BSA/AML program be independently tested?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, BSA/AML Independent Testing (PDF p. 1)`: Objective: Assess the adequacy of the bank’s independent testing program. The purpose of independent testing (audit) is to assess the bank’s compliance with BSA regulatory requirements, relative to its risk profile, and assess the overall adequacy of the BSA/AML compliance program. Independent testi…
  - `FFIEC BSA/AML Examination Manual, BSA/AML Independent Testing (PDF p. 1)`: There is no regulatory requirement establishing BSA/AML independent testing frequency. Independent testing, including the frequency, should be commensurate with the ML/TF and other illicit financial activity risk profile of the bank and the bank’s overall risk management strategy. The bank may condu…
  - `FFIEC BSA/AML Examination Manual, BSA/AML Independent Testing (PDF p. 2)`: The independent testing should evaluate the overall adequacy of the bank’s BSA/AML compliance program and the bank’s compliance with BSA regulatory requirements. This evaluation helps inform the board of directors and senior management of weakness, or areas in need of enhancements or stronger contro…
  - …and 1 more gold chunks

---

### q24 · exam · gold chunks: 7 · ranks 1 / 4 / 1

**What should a good SAR narrative cover?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Appendix L: SAR Quality Guidance (PDF p. 1)`: …ents, Release Date October 2012, Version 1.2.306 FinCEN’s instructions contain a checklist as a guide for preparing the narrative. FinCEN has requested banks include certain key terms in the narrative section of the SAR. A consolidated listing of SAR narrative key terms and a link to the related adv…
  - `FFIEC BSA/AML Examination Manual, Appendix L: SAR Quality Guidance (PDF p. 1)`: … available to the filing bank obtained through the account opening process and due diligence efforts. In general, a SAR narrative should identify the five essential elements of information (who? what? when? where? and why?) for the suspicious activity being reported. The method of operation (or how?…
  - `FFIEC BSA/AML Examination Manual, Appendix L: SAR Quality Guidance, Who is conducting the suspicious activity? (PDF p. 1)`: While one section of the SAR calls for specific suspect information, the narrative should be used to further describe the suspect or suspects, including occupation, position or title within the suspect’s business, the nature of the suspect’s business (or businesses), and any other information and id…
  - …and 4 more gold chunks

---

### q25 · exam · gold chunks: 5 · ranks 1 / 2 / 1

**How should a bank handle continuing suspicious activity after it has already filed a SAR?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Suspicious Activity Reporting — Overview, SAR Section to be updated to reflect interagency Frequently Asked Questions (PDF pp. 1–2)`: …, 2021 and October 9, 2025. These FAQs are the most current guidance regarding certain SAR topics such as SAR filing on continuing activity, documentation of a decision not to file a SAR, and maintaining a customer relationship after filing a SAR. The FAQs clarify regulatory requirements related to …
  - `FFIEC BSA/AML Examination Manual, Suspicious Activity Reporting — Overview, Systems to Identify, Research, and Report Suspicious Activity (PDF pp. 3–4)`: …g system output). • Managing alerts. • SAR decision making. • SAR completion and filing. • Monitoring and SAR filing on continuing activity.…
  - `FFIEC BSA/AML Examination Manual, Suspicious Activity Reporting — Overview, Systems to Identify, Research, and Report Suspicious Activity (PDF p. 4)`: • Monitoring and SAR filing on continuing activity. These components are present in banks of all sizes. However, the structure and formality of the components may vary. Larger banks typically have greater differentiation and distinction between functions, and may devote entire departments to the com…
  - …and 2 more gold chunks

---

### q26 · exam · gold chunks: 1 · ranks 1 / 5 / 2

**Under what conditions can a bank rely on another financial institution to perform parts of its customer identification program?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Customer Identification Program, Reliance on Another Financial Institution (PDF pp. 7–8)`: The bank’s CIP may include procedures specifying when a bank will rely on the performance by another financial institution (including an affiliate) of any procedures of the bank’s CIP with respect to any customer of the bank that is opening, or has opened, an account or has established a similar for…

---

### q27 · exam · gold chunks: 5 · ranks 1 / 3 / 1

**What does ongoing monitoring mean as part of customer due diligence?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Customer Due Diligence — Overview, Customer Due Diligence (PDF pp. 1–2)`: …he nature and purpose of customer relationships for the purpose of developing a customer risk profile; and • Conducting ongoing monitoring to identify and report suspicious transactions and, on a risk basis, to maintain and update customer information, including information 1 Department of the Treas…
  - `FFIEC BSA/AML Examination Manual, Customer Due Diligence — Overview, Customer Information – Risk-Based Procedures (PDF p. 3)`: …ccount. Customer information collected under CDD requirements for the purpose of developing a customer risk profile and ongoing monitoring to identify and report suspicious transactions and, on a risk basis, to maintain and update customer information, includes beneficial ownership information for l…
  - `FFIEC BSA/AML Examination Manual, Customer Due Diligence — Overview, Customer Information – Risk-Based Procedures (PDF pp. 5–6)`: …ence procedures must ensure compliance with these existing requirements and should meet these supervisory expectations. Ongoing Monitoring of the Customer Relationship The requirement for ongoing monitoring of the customer relationship reflects existing practices established to identify and report s…
  - …and 2 more gold chunks

---

### q28 · exam · gold chunks: 3 · ranks 1 / 1 / 1

**How should a bank treat the risk of customers who are politically exposed persons?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Nonresident Aliens and Foreign Individuals — Overview, Risk Mitigation (PDF p. 2)`: …t maintain due diligence procedures for private banking accounts for non-U.S. persons, including those held for PEPs or senior foreign political figures. Refer to the core overview and examination procedures, “Private Banking Due Diligence Program (Non-U.S. Persons),” pages 125 and 130, respectively…
  - `FFIEC BSA/AML Examination Manual, Politically Exposed Persons (PDF p. 1)`: …SA/AML) regulations do not define the term Politically Exposed Person (PEP),1 and the term should not be confused with “senior foreign political figure” (SFPF), a subset of PEP.2 The term PEP is commonly used in the financial industry to refer to foreign individuals who are or have been entrusted wi…
  - `FFIEC BSA/AML Examination Manual, Politically Exposed Persons, Risk Factors (PDF p. 1)`: …e diligence programs for private banking accounts); see also “FinCEN Advisory on Human Rights Abuses Enabled by Corrupt Senior Foreign Political Figures and their Financial Facilitators,” (June 2018). Specific to SFPFs, refer to the Private Banking Due Diligence Program (non- U.S. Persons) section f…

---

### q29 · exam · gold chunks: 6 · ranks 7 / - / -

**What transaction patterns are red flags for structuring?**

> ⚠ **Check:** misses in every mode

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Appendix F: Money Laundering and Terrorist Financing “Red Flags”, Potentially Suspicious Activity That May Indicate Money Laundering (PDF pp. 2–3)`: … a transaction involving a large withdrawal of currency, or accesses a safe deposit box before making currency deposits structured at or just under $10,000, to evade CTR filing requirements. Funds Transfers • Many funds transfers are sent in large, round dollar, hundred dollar, or thousand dollar am…
  - `FFIEC BSA/AML Examination Manual, Appendix F: Money Laundering and Terrorist Financing “Red Flags”, Potentially Suspicious Activity That May Indicate Money Laundering (PDF pp. 5–6)`: …ing of goods and services. • Obvious misrepresentation of quantity or type of goods imported or exported. • Transaction structure appears unnecessarily complex and designed to obscure the true nature of the transaction. • Customer requests payment of proceeds to an unrelated third party. • Shipment …
  - `FFIEC BSA/AML Examination Manual, Appendix F: Money Laundering and Terrorist Financing “Red Flags”, Potentially Suspicious Activity That May Indicate Money Laundering (PDF pp. 7–8)`: …ious movements of funds occur from one bank to another, and then funds are moved back to the first bank. • Deposits are structured through multiple branches of the same bank or by groups of people who enter a single branch at the same time. • Currency is deposited or withdrawn in amounts just below …
  - …and 3 more gold chunks

---

### q30 · exam · gold chunks: 3 · ranks 1 / 4 / 2

**What money laundering risks come with prepaid access products?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Prepaid Access — Overview, Risk Factors (PDF pp. 3–4)`: Prepaid access programs are extremely diverse in the range of products and services offered and the customer bases they serve. In evaluating the risk profile of a prepaid access program, banks should consider the program’s specific features and functionalities. Higher potential money laundering risk…
  - `FFIEC BSA/AML Examination Manual, Prepaid Access — Overview, Risk Mitigation (PDF pp. 4–5)`: Banks that offer prepaid access or otherwise participate in prepaid access programs should have policies, procedures, and processes sufficient to manage the related BSA/AML risks as required under the BSA and implementing regulations, as well as under payment network rules. Guidance provided by the …
  - `FFIEC BSA/AML Examination Manual, Nonbank Financial Institutions — Overview, Providing Banking Services to Money Services Businesses (PDF pp. 4–5)`: 284 Frequently Asked Questions Final Rule-Definitions and Other Regulations Relating to Prepaid Access (11/2/2011). used and accepted as a medium of exchange in the country of issuance.” In contrast, “virtual” currency is a medium of exchange that operates like a currency in some environments, but d…

---

### q31 · exam · gold chunks: 10 · ranks 1 / 1 / 1

**What makes third-party payment processors risky and how should a bank manage that risk?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Electronic Banking — Overview, Remote Deposit Capture (PDF p. 2)`: …omers may be defined by industry, incidence of fraud, or other criteria. Examples of higher-risk parties include online payment processors, certain credit-repair services, certain mail order and telephone order companies, online gambling operations, businesses located offshore, and adult entertainme…
  - `FFIEC BSA/AML Examination Manual, Automated Clearing House Transactions — Overview, Third-Party Service Providers (PDF pp. 4–5)`: …d. 213 Third-party service provider is a generic term for any business that provides services to a bank. A third- party payment processor is a specific type of service provider that processes payments such as checks, ACH files, or credit and debit card messages or files. Refer to expanded overview s…
  - `FFIEC BSA/AML Examination Manual, Automated Clearing House Transactions — Overview, Risk Mitigation (PDF pp. 6–7)`: …. In processing IATs, banks should consider the following: • Customers and transactions types and volume. • Third-party payment processor relationships. • Responsibilities, obligations, and risks of becoming a Gateway. • CIP, CDD, and EDD standards and practices. • Suspicious activity monitoring and…
  - …and 7 more gold chunks

---

### q32 · exam · gold chunks: 18 · ranks 1 / 2 / 1

**What due diligence is expected for correspondent accounts held for foreign financial institutions?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Customer Due Diligence — Overview, Customer Information – Risk-Based Procedures (PDF p. 5)`: … diligence and, in some cases, enhanced due diligence requirements for certain accounts or customers, including foreign correspondent accounts,6 payable-through 6 See 31 CFR 1010.610.…
  - `FFIEC BSA/AML Examination Manual, Due Diligence Programs for Correspondent Accounts for Foreign Financial Institutions (PDF p. 1)`: …sess the bank’s compliance with the Bank Secrecy Act (BSA) regulatory requirements regarding due diligence programs for correspondent accounts established, maintained, administered, or managed for foreign financial institutions, to detect and report money laundering and any potential suspicious acti…
  - `FFIEC BSA/AML Examination Manual, Due Diligence Programs for Correspondent Accounts for Foreign Financial Institutions, Regulatory Requirements for Due Diligence Programs for Correspondent Accounts for Foreign Financial Institutions (PDF p. 1)`: …his section outlines the regulatory requirements for banks in 31 CFR Chapter X regarding due diligence requirements for correspondent accounts established, maintained, administered, or managed by U.S. banks for foreign financial institutions. Specifically, this section covers: • 31 CFR 1010.60 (Defi…
  - …and 15 more gold chunks

---

### q33 · exam · gold chunks: 9 · ranks 1 / 1 / 1

**What elements should an OFAC compliance program include?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Office of Foreign Assets Control — Overview (PDF p. 1)`: Objective. Assess the bank’s risk-based Office of Foreign Assets Control (OFAC) compliance program to evaluate whether it is appropriate for the bank’s OFAC risk, taking into consideration its products, services, customers, entities, transactions, and geographic locations. OFAC is an office of the U…
  - `FFIEC BSA/AML Examination Manual, Office of Foreign Assets Control — Overview (PDF pp. 1–2)`: … aliens regardless of where they are located, all persons and entities within the United States, all U.S. evaluate OFAC compliance programs to ensure that all banks subject to their supervision comply with the sanctions.152 Unlike the BSA, the laws and OFAC-issued regulations apply not only to U.S. …
  - `FFIEC BSA/AML Examination Manual, Office of Foreign Assets Control — Overview, OFAC Compliance Program (PDF pp. 4–5)`: …tigate the risk of noncompliance with OFAC requirements, banks should establish and maintain an effective, written OFAC compliance program that is commensurate with their OFAC risk profile (based on products, services, customers, and geographic locations). The program should identify higher-risk are…
  - …and 6 more gold chunks

---

### q34 · exam · gold chunks: 7 · ranks 1 / 2 / 1

**Why is trade finance considered higher risk for money laundering?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Lending Activities — Overview (PDF p. 1)`: …e due diligence, monitoring, and reporting systems. Lending activities include, but are not limited to, real estate,240 trade finance,241 cash-secured, credit card, consumer, commercial, and agricultural. Lending activities can include multiple parties (e.g., guarantors, signatories, principals, or …
  - `FFIEC BSA/AML Examination Manual, Lending Activities — Overview, Risk Mitigation (PDF p. 1)`: …s well as money laundering through commercial and residential real estate. 241 Refer to the expanded overview section, “Trade Finance Activities,” page 267, for additional guidance.…
  - `FFIEC BSA/AML Examination Manual, Trade Finance Activities — Overview (PDF p. 1)`: Objective. Assess the adequacy of the bank’s systems to manage the risks associated with trade finance activities, and management’s ability to implement effective due diligence, monitoring, and reporting systems. Trade finance typically involves short-term financing to facilitate the import and expo…
  - …and 4 more gold chunks

---

### q35 · exam · gold chunks: 4 · ranks 1 / 1 / 1

**How should a bank manage the risk of cash-intensive businesses?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Independent Automated Teller Machine Owners or Operators, Risk Factors (PDF p. 2)`: …nship, such as transaction volume, locations of the ATMs, and the source of funds to replenish the ATMs. Because of the cash-intensive nature of an ATM, the source of funds used to replenish the ATM is a key risk factor. Independent ATM owners or operators that fund their ATM replenishment solely wi…
  - `FFIEC BSA/AML Examination Manual, Cash-Intensive Businesses — Overview (PDF p. 1)`: Objective. Assess the adequacy of the bank’s systems to manage the risks associated with cash-intensive businesses and entities, and management’s ability to implement effective due diligence, monitoring, and reporting systems. Cash-intensive businesses and entities cover various industry sectors. Mo…
  - `FFIEC BSA/AML Examination Manual, Cash-Intensive Businesses — Overview, Risk Factors (PDF p. 1)`: …and entities may be misused by money launderers to legitimize their illicit proceeds. For example, a criminal may own a cash-intensive business, such as a restaurant, and use it to launder currency from illicit criminal activities. The restaurant’s currency deposits with its bank do not, on the surf…
  - …and 1 more gold chunks

---

### q36 · exam · gold chunks: 1 · ranks 6 / 3 / 3

**What heightens money laundering or terrorist financing risk for charities and nonprofits?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Charities and Nonprofit Organizations, CHARITIES AND NONPROFIT ORGANIZATIONS (PDF p. 1)`: …s, and processes to assess, manage, and mitigate potential risks associated with customers that are charities and other nonprofit organizations (NPOs). Evaluate the bank’s compliance with regulatory requirements such as customer identification, customer due diligence (CDD), beneficial ownership of l…

---

### q37 · exam · gold chunks: 8 · ranks 1 / 7 / 1

**How do examiners use the bank's risk assessment to decide the scope of an exam?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Scoping and Planning Introduction, SCOPING AND PLANNING (PDF pp. 1–2)`: The scoping and planning process generally begins with a review of the bank’s BSA/AML risk assessment, independent testing (audit), analyses and conclusions from previous examinations, other information available through offsite and ongoing monitoring processes, and request letter items received fro…
  - `FFIEC BSA/AML Examination Manual, Scoping and Planning Introduction, SCOPING AND PLANNING (PDF p. 2)`: … apparent OFAC violations.3 If OFAC compliance will be part of the review, examiners should also review the bank’s OFAC risk assessment and related independent testing to determine the appropriate scope of the review. Refer to the Office of Foreign Assets Control section for more information. 3 OFAC…
  - `FFIEC BSA/AML Examination Manual, Risk-Focused BSA/AML Supervision (PDF p. 1)`: …ile, examiners should consider available information including, but not limited to, the following: • The bank’s BSA/AML risk assessment. • Independent testing or audits. • Analyses and conclusions from previous examinations. • Management’s responses, including the current status of issues, regarding…
  - …and 5 more gold chunks

---

### q38 · exam · gold chunks: 5 · ranks 1 / 5 / 1

**What factors determine which enforcement action is appropriate when a bank's BSA/AML program is deficient?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Appendix R: Enforcement Guidance, Joint Statement on Enforcement of Bank Secrecy Act/Anti-Money Laundering Requirements1 (PDF p. 1)`: …agency statement also describes the circumstances in which an Agency may use its discretion to issue formal or informal enforcement actions or use other supervisory actions to address BSA-related violations or unsafe or unsound banking practices or other deficiencies. This statement does not create …
  - `FFIEC BSA/AML Examination Manual, Appendix R: Enforcement Guidance, I. Background. (PDF p. 1)`: …ntain procedures reasonably designed to assure and monitor the 1 This statement supersedes the Interagency Statement on Enforcement of BSA/AML Requirements issued by the Agencies in July 2007 and is intended to set forth general policy guidance. It does not compel or preclude an enforcement or other…
  - `FFIEC BSA/AML Examination Manual, Appendix R: Enforcement Guidance, Failure to establish and maintain a reasonably designed BSA/AML Compliance Program. (PDF p. 4)`: …her required BSA reports. 10 The examples in this document do not in any way limit the ability of an Agency to bring an enforcement action under sections 8(s) and 206(q) where the failure to have or implement a BSA/AML compliance program is demonstrated by other deficiencies. The examples are includ…
  - …and 2 more gold chunks

---

### q39 · exam · gold chunks: 3 · ranks 1 / - / 1

**How long must different categories of BSA records be retained?**

> ⚠ **Check:** untouched in the review; confirm this is the retention chunk

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FFIEC BSA/AML Examination Manual, Appendix P: BSA Record Retention Requirements, Five-Year Retention for Records as Specified Below (PDF pp. 1–2)`: … document a bank’s compliance with the BSA. In general, the BSA requires that a bank maintain most records for at least five years. These records can be maintained in many forms including original, microfilm, electronic, copy, or a reproduction. A bank is not required to keep a separate system of re…
  - `FFIEC BSA/AML Examination Manual, Appendix P: BSA Record Retention Requirements, Five-Year Retention for Records as Specified Below (PDF pp. 4–5)`: … record of any SAR filed and the original or business record equivalent of any supporting documentation for a period of five years from the date of filing. Currency Transaction Report A bank must maintain a record of all Currency Transaction Reports (CTR) for a period of five years from the date of …
  - `FFIEC BSA/AML Examination Manual, Appendix P: BSA Record Retention Requirements, Five-Year Retention for Records as Specified Below (PDF p. 5)`: …g the identifying information obtained. A bank must retain the identifying information about a customer for a period of five years after the date the account is closed, or in the case of credit card accounts, five years after the account becomes closed or dormant. A bank must retain the information …

---

### q40 · guidance · gold chunks: 9 · ranks 2 / 2 / 1

**What does FinCEN expect from banks that serve marijuana-related businesses when filing SARs?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FinCEN, BSA Expectations Regarding Marijuana-Related Businesses (February 14, 2014), Guidance FIN-2014-G001 Issued: February 14, 2014 Subject: BSA Expectations Regarding Marijuana-Related Businesses (PDF p. 3)`: The obligation to file a SAR is unaffected by any state law that legalizes marijuana-related activity. A financial institution is required to file a SAR if, consistent with FinCEN regulations, the financial institution knows, suspects, or has reason to suspect that a transaction conducted or attempt…
  - `FinCEN, BSA Expectations Regarding Marijuana-Related Businesses (February 14, 2014), Guidance FIN-2014-G001 Issued: February 14, 2014 Subject: BSA Expectations Regarding Marijuana-Related Businesses (PDF p. 4)`: …elated parties; (iii) the fact that the filing institution is filing the SAR solely because the subject is engaged in a marijuana-related business; and (iv) the fact that no additional suspicious activity has been identified. Financial institutions should use the term “MARIJUANA LIMITED” in the narr…
  - `FinCEN, BSA Expectations Regarding Marijuana-Related Businesses (February 14, 2014), Guidance FIN-2014-G001 Issued: February 14, 2014 Subject: BSA Expectations Regarding Marijuana-Related Businesses (PDF p. 4)`: Financial institutions should use the term “MARIJUANA PRIORITY” in the narrative section to help law enforcement distinguish these SARs.7 “Marijuana Termination” SAR Filings If a financial institution deems it necessary to terminate a relationship with a marijuana-related business in order to mainta…
  - …and 6 more gold chunks

---

### q41 · guidance · gold chunks: 14 · ranks 1 / 1 / 1

**How do FinCEN's regulations apply to administrators and exchangers of convertible virtual currency?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FinCEN, Application of FinCEN’s Regulations to Persons Administering, Exchanging, or Using Virtual Currencies (March 18, 2013) (PDF p. 1)`: … exchanging, accepting, or transmitting virtual currencies.1 Such persons are referred to in this guidance as “users,” “administrators,” and “exchangers,” all as defined below.2 A user of virtual currency is not an MSB under FinCEN’s regulations and therefore is not subject to MSB registration, repo…
  - `FinCEN, Application of FinCEN’s Regulations to Persons Administering, Exchanging, or Using Virtual Currencies (March 18, 2013), Background (PDF p. 2)`: …atment under these definitions of persons engaged in virtual currency transactions. Definitions of User, Exchanger, and Administrator This guidance refers to the participants in generic virtual currency arrangements, using the terms “user,” “exchanger,” and “administrator.”6 A user is a person that …
  - `FinCEN, Application of FinCEN’s Regulations to Persons Administering, Exchanging, or Using Virtual Currencies (March 18, 2013), Background (PDF pp. 2–3)`: … such as systematic over- or under-invoicing or inflated transaction fees or commissions. 9 31 CFR § 1010.100(ff)(1-7). Administrators and Exchangers of Virtual Currency An administrator or exchanger that (1) accepts and transmits a convertible virtual currency or (2) buys or sells convertible virtu…
  - …and 11 more gold chunks

---

### q42 · guidance · gold chunks: 4 · ranks 4 / - / 7

**Do banks have to update beneficial ownership information for existing customers on a regular schedule?**

> ⚠ **Check:** only 4 gold chunks; check 'Question 26: Foreign financial institutions' belongs

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FinCEN, Frequently Asked Questions Regarding Customer Due Diligence Requirements for Financial Institutions (April 03, 2018), Question 7: Identification and verification: Existing customers as beneficial owners of new legal entity customer accounts (PDF p. 6)`: If an individual named as a beneficial owner of a new legal entity account is an existing customer of the covered financial institution subject to the financial institution’s CIP, is a covered financial institution still required to identify and verify the identity of this individual, or may it rely…
  - `FinCEN, Frequently Asked Questions Regarding Customer Due Diligence Requirements for Financial Institutions (April 03, 2018), Question 12: Collection of beneficial ownership information: Product or service renewals (PDF p. 9)`: Are financial institutions required to have their legal entity customers certify the beneficial owners for existing customers during the course of a financial product renewal (e.g., a loan renewal or certificate of deposit)? A. Yes. Consistent with the definition of “account” in the CIP rules and su…
  - `FinCEN, Frequently Asked Questions Regarding Customer Due Diligence Requirements for Financial Institutions (April 03, 2018), Question 12: Collection of beneficial ownership information: Product or service renewals (PDF p. 9)`: …t, meaning (in the case of a bank) for each new formal banking relationship established, even if the legal entity is an existing customer. For financial services or products established before May 11, 2018, covered financial institutions must obtain certified beneficial ownership information of the …
  - …and 1 more gold chunks

---

### q43 · guidance · gold chunks: 7 · ranks 2 / 2 / 2

**May a bank share a SAR with its parent or affiliates?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FinCEN, Guidance on Sharing of Suspicious Activity Reports by Securities Broker-Dealers, Futures Commission Merchants, and Introducing Brokers in Commodities (January 20, 2006), January 20, 2006 Guidance on Sharing of Suspicious Activity Reports by Securities Broker-Dealers, Futures Commission Merchants, and Introducing Brokers in Commodities (PDF p. 2)`: …ealer, futures commission merchant, or introducing broker in commodities may share a Suspicious Activity Report with an affiliate other than its parent entities, both in instances where the affiliate is located inside the United States and where the affiliate is located abroad. We expect to issue gu…
  - `FinCEN, Guidance on Sharing of Suspicious Activity Reports by Securities Broker-Dealers, Futures Commission Merchants, and Introducing Brokers in Commodities (January 20, 2006)`: …ealer, futures commission merchant, or introducing broker in commodities may share a Suspicious Activity Report with an affiliate other than its parent entities, both in instances where the affiliate is located inside the United States and where the affiliate is located abroad. We expect to issue gu…
  - `FinCEN, Sharing Suspicious Activity Reports by Securities Broker-Dealers, Mutual Funds, Futures Commission Merchants, and Introducing Brokers in Commodities with Certain U.S. Affiliates (November 23, 2010)`: …r which a securities broker-dealer, mutual fund, futures commission merchant, or introducing broker in commodities, its affiliate, or both entities would be liable for direct or indirect disclosure by the affiliate of a SAR or any information that would reveal the existence of a SAR. Therefore, the …
  - …and 4 more gold chunks

---

### q44 · guidance · gold chunks: 4 · ranks - / 6 / -

**Who counts as a provider of prepaid access under FinCEN's final rule?**

> ⚠ **Check:** misses in every mode

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FinCEN, Frequently Asked Questions regarding Prepaid Access (March 24, 2016), Frequently Asked Questions (FAQs) (PDF pp. 4–5)`: …embers of the organization. Question 5: Listing sellers of prepaid access on the provider’s MSB agent list Q: When is a provider of prepaid access required to list on its MSB agent list an entity that sells the provider’s prepaid product? A: A seller of prepaid access is defined in the regulation as…
  - `FinCEN, Frequently Asked Questions regarding Prepaid Access (March 24, 2016), Frequently Asked Questions (FAQs) (PDF p. 5)`: …h a sale.7 If an entity that sells a provider’s prepaid product meets the definition of "seller of prepaid access," the provider of prepaid access is required to list that entity on its MSB agent list. If an entity does not meet the definition of "seller of prepaid access," the provider of prepaid a…
  - `FinCEN, Frequently Asked Questions regarding Prepaid Access (March 24, 2016)`: …mbers of the organization. Question 5: Listing sellers of prepaid access on the provider’s MSB agent list Q : When is a provider of prepaid access required to list on its MSB agent list an entity that sells the provider’s prepaid product? A : A seller of prepaid access is defined in the regulation a…
  - …and 1 more gold chunks

---

### q45 · guidance · gold chunks: 8 · ranks 1 / 1 / 1

**What information must travel with a funds transfer under the travel rule?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FinCEN, Funds “Travel” Regulations: Questions & Answers (November 09, 2010), Guidance (PDF p. 1)`: FIN-2010-G004 Issued: November 9, 2010 Subject: Funds “Travel” Regulations: Questions & Answers The following is revised guidance to financial institutions on the transmittal of funds "Travel" rule. This guidance updates the document “Funds ‘Travel’ Regulations: Questions & Answers” issued in 1997. …
  - `FinCEN, Funds “Travel” Regulations: Questions & Answers (November 09, 2010), Guidance (PDF p. 2)`: An intermediary financial institution may receive supplementary information about a payment beyond the information the travel rule requires to be sent to the next financial institution in the payment chain. For example, a payment order may contain additional information about the payment or the part…
  - `FinCEN, Funds “Travel” Regulations: Questions & Answers (November 09, 2010), Guidance (PDF p. 2)`: Intermediary financial institutions in receipt of additional information not required by the travel rule should note that, while compliance with the travel rule is accomplished by inclusion of the information identified in the rule, other monitoring and reporting requirements may apply to additional…
  - …and 5 more gold chunks

---

### q46 · guidance · gold chunks: 8 · ranks 1 / 1 / 1

**Does a casino have to aggregate cash transactions across different gaming areas for CTR purposes?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FinCEN, Frequently Asked Questions Casino Record keeping, Reporting, and Compliance Program Requirements (September 30, 2009)`: …cy Transaction Reporting RequirementsQuestion 3: What is the definition of a gaming day and what effect does it have on aggregating a customer’s reportable currency transactions?…
  - `FinCEN, Frequently Asked Questions Casino Record keeping, Reporting, and Compliance Program Requirements (September 30, 2009)`: …day, which is common to all its gambling operating divisions or departments. Maintaining one gaming day facilitates the aggregation of transactions for purposes of currency transaction reporting.Question 4: Is a card club required to file FinCEN Form 103, Currency Transaction Report by Casinos ("CTR…
  - `FinCEN, Frequently Asked Questions Casino Record keeping, Reporting, and Compliance Program Requirements (September 30, 2009)`: Question 6: To what extent is a casino required to aggregate credit card advances with other types of cash out transactions for currency transaction reporting purposes? Answer 6: A casino is required to file a CTRC on currency transactions by or on behalf of any customer that, alone or when aggregat…
  - …and 5 more gold chunks

---

### q47 · guidance · gold chunks: 8 · ranks 1 / 1 / 1

**Do SAR safe harbor protections hold up when a customer sues the bank?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FinCEN, Federal Court Reaffirms Protections For Financial Institutions Filing Suspicious Activity Reports (May 24, 2004), Interagency Advisory FEDERAL COURT REAFFIRMS PROTECTIONS FOR FINANCIAL INSTITUTIONS FILING SUSPICIOUS ACTIVITY REPORTS (PDF p. 1)`: …306 F. Supp.2d 678 (S.D. Tex. 2004), that reaffirms the scope of that statutory protection, generally referred to as a “safe harbor.” In 1992, Congress passed the Annunzio-Wylie Anti-Money Laundering Act and provided a safe harbor for financial institutions and their employees from civil liability f…
  - `FinCEN, Federal Court Reaffirms Protections For Financial Institutions Filing Suspicious Activity Reports (May 24, 2004), Interagency Advisory FEDERAL COURT REAFFIRMS PROTECTIONS FOR FINANCIAL INSTITUTIONS FILING SUSPICIOUS ACTIVITY REPORTS (PDF pp. 1–2)`: Some courts have limited the safe harbor protection to disclosures based on a good faith belief that a violation has occurred, or have declined to extend the protection to financial institutions that may have misrepresented material facts to law enforcement.1 However, the majority of courts have rul…
  - `FinCEN, Federal Court Reaffirms Protections For Financial Institutions Filing Suspicious Activity Reports (May 24, 2004), Interagency Advisory FEDERAL COURT REAFFIRMS PROTECTIONS FOR FINANCIAL INSTITUTIONS FILING SUSPICIOUS ACTIVITY REPORTS (PDF p. 2)`: …ty for filing a SAR.2 The federal district court in Whitney sided with the majority of courts that have interpreted the safe harbor provision to afford unqualified protection to financial institutions and their employees from civil suit. In the Whitney case, individuals filed a defamation suit again…
  - …and 5 more gold chunks

---

### q48 · guidance · gold chunks: 4 · ranks 2 / - / 5

**What AML program obligations apply to dealers in precious metals, stones, or jewels?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FinCEN, Guidance for Dealers, Including Certain Retailers, of Precious Metals, Precious Stones, or Jewels, on Conducting a Risk Assessment of Their Foreign Suppliers (March 10, 2008)`: …ssessment required to be performed under the Interim Final Rule requiring anti-money laundering programs for dealers in precious metals, precious stones, or jewels ("Interim Final Rule"). 1 Specifically, this guidance will assist dealers, 2 including certain retailers, 3 in tailoring their anti-mone…
  - `FinCEN, Guidance for Dealers, Including Certain Retailers, of Precious Metals, Precious Stones, or Jewels, on Conducting a Risk Assessment of Their Foreign Suppliers (March 10, 2008)`: …oney laundering and terrorist financing. FinCEN acknowledges that there is no single agreed upon method to regulate the precious metals, precious stones and jewels industry, and other jurisdictions have taken different regulatory approaches to shield their industries from money launderers and terror…
  - `FinCEN, Guidance for Dealers, Including Certain Retailers, of Precious Metals, Precious Stones, or Jewels, on Conducting a Risk Assessment of Their Foreign Suppliers (March 10, 2008)`: …d terrorist financiers entrance into, or exploitation of, the industry. After reviewing the specific risks of their own precious metals, precious stones, and jewels industry, some jurisdictions have determined a need to issue regulations that impose requirements or place limitations on who may obtai…
  - …and 1 more gold chunks

---

### q49 · guidance · gold chunks: 1 · ranks 1 / 7 / 3

**What red flags indicate an e-mail compromise fraud scheme?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FinCEN, Advisory to Financial Institutions on E-mail Compromise Fraud Schemes (September 06, 2016)`: …icious behavior, which can be identified by one or more of the following red flags: • A customer’s seemingly legitimate e-mailed transaction instructions contain different language, timing, and amounts than previously verified and authentic transaction instructions. • john-doe@abc.com • john_doe@abc…

---

### q50 · guidance · gold chunks: 7 · ranks 3 / 1 / 2

**How should a bank fix errors in a batch of SARs it already filed electronically?**

- [ ] wording  - [ ] answerable  - [ ] gold answers it  - [ ] nothing missing  - [ ] not too broad

  - `FinCEN, FIN-2009-G005 - Requirements for Correcting Errors in Electronically Batch-Filed Suspicious Activity Reports (December 10, 2009) (PDF p. 1)`: …005 Issued: December 10, 2009 (Amended December 14, 2009) Subject: Requirements for Correcting Errors in Electronically Batch-Filed Suspicious Activity Reports The Financial Crimes Enforcement Network (FinCEN) is issuing these guidelines to assist users of the Bank Secrecy Act (BSA) E-Filing System …
  - `FinCEN, FIN-2009-G005 - Requirements for Correcting Errors in Electronically Batch-Filed Suspicious Activity Reports (December 10, 2009) (PDF p. 1)`: The following guidelines provide batch filers with the requirements for correcting errors identified in submitted batch files and preventing errors in future submissions. 1 For purposes of this document, “SAR” collectively refers to the Suspicious Activity Report by Casinos and Card Clubs (SAR-C), t…
  - `FinCEN, FIN-2009-G005 - Requirements for Correcting Errors in Electronically Batch-Filed Suspicious Activity Reports (December 10, 2009) (PDF pp. 2–3)`: … the primary and secondary errors for each SAR form. Appendix A: Guidelines for Correcting Errors in the Electronically-Batch Filed Suspicious Activity Report by Casinos and Card Clubs, FinCEN Form 102. Appendix B: Guidelines for Correcting Errors in Electronically-Batch Filed Suspicious Activity Re…
  - …and 4 more gold chunks

---
