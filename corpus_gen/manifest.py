"""
corpus_gen/manifest.py
Specification manifest for the 20 documents of Novacure Labs.
Defined per PLAN.md sections 5.4, 5.5, 6.1, 6.2, 6.3, 6.4.
"""

from typing import Any, Dict, List

ALLOWED_TOPICS = {
    "deviation",
    "capa",
    "oos",
    "cold-chain",
    "storage-temperature",
    "audit",
    "onboarding",
    "data-integrity",
    "stability",
    "equipment",
    "regulatory",
    "quality-system",
    "new-joiner",
}

PEOPLE = {
    "Dr. Meera Iyer": "QA Head",
    "Priya Rao": "QA Lead (owns deviation management)",
    "Arjun Menon": "Cold-Chain Supervisor",
    "Sana Khan": "QA Analyst",
    "Kavya Nair": "Regulatory Affairs Manager",
    "Vikram Shah": "Production Manager",
    "Rahul Verma": "New QA joiner",
}

MANIFEST: List[Dict[str, Any]] = [
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
        "folder": "sop",
        "filename": "SOP-001.pdf",
        "brief": (
            "Standard operating procedure detailing deviation identification, classification, and reporting protocols at Novacure Labs.\n"
            "Mandates immediate initial notification to Quality Assurance and formal escalation pathways for minor and major deviations.\n"
            "Specifies roles, responsibilities, initial containment, root-cause investigation triggers, and deviation closure criteria."
        ),
        "fixed_sentences": [
            "Every deviation must be reported to QA within 24 hours of discovery.",
            "Priya Rao, QA Lead, owns deviation management.",
        ],
        "people": ["Priya Rao"],
    },
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
        "folder": "sop",
        "filename": "SOP-014-v2.pdf",
        "brief": (
            "Superseded version 2.0 operating procedure governing temperature-controlled biological product storage at Novacure Labs.\n"
            "Defines the approved cold-chain temperature boundary and baseline monitoring intervals for refrigerated stock.\n"
            "Sets forth the legacy excursion notification allowance permitting short-term deviations without formal logging."
        ),
        "fixed_sentences": [
            "Vaccine batches must be stored at 2 to 8 °C.",
            "Temperature excursions of up to 12 hours do not require a deviation report.",
        ],
        "people": ["Arjun Menon"],
    },
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
        "folder": "sop",
        "filename": "SOP-014-v3.pdf",
        "brief": (
            "Current version 3.0 standard operating procedure governing cold-chain storage and handling for vaccine batches.\n"
            "Replaces version 2.0 with tightened excursion management controls, continuous digital datalogging, and quarantine rules.\n"
            "Establishes strict deviation escalation triggers when storage conditions breach predefined validated boundaries."
        ),
        "fixed_sentences": [
            "Vaccine batches must be stored at 2 to 8 °C.",
            "Any temperature excursion longer than 4 hours requires a deviation report.",
        ],
        "people": ["Arjun Menon"],
    },
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
        "folder": "sop",
        "filename": "SOP-021.pdf",
        "brief": (
            "Standard operating procedure for Corrective and Preventive Actions (CAPA) lifecycle management across Novacure Labs.\n"
            "Establishes mandatory root-cause analysis methodologies and timelines following confirmation of an Out of Specification result.\n"
            "Details action plan approval, implementation verification, effectiveness checks, and QA governance led by Priya Rao."
        ),
        "fixed_sentences": [
            "A CAPA must be raised and the investigation completed within 15 working days of an OOS result being confirmed.",
            "Priya Rao, QA Lead, owns deviation management.",
        ],
        "people": ["Priya Rao"],
    },
    {
        "doc_id": "QM-001",
        "title": "Quality Manual",
        "source_type": "sharepoint",
        "version": "4.1",
        "date": "2024-10-01",
        "author": "Dr. Meera Iyer",
        "owner": "Dr. Meera Iyer",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["intern", "analyst", "manager"],
        "topics": ["quality-system", "deviation"],
        "folder": "sharepoint",
        "filename": "QM-001.docx",
        "brief": (
            "High-level Quality Management System manual defining Novacure Labs quality policy, structure, and GMP commitments.\n"
            "Outlines governance tiers, executive management responsibilities, documentation hierarchy, and quality culture.\n"
            "Designates functional ownership for deviation handling, compliance audits, change management, and continual improvement."
        ),
        "fixed_sentences": [
            "Priya Rao, QA Lead, owns deviation management.",
        ],
        "people": ["Dr. Meera Iyer", "Priya Rao"],
    },
    {
        "doc_id": "ONB-001",
        "title": "New QA Hire Onboarding Guide",
        "source_type": "sharepoint",
        "version": "2.0",
        "date": "2025-08-01",
        "author": "Sana Khan",
        "owner": "Sana Khan",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["intern", "analyst", "manager"],
        "topics": ["onboarding", "new-joiner", "deviation"],
        "folder": "sharepoint",
        "filename": "ONB-001.docx",
        "brief": (
            "Comprehensive onboarding roadmap and curriculum for incoming Quality Assurance personnel at Novacure Labs.\n"
            "Lists mandatory first-week compliance reading, facility walkthrough checklists, and core system access protocols.\n"
            "Identifies key department contacts, mentoring expectations, and orientation milestones for new QA analysts and interns."
        ),
        "fixed_sentences": [
            "In your first week, read the Quality Manual, SOP-001, SOP-021 and the Data Integrity Policy.",
            "Priya Rao, QA Lead, owns deviation management.",
        ],
        "people": ["Rahul Verma", "Sana Khan", "Priya Rao"],
    },
    {
        "doc_id": "DI-001",
        "title": "Data Integrity Policy",
        "source_type": "sharepoint",
        "version": "1.2",
        "date": "2025-02-14",
        "author": "Dr. Meera Iyer",
        "owner": "Dr. Meera Iyer",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["analyst", "manager"],
        "topics": ["data-integrity", "quality-system"],
        "folder": "sharepoint",
        "filename": "DI-001.docx",
        "brief": (
            "Corporate policy establishing ALCOA+ data integrity standards across all laboratory and manufacturing records.\n"
            "Mandates electronic audit trails, secure computerized system controls, contemporaneity of raw data, and backup procedures.\n"
            "Prohibits unauthorized alteration, deletion, or backdating of GxP records and defines reporting mechanisms for violations."
        ),
        "fixed_sentences": [],
        "people": ["Dr. Meera Iyer"],
    },
    {
        "doc_id": "AUD-001",
        "title": "Audit Findings Summary",
        "source_type": "sharepoint",
        "version": "1.0",
        "date": "2025-11-20",
        "author": "Dr. Meera Iyer",
        "owner": "Dr. Meera Iyer",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["manager"],
        "topics": ["audit", "deviation", "cold-chain"],
        "folder": "sharepoint",
        "filename": "AUD-001.docx",
        "brief": (
            "Confidential executive summary of internal and external regulatory audit inspections conducted at Novacure Labs.\n"
            "Details non-conformance observations, risk rankings, repeat deficiencies in cold-chain logistics, and required remediations.\n"
            "Assigns managerial accountability and sets remediation timelines for quality system deficiencies."
        ),
        "fixed_sentences": [
            "The audit identified a recurring deviation: temperature excursions in cold-chain storage during Q2 and Q3.",
            "Priya Rao, QA Lead, owns deviation management.",
        ],
        "people": ["Dr. Meera Iyer", "Priya Rao"],
    },
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
        "folder": "email",
        "filename": "EML-001.eml",
        "brief": (
            "Urgent directive from QA Head Dr. Meera Iyer instructing cold-chain operations to adjust vaccine storage boundaries.\n"
            "Specifies temporary restriction to a tightened storage band while pending formal revision of SOP-014.\n"
            "Requests immediate confirmation and operational compliance from Cold-Chain Supervisor Arjun Menon."
        ),
        "fixed_sentences": [
            "Until SOP-014 is revised, store vaccine batches at 2 to 6 °C.",
        ],
        "people": ["Dr. Meera Iyer", "Arjun Menon"],
    },
    {
        "doc_id": "EML-002",
        "title": "Deviation closure thread",
        "source_type": "email",
        "version": None,
        "date": "2026-04-12",
        "author": "Priya Rao",
        "owner": "Priya Rao",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["analyst", "manager"],
        "topics": ["deviation"],
        "folder": "email",
        "filename": "EML-002.eml",
        "brief": (
            "Quality Assurance email correspondence discussing evidence review and closure criteria for open plant deviations.\n"
            "Emphasizes adherence to root-cause investigation documentation and timely closure sign-offs.\n"
            "Reiterates QA leadership oversight under Priya Rao."
        ),
        "fixed_sentences": [
            "Priya Rao, QA Lead, owns deviation management.",
        ],
        "people": ["Priya Rao", "Sana Khan"],
    },
    {
        "doc_id": "EML-003",
        "title": "CAPA overdue reminder",
        "source_type": "email",
        "version": None,
        "date": "2026-05-08",
        "author": "Priya Rao",
        "owner": "Priya Rao",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["analyst", "manager"],
        "topics": ["capa", "deviation"],
        "folder": "email",
        "filename": "EML-003.eml",
        "brief": (
            "Formal QA compliance notification warning operations regarding impending and overdue CAPA corrective action milestones.\n"
            "Demands immediate submission of pending root-cause analyses and implementation progress reports to prevent compliance escalations.\n"
            "Directs responses to QA Lead Priya Rao."
        ),
        "fixed_sentences": [
            "Priya Rao, QA Lead, owns deviation management.",
        ],
        "people": ["Priya Rao", "Vikram Shah"],
    },
    {
        "doc_id": "EML-004",
        "title": "Audit prep",
        "source_type": "email",
        "version": None,
        "date": "2026-06-15",
        "author": "Dr. Meera Iyer",
        "owner": "Dr. Meera Iyer",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["manager"],
        "topics": ["audit", "deviation"],
        "folder": "email",
        "filename": "EML-004.eml",
        "brief": (
            "Confidential leadership email regarding pre-audit preparation and readiness ahead of upcoming regulatory agency inspection.\n"
            "Coordinates executive strategy, document room readiness, mock inspection interviews, and deviation backlog remediation.\n"
            "Instructs leadership team to align with Priya Rao on deviation log status."
        ),
        "fixed_sentences": [
            "Priya Rao, QA Lead, owns deviation management.",
        ],
        "people": ["Dr. Meera Iyer", "Priya Rao"],
    },
    {
        "doc_id": "EML-005",
        "title": "New joiner welcome",
        "source_type": "email",
        "version": None,
        "date": "2026-07-01",
        "author": "Dr. Meera Iyer",
        "owner": "Dr. Meera Iyer",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["intern", "analyst", "manager"],
        "topics": ["onboarding", "new-joiner"],
        "folder": "email",
        "filename": "EML-005.eml",
        "brief": (
            "Department-wide welcome announcement introducing Rahul Verma as a new joiner in the Quality Assurance department.\n"
            "Encourages team members to assist Rahul during orientation and outlines his initial assignment and training mentor.\n"
            "Provides an encouraging overview of Novacure Labs quality excellence ethos."
        ),
        "fixed_sentences": [],
        "people": ["Rahul Verma", "Dr. Meera Iyer"],
    },
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
        "folder": "teams",
        "filename": "TEAMS-COLDCHAIN.json",
        "brief": (
            "Operations chat log from the #cold-chain Teams channel covering daily warehouse unit checks and alarms.\n"
            "Contains active coordination following Dr. Meera Iyer's instruction on temporary storage temperature restrictions.\n"
            "Features discussions on chiller sensor recalibration, datalogger downloads, and warehouse shift handovers."
        ),
        "fixed_sentences": [
            "Per Dr. Meera Iyer, hold vaccine batches at 2 to 6 °C until SOP-014 is revised.",
        ],
        "people": ["Arjun Menon", "Dr. Meera Iyer"],
    },
    {
        "doc_id": "TEAMS-QAHELP",
        "title": "#qa-help",
        "source_type": "teams",
        "version": None,
        "date": "2026-08-10",
        "author": "Priya Rao",
        "owner": "Priya Rao",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["intern", "analyst", "manager"],
        "topics": ["deviation", "onboarding"],
        "folder": "teams",
        "filename": "TEAMS-QAHELP.json",
        "brief": (
            "Collaborative discussion thread in the #qa-help channel addressing peer questions on document access and procedures.\n"
            "Provides junior analysts and interns with quick guidance on deviation reporting procedures and document repositories.\n"
            "Features QA lead Priya Rao advising new joiner Rahul Verma on deviation logging."
        ),
        "fixed_sentences": [
            "Priya Rao, QA Lead, owns deviation management.",
        ],
        "people": ["Priya Rao", "Rahul Verma", "Sana Khan"],
    },
    {
        "doc_id": "TEAMS-DEVIATIONS",
        "title": "#deviations",
        "source_type": "teams",
        "version": None,
        "date": "2026-08-15",
        "author": "Priya Rao",
        "owner": "Priya Rao",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["analyst", "manager"],
        "topics": ["deviation", "capa"],
        "folder": "teams",
        "filename": "TEAMS-DEVIATIONS.json",
        "brief": (
            "Technical channel discussion dedicated to active deviation tracking, triage, and root-cause investigations.\n"
            "Discusses manufacturing line anomalies, laboratory investigations, and CAPA initiation workflows.\n"
            "Demonstrates Priya Rao directing deviation evaluations and assigning investigation owners."
        ),
        "fixed_sentences": [
            "Priya Rao, QA Lead, owns deviation management.",
        ],
        "people": ["Priya Rao", "Vikram Shah", "Sana Khan"],
    },
    {
        "doc_id": "TEAMS-NEWJOINERS",
        "title": "#new-joiners",
        "source_type": "teams",
        "version": None,
        "date": "2026-07-05",
        "author": "Sana Khan",
        "owner": "Sana Khan",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["intern", "analyst", "manager"],
        "topics": ["onboarding", "new-joiner"],
        "folder": "teams",
        "filename": "TEAMS-NEWJOINERS.json",
        "brief": (
            "Informal cohort channel where new hires, interns, and mentors share onboarding tips and IT system setups.\n"
            "Rahul Verma asks questions regarding building access, training modules, and document search tips.\n"
            "Sana Khan guides junior colleagues through the first-week training requirements."
        ),
        "fixed_sentences": [],
        "people": ["Rahul Verma", "Sana Khan"],
    },
    {
        "doc_id": "REG-001",
        "title": "Regulatory Guideline Summary",
        "source_type": "pdf",
        "version": "1.0",
        "date": "2025-05-12",
        "author": "Kavya Nair",
        "owner": "Kavya Nair",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["analyst", "manager"],
        "topics": ["regulatory", "data-integrity"],
        "folder": "pdf",
        "filename": "REG-001.pdf",
        "brief": (
            "Summary digest of current regulatory guidance from FDA and EMA regarding computerized records and data integrity.\n"
            "Outlines statutory expectations for electronic signatures, system audit logs, and electronic submission standards.\n"
            "Highlights regulatory scrutiny regarding validation protocols, data traceability, and inspection readiness."
        ),
        "fixed_sentences": [],
        "people": ["Kavya Nair"],
    },
    {
        "doc_id": "EQP-001",
        "title": "Cold Storage Unit Equipment Manual",
        "source_type": "pdf",
        "version": "1.0",
        "date": "2024-09-01",
        "author": "Vikram Shah",
        "owner": "Vikram Shah",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["analyst", "manager"],
        "topics": ["equipment", "cold-chain"],
        "folder": "pdf",
        "filename": "EQP-001.pdf",
        "brief": (
            "Technical manual and operational guidelines for industrial cold storage refrigeration units and walk-in chillers.\n"
            "Details mechanical compressor maintenance, secondary backup power switching, temperature sensors, and calibration.\n"
            "Specifies scheduled preventive maintenance routines, alarm limits, and emergency containment response procedures."
        ),
        "fixed_sentences": [],
        "people": ["Vikram Shah", "Arjun Menon"],
    },
    {
        "doc_id": "STB-001",
        "title": "Stability Study Report",
        "source_type": "pdf",
        "version": "1.0",
        "date": "2025-10-30",
        "author": "Dr. Meera Iyer",
        "owner": "Dr. Meera Iyer",
        "status": "current",
        "supersedes": None,
        "allowed_roles": ["analyst", "manager"],
        "topics": ["stability", "storage-temperature"],
        "folder": "pdf",
        "filename": "STB-001.pdf",
        "brief": (
            "Formal stability testing study evaluating product potency and degradation profiles across long-term storage.\n"
            "Presents biochemical assay results, container-closure integrity data, and thermal stress challenge metrics.\n"
            "Validates real-time shelf life and accelerated stability projections for commercial batch releases."
        ),
        "fixed_sentences": [],
        "people": ["Dr. Meera Iyer"],
    },
]

DOCUMENTS = MANIFEST
