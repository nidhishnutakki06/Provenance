"""
corpus_gen/templates.py
Realistic offline templates for all 20 Novacure Labs documents.
Provides complete, professional pharmaceutical content embedding all required
fixed sentences and planted scenarios without needing external LLM calls.
"""

from typing import Any, Dict, List

TEMPLATES: Dict[str, Any] = {
    # -------------------------------------------------------------------------
    # 1. SOP-001
    # -------------------------------------------------------------------------
    "SOP-001": {
        "sections": [
            ("1. Purpose", "This Standard Operating Procedure establishes the mandatory process for identifying, documenting, triaging, and investigating deviations occurring during GMP manufacturing, packaging, testing, and storage operations at Novacure Labs."),
            ("2. Scope", "This procedure applies to all operational personnel, quality control analysts, warehouse operators, and validation engineers across all commercial and clinical production facilities at Novacure Labs."),
            ("3. Responsibilities", "Priya Rao, QA Lead, owns deviation management. The QA Lead is responsible for deviation classification, root-cause investigation approvals, and corrective action assignment. Department heads must ensure immediate reporting."),
            ("4. Procedure - Notification and Reporting", "Every deviation must be reported to QA within 24 hours of discovery. The reporting associate must execute immediate containment to prevent non-conforming product distribution and initiate an electronic deviation record in the QMS."),
            ("5. Procedure - Investigation and Root Cause", "For critical and major deviations, a formal root-cause analysis must be conducted using Ishikawa fishbone diagrams or 5-Why methodology. The investigation must be completed and submitted for QA review within 30 calendar days."),
            ("6. Batch Disposition and Record Retention", "Batches implicated in open deviations cannot be released for commercial distribution until all root-cause evaluations are concluded and signed off by Quality Assurance leadership. All records must be retained for at least 10 years."),
        ]
    },

    # -------------------------------------------------------------------------
    # 2. SOP-014-v2 (superseded)
    # -------------------------------------------------------------------------
    "SOP-014-v2": {
        "sections": [
            ("1. Purpose", "This procedure specifies storage conditions, cold-chain handling, and temperature monitoring standards for refrigerated pharmaceutical stock and bulk biological intermediates at Novacure Labs."),
            ("2. Scope and Specifications", "Vaccine batches must be stored at 2 to 8 °C. Applies to primary cold storage warehouse chambers and inter-facility cold-chain transfers. Temperature must be checked and recorded manually twice daily."),
            ("3. Temperature Excursion Management", "Temperature excursions of up to 12 hours do not require a deviation report. If an excursion exceeds 12 hours or rises above 12 °C, warehouse supervisors must notify the facility operations team."),
            ("4. Handling and Packaging", "Cold boxes must be packed using certified gel packs conditioning between -2 °C and 0 °C prior to batch loading. Shipments must not exceed 48 hours transit duration without ice replenishment."),
            ("5. Author and Administrative Control", "Authored by Arjun Menon, Cold-Chain Supervisor, Novacure Labs. Superseded by version 3.0 following revised risk assessment."),
        ]
    },

    # -------------------------------------------------------------------------
    # 3. SOP-014-v3 (current)
    # -------------------------------------------------------------------------
    "SOP-014-v3": {
        "sections": [
            ("1. Purpose", "This standard operating procedure sets mandatory storage limits, continuous telemetric monitoring, and quarantine rules for all temperature-sensitive vaccine products at Novacure Labs, superseding SOP-014-v2."),
            ("2. Cold-Chain Specifications", "Vaccine batches must be stored at 2 to 8 °C. Storage units must maintain calibrated NIST-traceable multi-point temperature sensors with real-time electronic alerting enabled 24/7."),
            ("3. Excursion Response Protocol", "Any temperature excursion longer than 4 hours requires a deviation report. Upon detecting a temperature excursion exceeding validated boundaries for more than 4 hours, stock must be segregated into quarantine immediately."),
            ("4. Quarantine and QA Escalation", "Physical quarantine cages and electronic warehouse holds must be applied instantly. The Cold-Chain Supervisor and QA Lead must initiate a deviation report within 24 hours pursuant to SOP-001."),
            ("5. Responsibilities and Author Control", "Authored by Arjun Menon, Cold-Chain Supervisor. Approved by Dr. Meera Iyer, QA Head. Replaces and supersedes SOP-014-v2 in its entirety."),
        ]
    },

    # -------------------------------------------------------------------------
    # 4. SOP-021
    # -------------------------------------------------------------------------
    "SOP-021": {
        "sections": [
            ("1. Purpose", "This procedure defines the requirements for initiating, evaluating, executing, and tracking Corrective and Preventive Actions (CAPA) at Novacure Labs."),
            ("2. Scope", "Encompasses quality issues resulting from confirmed OOS analytical findings, repeated deviations, internal audit findings, and regulatory audit observations."),
            ("3. Responsibilities", "Priya Rao, QA Lead, owns deviation management and provides oversight for CAPA system governance. Dr. Meera Iyer, QA Head, holds final approval authority for CAPA closure."),
            ("4. Timelines and Investigation", "A CAPA must be raised and the investigation completed within 15 working days of an OOS result being confirmed. The root-cause investigation must document verifiable containment and systemic remediation actions."),
            ("5. Effectiveness Review", "Each CAPA action plan must specify an effectiveness verification milestone typically scheduled 60 to 90 days post-implementation to guarantee defect recurrence is eliminated."),
        ]
    },

    # -------------------------------------------------------------------------
    # 5. QM-001
    # -------------------------------------------------------------------------
    "QM-001": {
        "title": "Novacure Labs Quality Manual",
        "subtitle": "Revision 4.1 - Quality Management System",
        "sections": [
            ("1. Corporate Quality Commitment", "Novacure Labs is dedicated to maintaining the highest standards of cGMP compliance, patient safety, and operational excellence across pharmaceutical manufacturing and testing operations."),
            ("2. Quality Governance Framework", "The Quality Assurance organization operates independently from production. Dr. Meera Iyer, QA Head, directs the executive quality committee. Priya Rao, QA Lead, owns deviation management and ensures operational compliance across all processing lines."),
            ("3. Deviation and Risk Management", "Quality risk management principles (ICH Q9) govern all deviation investigations, change controls, and CAPA systems. All operational personnel are required to flag potential compliance risks without delay."),
            ("4. Document Control Hierarchy", "The documentation pyramid consists of Level 1 Quality Manual, Level 2 Corporate Policies, Level 3 Standard Operating Procedures (SOPs), Level 4 Work Instructions, and Level 5 Batch Records and Forms."),
        ]
    },

    # -------------------------------------------------------------------------
    # 6. ONB-001
    # -------------------------------------------------------------------------
    "ONB-001": {
        "title": "New QA Hire Onboarding Guide",
        "subtitle": "Department of Quality Assurance - Novacure Labs",
        "sections": [
            ("Welcome to Quality Assurance", "Welcome to Novacure Labs Quality Assurance department. As a new team member, you play a pivotal role in safeguarding medicine quality and patient welfare. Sana Khan has prepared this curriculum to guide your initial weeks."),
            ("First Week Curriculum", "In your first week, read the Quality Manual, SOP-001, SOP-021 and the Data Integrity Policy. Complete the associated electronic reading acknowledgments in the learning management system before entering cleanroom suites."),
            ("Department Contacts and Mentorship", "Priya Rao, QA Lead, owns deviation management. For operational deviation triage and investigation inquiries, reach out to Priya Rao. For cold-chain logistics questions, consult Arjun Menon."),
            ("Training Milestones and Checkpoints", "By the end of your second week, you will shadow senior analysts on batch record review and observe a simulated deviation root-cause investigation. Welcome Rahul Verma and our incoming analyst cohort!"),
        ]
    },

    # -------------------------------------------------------------------------
    # 7. DI-001
    # -------------------------------------------------------------------------
    "DI-001": {
        "title": "Data Integrity Policy",
        "subtitle": "Corporate GxP Compliance Policy - Version 1.2",
        "sections": [
            ("1. Policy Statement", "Novacure Labs strictly enforces data integrity principles across all computerized systems, laboratory instrumentation, paper records, and data archives. Truthful, contemporaneous, and uncompromised data is the core of our license to operate."),
            ("2. ALCOA+ Principles", "All GxP data generated must be Attributable, Legible, Contemporaneous, Original, and Accurate. In addition, data must remain Complete, Consistent, Enduring, and Available throughout the record retention period."),
            ("3. Electronic System Controls", "Computerized systems must feature role-based permissions, unique user credentials, and active automated audit trails. Shared generic passwords are categorically prohibited. Audit trail reviews must be executed prior to batch release."),
            ("4. Enforcement and Governance", "Authored and authorized by Dr. Meera Iyer, QA Head. Any deliberate manipulation, backdating, deletion, or omission of GxP data constitutes gross misconduct and grounds for immediate dismissal and regulatory notification."),
        ]
    },

    # -------------------------------------------------------------------------
    # 8. AUD-001
    # -------------------------------------------------------------------------
    "AUD-001": {
        "title": "Audit Findings Summary - Annual Quality Inspection",
        "subtitle": "Confidential - Managerial Review Only",
        "sections": [
            ("Executive Summary", "This confidential report synthesizes observations from internal compliance assessments and external regulatory inspections completed during the fiscal year across Novacure Labs facilities. Dr. Meera Iyer, QA Head, issued this summary for management review."),
            ("Critical and Major Audit Observations", "The audit identified a recurring deviation: temperature excursions in cold-chain storage during Q2 and Q3. Multiple temperature fluctuations in warehouse refrigeration chambers exceeded permitted durations without prompt root-cause escalation."),
            ("Remediation and Corrective Mandate", "Priya Rao, QA Lead, owns deviation management and has been directed to coordinate an enterprise-wide review of cold storage alerts, revising operating procedures and implementing automated notification links between building management systems and the QMS."),
            ("Managerial Action Items", "Warehouse management under Vikram Shah and cold-chain leads must finalize physical insulation upgrades and complete CAPA verification before the upcoming regulatory audit."),
        ]
    },

    # -------------------------------------------------------------------------
    # 9. EML-001
    # -------------------------------------------------------------------------
    "EML-001": {
        "from": "meera.iyer@novacure.com",
        "to": "arjun.menon@novacure.com",
        "subject": "Storage temperature change (from QA Head)",
        "date": "Fri, 18 Sep 2026 09:30:00 +0000",
        "body": (
            "Hi Arjun,\n\n"
            "Following preliminary stability review and feedback from our quality committee, we are introducing an immediate interim restriction on cold storage operations.\n\n"
            "Until SOP-014 is revised, store vaccine batches at 2 to 6 °C.\n\n"
            "Please adjust setpoints on warehouse refrigeration units Chiller-01 and Chiller-02 accordingly today, and instruct the warehouse team to monitor alerts within this narrower window.\n\n"
            "Regards,\n"
            "Dr. Meera Iyer\n"
            "QA Head, Novacure Labs\n"
        )
    },

    # -------------------------------------------------------------------------
    # 10. EML-002
    # -------------------------------------------------------------------------
    "EML-002": {
        "from": "priya.rao@novacure.com",
        "to": "sana.khan@novacure.com",
        "subject": "Deviation closure thread",
        "date": "Sun, 12 Apr 2026 14:15:00 +0000",
        "body": (
            "Hi Sana,\n\n"
            "I have reviewed the investigation documentation for DEV-2026-088. The root-cause assessment meets our standards, and the containment actions were executed cleanly.\n\n"
            "As a reminder for the team, Priya Rao, QA Lead, owns deviation management and provides final QA sign-off for closure. Please submit the attached QA impact statement to the record so we can formally sign off before the end of the shift.\n\n"
            "Thanks,\n"
            "Priya Rao\n"
            "QA Lead, Novacure Labs\n"
        )
    },

    # -------------------------------------------------------------------------
    # 11. EML-003
    # -------------------------------------------------------------------------
    "EML-003": {
        "from": "priya.rao@novacure.com",
        "to": "vikram.shah@novacure.com",
        "subject": "CAPA overdue reminder",
        "date": "Fri, 08 May 2026 11:20:00 +0000",
        "body": (
            "Vikram,\n\n"
            "This is an urgent reminder that CAPA-2026-042 (Packaging line sensor drift) has exceeded its target implementation deadline of 30 days. We need immediate resolution on the root cause and replacement sensor calibration.\n\n"
            "Priya Rao, QA Lead, owns deviation management. Any delays in CAPA execution create significant audit vulnerability for the site. Please provide the updated effectiveness check plan by Monday morning.\n\n"
            "Best,\n"
            "Priya Rao\n"
            "QA Lead, Novacure Labs\n"
        )
    },

    # -------------------------------------------------------------------------
    # 12. EML-004
    # -------------------------------------------------------------------------
    "EML-004": {
        "from": "meera.iyer@novacure.com",
        "to": "priya.rao@novacure.com",
        "subject": "Audit prep",
        "date": "Mon, 15 Jun 2026 16:45:00 +0000",
        "body": (
            "Dear Priya,\n\n"
            "The regulatory agency has confirmed their site inspection for next month. Our priority during pre-audit preparations is to ensure all open deviations and CAPA files are thoroughly documented with robust rationales.\n\n"
            "Priya Rao, QA Lead, owns deviation management, so please lead the document readiness review for all open and recently closed deviation records. Prepare a summary table of repeat deviations over the last 12 months for executive review.\n\n"
            "Sincerely,\n"
            "Dr. Meera Iyer\n"
            "QA Head, Novacure Labs\n"
        )
    },

    # -------------------------------------------------------------------------
    # 13. EML-005
    # -------------------------------------------------------------------------
    "EML-005": {
        "from": "meera.iyer@novacure.com",
        "to": "rahul.verma@novacure.com",
        "subject": "New joiner welcome",
        "date": "Wed, 01 Jul 2026 09:00:00 +0000",
        "body": (
            "Dear Rahul,\n\n"
            "Welcome to Novacure Labs! We are delighted to have you join our Quality Assurance organization. Your training schedule has been organized in coordination with Sana Khan and your team mentors.\n\n"
            "Please review the onboarding materials on SharePoint and familiarize yourself with our site quality policies and operating procedures. Feel free to reach out to any of the team if you need guidance.\n\n"
            "Warm regards,\n"
            "Dr. Meera Iyer\n"
            "QA Head, Novacure Labs\n"
        )
    },

    # -------------------------------------------------------------------------
    # 14. TEAMS-COLDCHAIN
    # -------------------------------------------------------------------------
    "TEAMS-COLDCHAIN": [
        {"msg_id": 1, "author": "Arjun Menon", "timestamp": "2026-09-19T08:15:00Z", "text": "Morning team. Please check the datalogger readings on Chiller-01 before start of shift."},
        {"msg_id": 2, "author": "Dr. Meera Iyer", "timestamp": "2026-09-19T08:22:00Z", "text": "Arjun, did you see my email regarding the storage band adjustment?"},
        {"msg_id": 3, "author": "Arjun Menon", "timestamp": "2026-09-19T08:30:00Z", "text": "Yes Dr. Iyer. I am updating the setpoints on the control panel right now."},
        {"msg_id": 4, "author": "Arjun Menon", "timestamp": "2026-09-19T08:45:00Z", "text": "Per Dr. Meera Iyer, hold vaccine batches at 2 to 6 °C until SOP-014 is revised."},
        {"msg_id": 5, "author": "Sana Khan", "timestamp": "2026-09-19T09:10:00Z", "text": "Got it Arjun. Has the building automation alarm threshold been updated as well?"},
        {"msg_id": 6, "author": "Arjun Menon", "timestamp": "2026-09-19T09:18:00Z", "text": "Yes, high alarm warning is now configured at 6.1 °C on both units."},
        {"msg_id": 7, "author": "Vikram Shah", "timestamp": "2026-09-20T10:05:00Z", "text": "Are we ready to stage batch VAC-2026-902 for packaging?"},
        {"msg_id": 8, "author": "Arjun Menon", "timestamp": "2026-09-20T10:14:00Z", "text": "Temp logs over the last 24 hours show stable 3.8 °C. Clear for transfer."},
        {"msg_id": 9, "author": "Sana Khan", "timestamp": "2026-09-21T11:30:00Z", "text": "Double check the probe calibration certificate before signing the transfer sheet."},
        {"msg_id": 10, "author": "Arjun Menon", "timestamp": "2026-09-21T11:42:00Z", "text": "Calibration is valid through December 2026."},
        {"msg_id": 11, "author": "Vikram Shah", "timestamp": "2026-09-22T08:00:00Z", "text": "Backup compressor routine test scheduled for 14:00 today."},
        {"msg_id": 12, "author": "Arjun Menon", "timestamp": "2026-09-22T08:25:00Z", "text": "Confirmed, I will monitor temperature telemetry throughout the switchover."},
    ],

    # -------------------------------------------------------------------------
    # 15. TEAMS-QAHELP
    # -------------------------------------------------------------------------
    "TEAMS-QAHELP": [
        {"msg_id": 1, "author": "Rahul Verma", "timestamp": "2026-08-10T09:05:00Z", "text": "Hello everyone! Quick question: where can I find the initial deviation reporting template?"},
        {"msg_id": 2, "author": "Sana Khan", "timestamp": "2026-08-10T09:12:00Z", "text": "Welcome Rahul! It is located in the QMS electronic portal under Form-DEV-01."},
        {"msg_id": 3, "author": "Rahul Verma", "timestamp": "2026-08-10T09:18:00Z", "text": "Thanks Sana! Who should I assign as the primary QA reviewer when submitting?"},
        {"msg_id": 4, "author": "Priya Rao", "timestamp": "2026-08-10T09:25:00Z", "text": "Priya Rao, QA Lead, owns deviation management."},
        {"msg_id": 5, "author": "Priya Rao", "timestamp": "2026-08-10T09:28:00Z", "text": "Assign it to me in the QMS workflow and I will review the triage classification."},
        {"msg_id": 6, "author": "Rahul Verma", "timestamp": "2026-08-10T09:35:00Z", "text": "Understood Priya, will do. Appreciate the guidance!"},
        {"msg_id": 7, "author": "Sana Khan", "timestamp": "2026-08-10T10:00:00Z", "text": "Make sure you include the lot number and exact location timestamp in section 1."},
        {"msg_id": 8, "author": "Rahul Verma", "timestamp": "2026-08-10T10:15:00Z", "text": "Got it, filling out the details now."},
        {"msg_id": 9, "author": "Priya Rao", "timestamp": "2026-08-10T11:00:00Z", "text": "Also check SOP-001 for classification guidelines if you are uncertain whether it is minor or major."},
        {"msg_id": 10, "author": "Rahul Verma", "timestamp": "2026-08-10T11:10:00Z", "text": "Reading SOP-001 right now. Very clear!"},
    ],

    # -------------------------------------------------------------------------
    # 16. TEAMS-DEVIATIONS
    # -------------------------------------------------------------------------
    "TEAMS-DEVIATIONS": [
        {"msg_id": 1, "author": "Vikram Shah", "timestamp": "2026-08-15T08:30:00Z", "text": "Priya, we had a pressure drop alarm on sterile filling suite B at 04:15 this morning."},
        {"msg_id": 2, "author": "Priya Rao", "timestamp": "2026-08-15T08:38:00Z", "text": "Priya Rao, QA Lead, owns deviation management."},
        {"msg_id": 3, "author": "Priya Rao", "timestamp": "2026-08-15T08:42:00Z", "text": "Was sterile filling actively underway when the differential pressure dropped?"},
        {"msg_id": 4, "author": "Vikram Shah", "timestamp": "2026-08-15T08:49:00Z", "text": "No, line was in cleaning and sanitation mode between batch runs."},
        {"msg_id": 5, "author": "Priya Rao", "timestamp": "2026-08-15T08:55:00Z", "text": "Good. Log it as a minor deviation under DEV-2026-114 and attach the BMS pressure trace."},
        {"msg_id": 6, "author": "Sana Khan", "timestamp": "2026-08-15T09:12:00Z", "text": "I can assist Vikram with the environmental monitoring swab data collection."},
        {"msg_id": 7, "author": "Vikram Shah", "timestamp": "2026-08-15T09:30:00Z", "text": "Thanks Sana. I will have the swab plates pulled and sent to micro lab."},
        {"msg_id": 8, "author": "Priya Rao", "timestamp": "2026-08-15T10:00:00Z", "text": "Ensure the 24-hour clock rule in SOP-001 is respected for initial logging."},
        {"msg_id": 9, "author": "Vikram Shah", "timestamp": "2026-08-15T10:15:00Z", "text": "Deviation form submitted in QMS just now."},
        {"msg_id": 10, "author": "Priya Rao", "timestamp": "2026-08-15T11:00:00Z", "text": "Acknowledged. I will review and set the containment action items."},
    ],

    # -------------------------------------------------------------------------
    # 17. TEAMS-NEWJOINERS
    # -------------------------------------------------------------------------
    "TEAMS-NEWJOINERS": [
        {"msg_id": 1, "author": "Sana Khan", "timestamp": "2026-07-05T09:00:00Z", "text": "Welcome everyone to the new joiners chat channel! Feel free to ask any onboarding questions here."},
        {"msg_id": 2, "author": "Rahul Verma", "timestamp": "2026-07-05T09:15:00Z", "text": "Hi Sana! Thanks for setting this up. How do I get badge access to the QC testing wing?"},
        {"msg_id": 3, "author": "Sana Khan", "timestamp": "2026-07-05T09:25:00Z", "text": "You will need to complete the gowning qualification module in LMS first, then security will activate your badge."},
        {"msg_id": 4, "author": "Rahul Verma", "timestamp": "2026-07-05T09:40:00Z", "text": "Great, working through the online training modules right now."},
        {"msg_id": 5, "author": "Sana Khan", "timestamp": "2026-07-05T10:05:00Z", "text": "Also check the onboarding checklist in ONB-001 on SharePoint for week 1 priorities."},
        {"msg_id": 6, "author": "Rahul Verma", "timestamp": "2026-07-05T10:30:00Z", "text": "Yes, I am reading through the Quality Manual and SOP-001 today."},
        {"msg_id": 7, "author": "Sana Khan", "timestamp": "2026-07-05T11:15:00Z", "text": "Let me know if you want to grab lunch around 12:30 with the QA analysts."},
        {"msg_id": 8, "author": "Rahul Verma", "timestamp": "2026-07-05T11:20:00Z", "text": "Sounds great! See you at 12:30 in the cafeteria."},
        {"msg_id": 9, "author": "Sana Khan", "timestamp": "2026-07-05T14:00:00Z", "text": "Remember to log your reading completion signatures in the training tracker."},
        {"msg_id": 10, "author": "Rahul Verma", "timestamp": "2026-07-05T14:10:00Z", "text": "All signed and submitted for day 1!"},
    ],

    # -------------------------------------------------------------------------
    # 18. REG-001
    # -------------------------------------------------------------------------
    "REG-001": {
        "title": "Regulatory Guideline Summary: GxP Data Integrity & Records",
        "subtitle": "Novacure Labs Regulatory Affairs - Technical Brief",
        "sections": [
            ("1. Overview of Global Regulatory Expectations", "Regulatory health authorities including the FDA (21 CFR Part 11) and EMA (Annex 11) emphasize complete and verifiable traceability for all data used to demonstrate pharmaceutical safety, quality, and efficacy. Kavya Nair, Regulatory Affairs Manager, compiled this summary to support site compliance."),
            ("2. Statutory Audit Trail Obligations", "Audit trails must remain operational at all times without administrative bypass. Computer systems must log who created, modified, or deleted records, along with exact UTC timestamps and documented reasons for change."),
            ("3. Storage and Cold-Chain Validation", "Regulatory authorities require validated temperature mapping and monitoring systems. Temperature boundaries must be supported by stability profiles. Temperature controlled materials must be stored within validated limits such as 2 to 8 °C for refrigerated biological inventory."),
            ("4. Inspection Readiness Strategy", "Inspection readiness requires proactive self-inspection and contemporaneous record reviews. Facilities must demonstrate robust change control and rapid access to unadulterated source documents."),
        ]
    },

    # -------------------------------------------------------------------------
    # 19. EQP-001
    # -------------------------------------------------------------------------
    "EQP-001": {
        "title": "Cold Storage Unit Equipment Manual",
        "subtitle": "Engineering and Maintenance Manual - Rev 1.0",
        "sections": [
            ("1. Equipment Identification and Architecture", "This manual governs industrial refrigeration units Unit-CR-01 and Unit-CR-02 manufactured for Novacure Labs. Authored by Vikram Shah, Production Manager, with maintenance schedules validated by Arjun Menon."),
            ("2. Temperature Control Loop and Tuning", "The refrigeration system is engineered to maintain target storage at 2 to 8 °C using redundant dual-stage scroll compressors and variable speed fan coils. Temperature feedback is captured via calibrated Pt100 RTD sensors."),
            ("3. Preventive Maintenance Routines", "Monthly maintenance includes inspection of evaporator coils, compressor oil levels, door gasket seals, and validation of automatic generator backup switchover circuits."),
            ("4. Emergency Response and Failsafe Modes", "In the event of compressor malfunction, secondary refrigeration circuits engage automatically within 60 seconds. Alarm sirens and SMS alerts trigger if compartment temperatures drift outside validated boundaries."),
        ]
    },

    # -------------------------------------------------------------------------
    # 20. STB-001
    # -------------------------------------------------------------------------
    "STB-001": {
        "title": "Stability Study Report: Vaccine Product Line",
        "subtitle": "Annual Long-Term Stability Evaluation - Rev 1.0",
        "sections": [
            ("1. Study Objective and Experimental Design", "This stability report summarizes long-term and accelerated stability testing for commercial vaccine product lots manufactured at Novacure Labs. Dr. Meera Iyer, QA Head, supervised the study and approved the stability protocol."),
            ("2. Storage Conditions and Assay Results", "Long-term stability lots were maintained at 2 to 8 °C in qualified walk-in cold chambers over a 36-month monitoring period. Potency, pH, sterility, and aggregate levels met all pre-specified acceptance criteria across all evaluated time points."),
            ("3. Thermal Stress Challenge Analysis", "Accelerated excursion testing showed that vaccine potency remains within specification during temporary thermal stress events, provided total cumulative excursion duration does not exceed validated critical thresholds."),
            ("4. Conclusion and Shelf-Life Recommendation", "Based on real-time 36-month stability data, the commercial shelf life is confirmed as 24 months when stored at 2 to 8 °C. Continued routine annual stability pull testing is mandated."),
        ]
    },
}
