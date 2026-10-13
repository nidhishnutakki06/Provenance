"""Sample raw corpus generator for Dev 2 fixtures.

Generates sample documents following Section 5.4 raw corpus contracts
and Section 6.2/6.3 specifications for Novacure Labs:
- SOPs (PDF via ReportLab): SOP-014-v2 (superseded), SOP-014-v3, SOP-021, SOP-001
- Other PDFs (PDF via ReportLab): REG-001
- SharePoint (.docx via python-docx): QM-001, AUD-001 (manager-only), ONB-001
- Email (.eml): EML-001, EML-002
- Teams (.json): TEAMS-COLDCHAIN, TEAMS-QAHELP

Includes exact fixed sentences from Section 6.3 and mentions of Priya Rao.
"""

from __future__ import annotations

import json
from email.message import EmailMessage
from pathlib import Path

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def create_pdf(path: Path, title: str, pages_text: list[list[str]]) -> None:
    """Generate a multi-page PDF with real extractable text using reportlab."""
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter

    for page_idx, paragraphs in enumerate(pages_text):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(54, height - 54, f"{title} - Page {page_idx + 1}")
        c.setFont("Helvetica", 10)
        y = height - 80
        for para in paragraphs:
            # Simple text wrap
            words = para.split()
            line = []
            for word in words:
                line.append(word)
                if len(" ".join(line)) > 75:
                    c.drawString(54, y, " ".join(line[:-1]))
                    y -= 14
                    line = [word]
                    if y < 54:
                        break
            if line and y >= 54:
                c.drawString(54, y, " ".join(line))
                y -= 18
            if y < 54:
                break
        c.showPage()
    c.save()


def create_docx(path: Path, title: str, sections: list[tuple[str, list[str]]]) -> None:
    """Generate a docx file with headings and paragraphs using python-docx."""
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    doc.add_heading(title, level=0)
    for heading, paragraphs in sections:
        doc.add_heading(heading, level=1)
        for p in paragraphs:
            doc.add_paragraph(p)
    doc.save(str(path))


def create_eml(path: Path, from_addr: str, to_addr: str, subject: str, date_str: str, body: str) -> None:
    """Generate an .eml email file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg["Date"] = date_str
    msg.set_content(body)
    with open(path, "wb") as f:
        f.write(msg.as_bytes())


def create_teams_json(path: Path, messages: list[dict]) -> None:
    """Generate a Teams channel JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)


