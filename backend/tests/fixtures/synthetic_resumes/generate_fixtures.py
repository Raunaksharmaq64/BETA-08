"""
RIGHT FIT — Synthetic Resume Fixture Generator
Generates realistic, non-real-person synthetic PDF and DOCX files for automated regression testing.
"""

from __future__ import annotations

import io
from pathlib import Path
import docx
import fitz  # PyMuPDF

FIXTURES_DIR = Path(__file__).resolve().parent


def create_standard_one_page_pdf(path: Path):
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)  # Standard Letter

    text = """JANE DOE
Email: jane.doe@example.com | Phone: (555) 123-4567
LinkedIn: linkedin.com/in/janedoe | GitHub: github.com/janedoe

PROFESSIONAL SUMMARY
Senior Backend Engineer with 6+ years of experience designing scalable microservices in Python and Go.
Architected distributed systems handling 50M requests daily with 99.99% uptime.

WORK EXPERIENCE
TechCorp Solutions | Senior Software Engineer | 2021 - Present
- Led migration of legacy monolith to FastAPI microservices, reducing API response latency by 35%.
- Architected Redis caching layer that cut database query load by 40% across 5M daily queries.
- Automated CI/CD deployment pipelines using Docker and Kubernetes, reducing release time from 4 hours to 15 minutes.

DataFlow Inc | Software Engineer | 2018 - 2021
- Developed payment processing gateway in Python and PostgreSQL processing $10M in monthly transactions.
- Designed REST APIs for 100k active mobile users with automated unit and integration tests.

EDUCATION
Stanford University | B.S. in Computer Science | 2014 - 2018
GPA: 3.85 / 4.0

TECHNICAL SKILLS
Languages: Python, Go, TypeScript, SQL
Frameworks: FastAPI, Django, React, Next.js, Node.js
Databases: PostgreSQL, Redis, MongoDB
Cloud & Tools: AWS, Docker, Kubernetes, Git, CI/CD, Linux

PROJECTS
CloudQueue: High-throughput async message broker built with Go and Redis.
DevMetrics: Developer telemetry dashboard built with Next.js and PostgreSQL.

CERTIFICATIONS
AWS Certified Solutions Architect - Associate
"""
    page.insert_text(fitz.Point(54, 54), text, fontsize=10, fontname="helv")
    doc.save(str(path))
    doc.close()


def create_multi_page_pdf(path: Path):
    doc = fitz.open()
    # Page 1
    p1 = doc.new_page(width=612, height=792)
    p1_text = """ALEX SMITH
Email: alex.smith@example.org | Phone: (555) 987-6543
LinkedIn: linkedin.com/in/alexsmith | GitHub: github.com/alexsmith

SUMMARY
Principal Software Architect specializing in cloud infrastructure, high-throughput streaming systems, and engineering leadership.

WORK EXPERIENCE
CloudScale Systems | Principal Architect | 2020 - Present
- Spearheaded company-wide cloud transformation to AWS, cutting annual infrastructure spend by $1.2M.
- Designed event-driven Kafka pipelines processing 200,000 events/sec with sub-second latency.
- Mentored 15 senior engineers across 3 distributed engineering squads in an Agile environment.

AlphaTech Industries | Staff Engineer | 2016 - 2020
- Built distributed search cluster with Elasticsearch handling 20TB index and 15,000 queries per second.
- Championed automated code quality standards and test-driven development across 40 developers.
"""
    p1.insert_text(fitz.Point(54, 54), p1_text, fontsize=10, fontname="helv")

    # Page 2
    p2 = doc.new_page(width=612, height=792)
    p2_text = """ALEX SMITH — PAGE 2

WORK EXPERIENCE (CONTINUED)
BetaCorp Labs | Systems Software Engineer | 2012 - 2016
- Developed high-performance network proxy in C++ and Linux kernel sockets.

EDUCATION
Massachusetts Institute of Technology | M.S. in Computer Science | 2010 - 2012
University of California, Berkeley | B.S. in Electrical Engineering and Computer Science | 2006 - 2010

TECHNICAL SKILLS
Languages: Python, Rust, C++, Java, SQL
Cloud & Infrastructure: AWS, GCP, Terraform, Kubernetes, Docker, Prometheus
Databases: PostgreSQL, Cassandra, Redis, Elasticsearch
Tools: Git, Linux, Kafka, Datadog

CERTIFICATIONS
Certified Kubernetes Administrator (CKA)
HashiCorp Certified Terraform Associate
"""
    p2.insert_text(fitz.Point(54, 54), p2_text, fontsize=10, fontname="helv")
    doc.save(str(path))
    doc.close()


