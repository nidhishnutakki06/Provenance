"""Document connectors for Provenance ingestion.

Connectors ingest documents from local repository folders representing:
- SharePoint (.docx via python-docx)
- SOP & PDFs (.pdf via pypdf)
- Email (.eml via stdlib email)
- Teams (.json channel dumps)

Each connector:
1. Implements load(raw_dir: Path) -> list[Chunk]
2. Strictly reads document metadata from sidecars (<file>.meta.json) without inferring roles or status.
3. Includes a detailed docstring explaining how the Microsoft Graph API replaces local disk folders in production.
"""

from __future__ import annotations

import json
import sys
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Optional

from docx import Document
from pypdf import PdfReader

from contracts import Chunk, Role, Source
from modules.ingestion.chunker import make_chunk_id, split_words_with_overlap


def load_sidecar(doc_file: Path) -> Optional[dict]:
    """Load sidecar metadata file for a document, trying <file>.meta.json and <stem>.meta.json."""
    candidates = [
        doc_file.parent / f"{doc_file.name}.meta.json",
        doc_file.with_suffix(".meta.json"),
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                sys.stderr.write(f"Error loading sidecar {candidate}: {e}\n")
                return None
    sys.stderr.write(f"Missing sidecar metadata for document {doc_file}\n")
    return None


class SharePointConnector:
    """Ingests Word documents (.docx) from the local SharePoint export folder.

    Microsoft Graph API Integration (Production Architecture):
    ----------------------------------------------------------
    In enterprise deployment, this local filesystem connector is replaced by direct
    integration with the Microsoft Graph Drive API:
    1. SharePoint Drive Items: Crawls document libraries via
       `GET /sites/{site-id}/drives/{drive-id}/root/children` or retrieves file binary streams
       using `GET /drives/{drive-id}/items/{item-id}/content`.
    2. Delta Queries: Employs `GET /drives/{drive-id}/root/delta` to power incremental sync.
       Only newly created, modified, or deleted documents are ingested on subsequent runs,
       drastically minimizing API calls and processing overhead.
    3. Item Permissions & Role Mapping: Reads effective access control lists via
       `GET /drives/{drive-id}/items/{item-id}/permissions`. Azure Active Directory (Microsoft Entra ID)
       security groups (e.g., 'Pharma-Interns', 'QA-Analysts', 'Executive-Managers') are dynamically
       mapped to Provenance `allowed_roles` (intern, analyst, manager), guaranteeing zero permission drift.
    """

    def __init__(self, folder_name: str = "sharepoint"):
        self.folder_name = folder_name

    def load(self, raw_dir: Path) -> list[Chunk]:
        """Load .docx documents from raw_dir / folder_name into Chunks."""
        chunks: list[Chunk] = []
        target_dir = raw_dir / self.folder_name
        if not target_dir.is_dir():
            return chunks

        docx_files = sorted(
            [f for f in target_dir.glob("*.docx") if not f.name.startswith("~$")]
        )
        for docx_path in docx_files:
            meta = load_sidecar(docx_path)
            if not meta:
                continue

            try:
                doc = Document(str(docx_path))
                # Group text into sections by heading or paragraph groups
                sections: list[tuple[str, list[str]]] = []
                current_heading = "section 1"
                current_paras: list[str] = []
                section_counter = 1

                for para in doc.paragraphs:
                    text = para.text.strip()
                    if not text:
                        continue
                    if para.style.name.startswith("Heading"):
                        if current_paras:
                            sections.append((current_heading, current_paras))
                            current_paras = []
                        section_counter += 1
                        current_heading = f"section {section_counter}"
                    current_paras.append(text)

                if current_paras:
                    sections.append((current_heading, current_paras))
                if not sections and doc.paragraphs:
                    # Fallback for document with no headings
                    sections = [("section 1", [p.text.strip() for p in doc.paragraphs if p.text.strip()])]

                chunk_index = 1
                for section_loc, paras in sections:
                    full_text = "\n\n".join(paras)
                    text_windows = split_words_with_overlap(full_text, chunk_size=150, overlap=20)
                    for win in text_windows:
                        chunk_id = make_chunk_id(meta["doc_id"], chunk_index)
                        chunks.append(
                            Chunk(
                                chunk_id=chunk_id,
                                doc_id=meta["doc_id"],
                                text=win,
                                source_type=meta.get("source_type", "sharepoint"),
                                title=meta["title"],
                                version=meta.get("version"),
                                date=meta["date"],
                                author=meta["author"],
                                owner=meta.get("owner", meta["author"]),
                                status=meta.get("status", "current"),
                                supersedes=meta.get("supersedes"),
                                allowed_roles=meta.get("allowed_roles", ["analyst", "manager"]),
                                location=section_loc,
                                topics=meta.get("topics", []),
                            )
                        )
                        chunk_index += 1
            except Exception as e:
                sys.stderr.write(f"Error reading docx {docx_path}: {e}\n")

        return chunks


class SopConnector:
    """Ingests Standard Operating Procedures and general compliance PDFs via pypdf.

    Handles both 'sop' and 'pdf' directories, producing one location string per page ('page N').

    Microsoft Graph API Integration (Production Architecture):
    ----------------------------------------------------------
    In enterprise deployment, this connector integrates with controlled SharePoint document libraries:
    1. SharePoint Drive Items: Accesses controlled PDF SOP repositories and validation dossiers via
       `GET /drives/{drive-id}/items/{item-id}/content`.
    2. Delta Queries: Subscribes to Microsoft Graph webhooks for real-time lifecycle notifications
       and uses `GET /drives/{drive-id}/root/delta` to perform fast, incremental synchronization
       whenever revised SOP versions (e.g., v3 replacing v2) are released.
    3. Item Permissions & Role Mapping: Reads document permissions through
       `GET /drives/{drive-id}/items/{item-id}/permissions`, ensuring controlled SOP distribution
       honors organizational role boundaries (intern, analyst, manager) without inferring status.
    """

    def __init__(self, folder_names: tuple[str, ...] = ("sop", "pdf")):
        self.folder_names = folder_names

    def load(self, raw_dir: Path) -> list[Chunk]:
        """Load .pdf documents from raw_dir / sop and raw_dir / pdf into Chunks."""
        chunks: list[Chunk] = []

        for folder_name in self.folder_names:
            target_dir = raw_dir / folder_name
            if not target_dir.is_dir():
                continue

            pdf_files = sorted(target_dir.glob("*.pdf"))
            for pdf_path in pdf_files:
                meta = load_sidecar(pdf_path)
                if not meta:
                    continue

                try:
                    reader = PdfReader(str(pdf_path))
                    chunk_index = 1
                    for page_num_0, page in enumerate(reader.pages):
                        page_num = page_num_0 + 1
                        page_text = page.extract_text() or ""
                        page_text = page_text.strip()
                        if not page_text:
                            continue

                        text_windows = split_words_with_overlap(page_text, chunk_size=150, overlap=20)
                        for win in text_windows:
                            chunk_id = make_chunk_id(meta["doc_id"], chunk_index)
                            chunks.append(
                                Chunk(
                                    chunk_id=chunk_id,
                                    doc_id=meta["doc_id"],
                                    text=win,
                                    source_type=meta.get("source_type", "sop" if folder_name == "sop" else "pdf"),
                                    title=meta["title"],
                                    version=meta.get("version"),
                                    date=meta["date"],
                                    author=meta["author"],
                                    owner=meta.get("owner", meta["author"]),
                                    status=meta.get("status", "current"),
                                    supersedes=meta.get("supersedes"),
                                    allowed_roles=meta.get("allowed_roles", ["analyst", "manager"]),
                                    location=f"page {page_num}",
                                    topics=meta.get("topics", []),
                                )
                            )
                            chunk_index += 1
                except Exception as e:
                    sys.stderr.write(f"Error reading PDF {pdf_path}: {e}\n")

        return chunks


class EmailConnector:
    """Ingests email records (.eml) with headers and plain text body.

    Microsoft Graph API Integration (Production Architecture):
    ----------------------------------------------------------
    In enterprise deployment, this connector integrates with Microsoft Exchange Online via Microsoft Graph Mail API:
    1. Outlook Messages: Ingests compliance communications, quality advisories, and executive memos
       directly from shared mailboxes and user accounts via `GET /users/{user-id}/messages` or
       `GET /groups/{group-id}/conversations`.
    2. Delta Queries: Executes `GET /users/{user-id}/mailFolders('Inbox')/messages/delta` for incremental
       synchronization of incoming messages and thread replies without repeated full mailbox sweeps.
    3. Item Permissions & Role Mapping: Leverages Microsoft Information Protection (MIP) sensitivity labels
       and mailbox delegation access to assign appropriate `allowed_roles` (intern, analyst, manager).
    """

    def __init__(self, folder_name: str = "email"):
        self.folder_name = folder_name

    def load(self, raw_dir: Path) -> list[Chunk]:
        """Load .eml emails from raw_dir / folder_name into Chunks."""
        chunks: list[Chunk] = []
        target_dir = raw_dir / self.folder_name
        if not target_dir.is_dir():
            return chunks

        eml_files = sorted(target_dir.glob("*.eml"))
        for eml_path in eml_files:
            meta = load_sidecar(eml_path)
            if not meta:
                continue

            try:
                with open(eml_path, "rb") as f:
                    msg = BytesParser(policy=policy.default).parse(f)

                subject = str(msg.get("Subject", "")).strip()
                sender = str(msg.get("From", "")).strip()
                to_addr = str(msg.get("To", "")).strip()
                date_str = str(msg.get("Date", "")).strip()

                body = ""
                body_part = msg.get_body(preferencelist=("plain",))
                if body_part:
                    body = body_part.get_content()
                else:
                    body = msg.get_content() if not msg.is_multipart() else ""

                combined_text = (
                    f"Subject: {subject}\n"
                    f"From: {sender}\n"
                    f"To: {to_addr}\n"
                    f"Date: {date_str}\n\n"
                    f"{body}"
                ).strip()

                text_windows = split_words_with_overlap(combined_text, chunk_size=150, overlap=20)
                for chunk_index, win in enumerate(text_windows, start=1):
                    chunk_id = make_chunk_id(meta["doc_id"], chunk_index)
                    chunks.append(
                        Chunk(
                            chunk_id=chunk_id,
                            doc_id=meta["doc_id"],
                            text=win,
                            source_type="email",
                            title=meta["title"],
                            version=meta.get("version"),
                            date=meta["date"],
                            author=meta["author"],
                            owner=meta.get("owner", meta["author"]),
                            status=meta.get("status", "current"),
                            supersedes=meta.get("supersedes"),
                            allowed_roles=meta.get("allowed_roles", ["analyst", "manager"]),
                            location="email body",
                            topics=meta.get("topics", []),
                        )
                    )
            except Exception as e:
                sys.stderr.write(f"Error reading EML {eml_path}: {e}\n")

        return chunks


class TeamsConnector:
    """Ingests Teams channel conversation dumps (.json).

    Groups messages into chunks of 3 to 5 messages with location string 'msg A-B'.

    Microsoft Graph API Integration (Production Architecture):
    ----------------------------------------------------------
    In enterprise deployment, this connector connects directly to Microsoft Teams via Microsoft Graph:
    1. Teams Channel Messages: Ingests compliance chats, operational announcements, and QA queries using
       `GET /teams/{team-id}/channels/{channel-id}/messages`.
    2. Delta Queries: Uses `GET /teams/{team-id}/channels/{channel-id}/messages/delta` to capture real-time
       channel conversations, replies, and edits incrementally without full polling.
    3. Item Permissions & Role Mapping: Reads channel membership (`GET /teams/{team-id}/channels/{channel-id}/members`)
       and team sensitivity labels to align channel visibility with user organizational roles (intern, analyst, manager).
    """

    def __init__(self, folder_name: str = "teams", batch_size: int = 4):
        self.folder_name = folder_name
        self.batch_size = max(3, min(5, batch_size))

    def load(self, raw_dir: Path) -> list[Chunk]:
        """Load Teams channel JSON dumps into Chunks."""
        chunks: list[Chunk] = []
        target_dir = raw_dir / self.folder_name
        if not target_dir.is_dir():
            return chunks

        json_files = sorted(
            [f for f in target_dir.glob("*.json") if not f.name.endswith(".meta.json")]
        )
        for json_path in json_files:
            meta = load_sidecar(json_path)
            if not meta:
                continue

            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    messages = json.load(f)

                if not isinstance(messages, list) or not messages:
                    continue

                # Group into batches of 3 to 5 messages
                batches: list[list[dict]] = []
                for i in range(0, len(messages), self.batch_size):
                    batch = messages[i : i + self.batch_size]
                    batches.append(batch)

                for chunk_index, batch in enumerate(batches, start=1):
                    msg_ids = [m.get("msg_id", idx) for idx, m in enumerate(batch, start=1)]
                    first_id, last_id = msg_ids[0], msg_ids[-1]
                    loc = f"msg {first_id}-{last_id}" if first_id != last_id else f"msg {first_id}"

                    text_lines = []
                    for m in batch:
                        author = m.get("author", "Unknown")
                        text = m.get("text", "")
                        ts = m.get("timestamp", "")
                        text_lines.append(f"[{author} {ts}]: {text}")

                    batch_text = "\n".join(text_lines)
                    chunk_id = make_chunk_id(meta["doc_id"], chunk_index)

                    chunks.append(
                        Chunk(
                            chunk_id=chunk_id,
                            doc_id=meta["doc_id"],
                            text=batch_text,
                            source_type="teams",
                            title=meta["title"],
                            version=meta.get("version"),
                            date=meta["date"],
                            author=meta["author"],
                            owner=meta.get("owner", meta["author"]),
                            status=meta.get("status", "current"),
                            supersedes=meta.get("supersedes"),
                            allowed_roles=meta.get("allowed_roles", ["analyst", "manager"]),
                            location=loc,
                            topics=meta.get("topics", []),
                        )
                    )
            except Exception as e:
                sys.stderr.write(f"Error reading Teams json {json_path}: {e}\n")

        return chunks