def write_sidecar(path: Path, meta: dict) -> None:
    """Write the <file>.meta.json sidecar."""
    sidecar_path = path.parent / f"{path.name}.meta.json"
    with open(sidecar_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def generate_all_samples(target_dir: Path) -> None:
    """Generate all sample files and sidecars into target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. SOP-014-v2 (sop/.pdf) - superseded
    sop_014_v2_path = target_dir / "sop" / "SOP-014-v2.pdf"
    create_pdf(
        sop_014_v2_path,
        "SOP-014 Cold-Chain Storage v2",
        [
            [
                "Section 1. Purpose and Scope: This standard operating procedure defines storage protocols for cold-chain biological products at Novacure Labs facilities.",
                "Vaccine batches must be stored at 2 to 8 °C.",
                "Storage units are monitored continuously using calibrated temperature probes. Arjun Menon manages the warehouse temperature monitoring logging system.",
            ],
            [
                "Section 2. Temperature Excursion Management:",
                "Temperature excursions of up to 12 hours do not require a deviation report.",
                "Warehouse staff shall log minor excursions in the auxiliary shift log without initiating immediate quarantine.",
            ],
        ],
    )
    write_sidecar(
        sop_014_v2_path,
        {
            "doc_id": "SOP-014-v2",
            "title": "SOP-014 Cold-Chain Storage v2",
            "source_type": "sop",
            "version": "2.0",
            "date": "2024-11-05",
            "author": "Arjun Menon",
            "owner": "Arjun Menon",
            "status": "superseded",
            "supersedes": None,
            "allowed_roles": ["analyst", "manager"],
            "topics": ["cold-chain", "storage-temperature"],
        },
    )

    # 2. SOP-014-v3 (sop/.pdf) - current
    sop_014_v3_path = target_dir / "sop" / "SOP-014-v3.pdf"
    create_pdf(
        sop_014_v3_path,
        "SOP-014 Cold-Chain Storage v3",
        [
            [
                "Section 1. Purpose and Storage Temperature Requirements:",
                "Vaccine batches must be stored at 2 to 8 °C.",
                "All cold rooms and reach-in freezers must maintain active temperature recording systems verified daily by Arjun Menon.",
            ],
            [
                "Section 2. Deviation Escalation Protocol:",
                "Any temperature excursion longer than 4 hours requires a deviation report.",
                "Priya Rao, QA Lead, owns deviation management and must be informed of cold-chain excursions immediately.",
            ],
        ],
    )
    write_sidecar(
        sop_014_v3_path,
        {
            "doc_id": "SOP-014-v3",
            "title": "SOP-014 Cold-Chain Storage v3",
            "source_type": "sop",
            "version": "3.0",
            "date": "2025-06-20",
            "author": "Arjun Menon",
            "owner": "Arjun Menon",
            "status": "current",
            "supersedes": "SOP-014-v2",
            "allowed_roles": ["intern", "analyst", "manager"],
            "topics": ["cold-chain", "storage-temperature"],
        },
    )

    # 3. SOP-021 (sop/.pdf) - current
    sop_021_path = target_dir / "sop" / "SOP-021.pdf"
    create_pdf(
        sop_021_path,
        "SOP-021 CAPA Management",
        [
            [
                "Section 1. Purpose and Overview:",
                "This procedure establishes standard requirements for corrective and preventive actions following quality events and confirmed out-of-specification results.",
                "A CAPA must be raised and the investigation completed within 15 working days of an OOS result being confirmed.",
                "Priya Rao, QA Lead, owns deviation management and oversees CAPA root cause analysis across manufacturing lines.",
            ],
            [
                "Section 2. Investigation and Closure:",
                "All investigations require cross-functional review by Quality Assurance before closure.",
                "Corrective actions must eliminate the verified root cause to prevent recurrence of deviations.",
            ],
        ],
    )
    write_sidecar(
        sop_021_path,
        {
            "doc_id": "SOP-021",
            "title": "SOP-021 CAPA Management",
            "source_type": "sop",
            "version": "1.0",
            "date": "2025-03-10",
            "author": "Priya Rao",
            "owner": "Priya Rao",
            "status": "current",
            "supersedes": None,
            "allowed_roles": ["analyst", "manager"],
            "topics": ["capa", "oos", "deviation"],
        },
    )

    # 4. SOP-001 (sop/.pdf) - current
    sop_001_path = target_dir / "sop" / "SOP-001.pdf"
    create_pdf(
        sop_001_path,
        "SOP-001 Deviation Handling",
        [
            [
                "Section 1. Scope and Responsibilities:",
                "This standard operating procedure applies to all GMP operations at Novacure Labs.",
                "Priya Rao, QA Lead, owns deviation management.",
                "Every deviation must be reported to QA within 24 hours of discovery.",
            ],
            [
                "Section 2. Deviation Classification:",
                "Deviations are categorized into Minor, Major, and Critical by the QA Lead.",
                "Priya Rao reviews and approves all immediate containment actions for active deviations.",
            ],
        ],
    )
    write_sidecar(
        sop_001_path,
        {
            "doc_id": "SOP-001",
            "title": "SOP-001 Deviation Handling",
            "source_type": "sop",
            "version": "1.0",
            "date": "2025-01-15",
            "author": "Priya Rao",
            "owner": "Priya Rao",
            "status": "current",
            "supersedes": None,
            "allowed_roles": ["intern", "analyst", "manager"],
            "topics": ["deviation", "quality-system"],
        },
    )

    # 5. REG-001 (pdf/.pdf) - current
    reg_001_path = target_dir / "pdf" / "REG-001.pdf"
    create_pdf(
        reg_001_path,
        "Regulatory Guideline Summary",
        [
            [
                "Section 1. Global Regulatory Framework:",
                "Summary of ICH Q9 Quality Risk Management and ICH Q10 Pharmaceutical Quality Systems.",
                "Kavya Nair ensures compliance with applicable health authority regulations and audit expectations.",
            ],
            [
                "Section 2. Data Governance and Inspection Readiness:",
                "Electronic records must comply with 21 CFR Part 11 and EU GMP Annex 11 principles.",
                "Data integrity controls prevent unauthorized modification of GMP records.",
            ],
        ],
    )
    write_sidecar(
        reg_001_path,
        {
            "doc_id": "REG-001",
            "title": "Regulatory Guideline Summary",
            "source_type": "pdf",
            "version": "1.0",
            "date": "2025-02-01",
            "author": "Kavya Nair",
            "owner": "Kavya Nair",
            "status": "current",
            "supersedes": None,
            "allowed_roles": ["analyst", "manager"],
            "topics": ["regulatory", "data-integrity"],
        },
    )

    # 6. QM-001 (sharepoint/.docx) - current
    qm_001_path = target_dir / "sharepoint" / "QM-001.docx"
    create_docx(
        qm_001_path,
        "Quality Manual",
        [
            (
                "1. Quality Policy and Governance",
                [
                    "Novacure Labs is dedicated to delivering safe and effective biopharmaceutical products.",
                    "Quality leadership is overseen by Dr. Meera Iyer, QA Head, ensuring compliance with international cGMP standards.",
                ],
            ),
            (
                "2. Deviation Management System",
                [
                    "The deviation management system ensures prompt investigation and corrective action.",
                    "Priya Rao, QA Lead, owns deviation management and directs QA investigations across operations.",
                    "All personnel must adhere strictly to established quality management standards.",
                ],
            ),
        ],
    )
    write_sidecar(
        qm_001_path,
        {
            "doc_id": "QM-001",
            "title": "Quality Manual",
            "source_type": "sharepoint",
            "version": "4.1",
            "date": "2025-01-10",
            "author": "Dr. Meera Iyer",
            "owner": "Dr. Meera Iyer",
            "status": "current",
            "supersedes": None,
            "allowed_roles": ["intern", "analyst", "manager"],
            "topics": ["quality-system", "deviation"],
        },
    )

    # 7. AUD-001 (sharepoint/.docx) - manager only
    aud_001_path = target_dir / "sharepoint" / "AUD-001.docx"
    create_docx(
        aud_001_path,
        "Audit Findings Summary",
        [
            (
                "1. Executive Audit Overview",
                [
                    "Confidential internal compliance assessment conducted by external QA auditors for executive leadership.",
                    "This report is restricted to management personnel only.",
                ],
            ),
            (
                "2. Recurring Quality Findings",
                [
                    "The audit identified a recurring deviation: temperature excursions in cold-chain storage during Q2 and Q3.",
                    "Priya Rao, QA Lead, owns deviation management and was requested by Dr. Meera Iyer to initiate remediation.",
                    "Management must review preventive CAPA implementation timelines immediately.",
                ],
            ),
        ],
    )
    write_sidecar(
        aud_001_path,
        {
            "doc_id": "AUD-001",
            "title": "Audit Findings Summary",
            "source_type": "sharepoint",
            "version": "1.0",
            "date": "2025-10-12",
            "author": "Dr. Meera Iyer",
            "owner": "Dr. Meera Iyer",
            "status": "current",
            "supersedes": None,
            "allowed_roles": ["manager"],
            "topics": ["audit", "deviation", "cold-chain"],
        },
    )

    # 8. ONB-001 (sharepoint/.docx) - current
    onb_001_path = target_dir / "sharepoint" / "ONB-001.docx"
    create_docx(
        onb_001_path,
        "New QA Hire Onboarding Guide",
        [
            (
                "1. Welcome to Novacure Labs",
                [
                    "Welcome to the Quality Assurance team at Novacure Labs. This guide structures your initial training requirements.",
                    "In your first week, read the Quality Manual, SOP-001, SOP-021 and the Data Integrity Policy.",
                ],
            ),
            (
                "2. Key Department Contacts",
                [
                    "Priya Rao, QA Lead, owns deviation management and will supervise your deviation investigation shadowing sessions.",
                    "Sana Khan, QA Analyst, is your onboarding mentor for daily lab record documentation reviews.",
                ],
            ),
        ],
    )
    write_sidecar(
        onb_001_path,
        {
            "doc_id": "ONB-001",
            "title": "New QA Hire Onboarding Guide",
            "source_type": "sharepoint",
            "version": "2.0",
            "date": "2025-02-15",
            "author": "Priya Rao",
            "owner": "Priya Rao",
            "status": "current",
            "supersedes": None,
            "allowed_roles": ["intern", "analyst", "manager"],
            "topics": ["onboarding", "new-joiner", "deviation"],
        },
    )

    # 9. EML-001 (email/.eml) - current
    eml_001_path = target_dir / "email" / "EML-001.eml"
    create_eml(
        eml_001_path,
        from_addr="Dr. Meera Iyer <meera.iyer@novacure.com>",
        to_addr="arjun.menon@novacure.com, qa-team@novacure.com",
        subject="Storage temperature change (from QA Head)",
        date_str="Fri, 18 Sep 2026 09:30:00 +0000",
        body=(
            "Team,\n\n"
            "Following recent stability monitoring data and regulatory advisories:\n"
            "Until SOP-014 is revised, store vaccine batches at 2 to 6 °C.\n\n"
            "Please ensure warehouse temperature limits are set to these tighter thresholds immediately.\n"
            "Priya Rao will review any related deviation reports.\n\n"
            "Regards,\nDr. Meera Iyer\nQA Head, Novacure Labs"
        ),
    )
    write_sidecar(
        eml_001_path,
        {
            "doc_id": "EML-001",
            "title": "Storage temperature change (from QA Head)",
            "source_type": "email",
            "version": None,
            "date": "2026-09-18",
            "author": "Dr. Meera Iyer",
            "owner": "Dr. Meera Iyer",
            "status": "current",
            "supersedes": None,
            "allowed_roles": ["analyst", "manager"],
            "topics": ["cold-chain", "storage-temperature"],
        },
    )

    # 10. EML-002 (email/.eml) - current
    eml_002_path = target_dir / "email" / "EML-002.eml"
    create_eml(
        eml_002_path,
        from_addr="Priya Rao <priya.rao@novacure.com>",
        to_addr="sana.khan@novacure.com, meera.iyer@novacure.com",
        subject="Deviation closure thread",
        date_str="Mon, 21 Sep 2026 14:15:00 +0000",
        body=(
            "Hi Sana,\n\n"
            "Priya Rao, QA Lead, owns deviation management and has completed review of DEV-2026-089.\n"
            "All root cause documentation and containment measures have been verified.\n"
            "The deviation record is formally approved and closed.\n\n"
            "Best,\nPriya Rao\nQA Lead"
        ),
    )
    write_sidecar(
        eml_002_path,
        {
            "doc_id": "EML-002",
            "title": "Deviation closure thread",
            "source_type": "email",
            "version": None,
            "date": "2026-09-21",
            "author": "Priya Rao",
            "owner": "Priya Rao",
            "status": "current",
            "supersedes": None,
            "allowed_roles": ["analyst", "manager"],
            "topics": ["deviation"],
        },
    )

    # 11. TEAMS-COLDCHAIN (teams/.json) - current
    teams_coldchain_path = target_dir / "teams" / "TEAMS-COLDCHAIN.json"
    teams_coldchain_messages = [
        {
            "msg_id": 1,
            "author": "Arjun Menon",
            "timestamp": "2026-09-19T08:15:00Z",
            "text": "Morning team. Heads up regarding the cold-chain warehouse temperature setpoints.",
        },
        {
            "msg_id": 2,
            "author": "Arjun Menon",
            "timestamp": "2026-09-19T08:16:30Z",
            "text": "Per Dr. Meera Iyer, hold vaccine batches at 2 to 6 °C until SOP-014 is revised.",
        },
        {
            "msg_id": 3,
            "author": "Sana Khan",
            "timestamp": "2026-09-19T08:20:00Z",
            "text": "Understood Arjun. Has the deviation logging threshold also changed?",
        },
        {
            "msg_id": 4,
            "author": "Arjun Menon",
            "timestamp": "2026-09-19T08:25:00Z",
            "text": "SOP-014-v3 still governs deviation reporting for excursions over 4 hours. Keep Priya Rao updated on any variance.",
        },
        {
            "msg_id": 5,
            "author": "Priya Rao",
            "timestamp": "2026-09-19T08:30:00Z",
            "text": "Priya Rao here. Any deviation logged against 2 to 6 °C should reference Dr. Meera Iyer's memo.",
        },
    ]
    create_teams_json(teams_coldchain_path, teams_coldchain_messages)
    write_sidecar(
        teams_coldchain_path,
        {
            "doc_id": "TEAMS-COLDCHAIN",
            "title": "#cold-chain",
            "source_type": "teams",
            "version": None,
            "date": "2026-09-19",
            "author": "Arjun Menon",
            "owner": "Arjun Menon",
            "status": "current",
            "supersedes": None,
            "allowed_roles": ["analyst", "manager"],
            "topics": ["cold-chain", "storage-temperature"],
        },
    )

    # 12. TEAMS-QAHELP (teams/.json) - current (intern, analyst, manager)
    teams_qahelp_path = target_dir / "teams" / "TEAMS-QAHELP.json"
    teams_qahelp_messages = [
        {
            "msg_id": 1,
            "author": "Rahul Verma",
            "timestamp": "2026-09-20T10:00:00Z",
            "text": "Hi everyone, I have a quick question about deviation log forms for new joiners.",
        },
        {
            "msg_id": 2,
            "author": "Sana Khan",
            "timestamp": "2026-09-20T10:05:00Z",
            "text": "Check SOP-001 Section 1 for the 24-hour reporting requirement.",
        },
        {
            "msg_id": 3,
            "author": "Priya Rao",
            "timestamp": "2026-09-20T10:10:00Z",
            "text": "Priya Rao, QA Lead, owns deviation management. Rahul, ping me directly if you need form QA-DEV-01.",
        },
        {
            "msg_id": 4,
            "author": "Rahul Verma",
            "timestamp": "2026-09-20T10:12:00Z",
            "text": "Thank you Priya, will review the onboarding guide and SOP-001 now.",
        },
    ]
    create_teams_json(teams_qahelp_path, teams_qahelp_messages)
    write_sidecar(
        teams_qahelp_path,
        {
            "doc_id": "TEAMS-QAHELP",
            "title": "#qa-help",
            "source_type": "teams",
            "version": None,
            "date": "2026-09-20",
            "author": "Priya Rao",
            "owner": "Priya Rao",
            "status": "current",
            "supersedes": None,
            "allowed_roles": ["intern", "analyst", "manager"],
            "topics": ["deviation", "onboarding"],
        },
    )


    # 13. DI-001 (sharepoint/.docx) - current
    di_001_path = target_dir / "sharepoint" / "DI-001.docx"
    create_docx(
        di_001_path,
        "Data Integrity Policy",
        [
            (
                "1. ALCOA+ Principles",
                [
                    "All data generated across Novacure Labs must be Attributable, Legible, Contemporaneous, Original, and Accurate.",
                    "Audit trails must remain enabled at all times on validated computerized systems.",
                ],
            ),
            (
                "2. Governance and Oversight",
                [
                    "Kavya Nair and Priya Rao oversee data integrity compliance checks across departments.",
                    "Any intentional or accidental falsification constitutes a critical deviation.",
                ],
            ),
        ],
    )
    write_sidecar(
        di_001_path,
        {
            "doc_id": "DI-001",
            "title": "Data Integrity Policy",
            "source_type": "sharepoint",
            "version": "1.2",
            "date": "2025-01-20",
            "author": "Kavya Nair",
            "owner": "Kavya Nair",
            "status": "current",
            "supersedes": None,
            "allowed_roles": ["analyst", "manager"],
            "topics": ["data-integrity", "quality-system"],
        },
    )

    # 14. EQP-001 (pdf/.pdf) - current
    eqp_001_path = target_dir / "pdf" / "EQP-001.pdf"
    create_pdf(
        eqp_001_path,
        "Cold Storage Unit Equipment Manual",
        [
            [
                "Section 1. Unit Specifications and Operation:",
                "Operating manual for industrial pharmaceutical cold storage chambers.",
                "Storage units maintain a setpoint of 2 to 8 °C under normal load conditions.",
                "Arjun Menon is responsible for monthly preventive maintenance and sensor calibration.",
            ],
            [
                "Section 2. Alarm and Excursion Protocols:",
                "Audible alarms trigger when chamber temperatures breach operational limits.",
                "Vikram Shah coordinates maintenance response with facility engineering.",
            ],
        ],
    )
    write_sidecar(
        eqp_001_path,
        {
            "doc_id": "EQP-001",
            "title": "Cold Storage Unit Equipment Manual",
            "source_type": "pdf",
            "version": "1.0",
            "date": "2025-01-05",
            "author": "Arjun Menon",
            "owner": "Arjun Menon",
            "status": "current",
            "supersedes": None,
            "allowed_roles": ["analyst", "manager"],
            "topics": ["equipment", "cold-chain"],
        },
    )

    # 15. STB-001 (pdf/.pdf) - current
    stb_001_path = target_dir / "pdf" / "STB-001.pdf"
    create_pdf(
        stb_001_path,
        "Stability Study Report",
        [
            [
                "Section 1. Study Design and Scope:",
                "Long-term stability protocol assessing degradation kinetics of lead vaccine formulations.",
                "Samples are maintained under recommended refrigerated storage conditions at 2 to 8 °C.",
            ],
            [
                "Section 2. 12-Month Analytical Results:",
                "Potency and purity testing confirms stability within specification over the study interval.",
                "Priya Rao reviewed degradation pathway deviations logged during preliminary thermal stress testing.",
            ],
        ],
    )
    write_sidecar(
        stb_001_path,
        {
            "doc_id": "STB-001",
            "title": "Stability Study Report",
            "source_type": "pdf",
            "version": "1.0",
            "date": "2025-03-30",
            "author": "Vikram Shah",
            "owner": "Vikram Shah",
            "status": "current",
            "supersedes": None,
            "allowed_roles": ["analyst", "manager"],
            "topics": ["stability", "storage-temperature"],
        },
    )


if __name__ == "__main__":
    from app.config import FIXTURES_DIR

    sample_raw_dir = FIXTURES_DIR / "raw_sample"
    generate_all_samples(sample_raw_dir)
    print(f"Generated raw sample fixtures at {sample_raw_dir}")