def create_missing_sections_pdf(path: Path):
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    # Missing summary, projects, certifications
    text = """MARK JOHNSON
Email: mark.j@example.net | Phone: (555) 333-4444

EDUCATION
University of Washington | B.S. in Informatics | 2019 - 2023

SKILLS
Languages: Python, JavaScript, SQL
Tools: Git, Docker, Linux

WORK EXPERIENCE
Acme Software | Junior Developer | 2023 - Present
- Maintained REST endpoints in FastAPI and PostgreSQL.
"""
    page.insert_text(fitz.Point(54, 54), text, fontsize=10, fontname="helv")
    doc.save(str(path))
    doc.close()


def create_empty_pdf(path: Path):
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    # Page with zero text
    doc.save(str(path))
    doc.close()


def create_corrupted_pdf(path: Path):
    # Starts with %PDF- but followed by invalid binary noise
    with open(path, "wb") as f:
        f.write(b"%PDF-1.7\nCorrupted binary payload\x00\xff\xfe\x00\x01\x02not_a_valid_pdf_trailer")


def create_password_protected_pdf(path: Path):
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text(fitz.Point(54, 54), "CONFIDENTIAL RESUME ENCRYPTED", fontsize=12)
    # Encrypt document with user password
    perm = int(
        fitz.PDF_PERM_ACCESSIBILITY
        | fitz.PDF_PERM_PRINT
        | fitz.PDF_PERM_COPY
        | fitz.PDF_PERM_ANNOTATE
    )
    doc.save(
        str(path),
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw="secret",
        owner_pw="master_secret",
        permissions=perm
    )
    doc.close()


def create_standard_docx(path: Path):
    doc = docx.Document()
    doc.add_heading("EMILY DAVIS", level=0)
    doc.add_paragraph("Email: emily.davis@example.org | Phone: (555) 444-5555 | GitHub: github.com/emilydavis")

    doc.add_heading("PROFESSIONAL SUMMARY", level=1)
    doc.add_paragraph("Full-Stack Web Developer with 4 years of experience building React and FastAPI web applications.")

    doc.add_heading("WORK EXPERIENCE", level=1)
    p = doc.add_paragraph("NextGen Web Studios | Full-Stack Developer | 2021 - Present")
    doc.add_paragraph("• Developed reactive dashboards using React, Next.js, and Tailwind CSS serving 50k users.")
    doc.add_paragraph("• Implemented FastAPI backend APIs with PostgreSQL database and Redis session caching.")

    doc.add_heading("EDUCATION", level=1)
    doc.add_paragraph("University of Michigan | B.S. in Computer Science | 2017 - 2021")

    doc.add_heading("TECHNICAL SKILLS", level=1)
    # Table of skills
    table = doc.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Category"
    hdr_cells[1].text = "Skills"
    row = table.add_row().cells
    row[0].text = "Languages"
    row[1].text = "Python, TypeScript, JavaScript, HTML, CSS"
    row = table.add_row().cells
    row[0].text = "Frameworks & DB"
    row[1].text = "FastAPI, React, Next.js, PostgreSQL, Redis"

    doc.save(str(path))


def create_corrupted_docx(path: Path):
    # Starts with PK\x03\x04 but corrupted zip
    with open(path, "wb") as f:
        f.write(b"PK\x03\x04\x00\x00corrupted_zip_bytes_that_fail_openxml_parsing")


def create_malicious_file(path: Path):
    with open(path, "wb") as f:
        f.write(b"MZ\x90\x00\x03\x00\x00\x00This is a simulated executable file header")


def generate_all_fixtures():
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    create_standard_one_page_pdf(FIXTURES_DIR / "standard_one_page.pdf")
    create_multi_page_pdf(FIXTURES_DIR / "multi_page.pdf")
    create_missing_sections_pdf(FIXTURES_DIR / "missing_sections.pdf")
    create_empty_pdf(FIXTURES_DIR / "empty.pdf")
    create_corrupted_pdf(FIXTURES_DIR / "corrupted.pdf")
    create_password_protected_pdf(FIXTURES_DIR / "password_protected.pdf")
    create_standard_docx(FIXTURES_DIR / "standard_resume.docx")
    create_corrupted_docx(FIXTURES_DIR / "corrupted_resume.docx")
    create_malicious_file(FIXTURES_DIR / "malicious.exe")
    print(f"Generated all synthetic fixtures in {FIXTURES_DIR}")


if __name__ == "__main__":
    generate_all_fixtures()

