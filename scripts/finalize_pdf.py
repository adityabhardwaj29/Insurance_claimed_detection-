"""
scripts/finalize_pdf.py
-----------------------
Stamps exact academic Roman/Arabic page numbers and injects complete
hierarchical PDF bookmarks/outline into docs/ACADEMIC_PROJECT_BLACKBOOK.pdf.
"""

import os
import pymupdf as fitz

pdf_path = "docs/ACADEMIC_PROJECT_BLACKBOOK.pdf"
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

doc = fitz.open(stream=pdf_bytes, filetype="pdf")
total_pages = len(doc)
print(f"Loaded {pdf_path} (in-memory) with {total_pages} pages.")

# 1. Page Numbering Stamping
# Preliminary Pages: index 1 to 11 (PDF Page 2 to 12) -> Roman 'ii' to 'xii'
# Chapter Pages: index 12 to 37 (PDF Page 13 to 38) -> Arabic '1' to '26'
roman_numerals = ["ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"]

for idx in range(total_pages):
    page = doc[idx]
    rect = page.rect
    width = rect.width
    height = rect.height

    # Footer rect: centered horizontally, 36 pt from bottom
    footer_rect = fitz.Rect(0, height - 38, width, height - 16)

    if idx == 0:
        # Cover page: no page number
        continue
    elif 1 <= idx <= 11:
        # Preliminary page
        roman_str = roman_numerals[idx - 1]
        page.insert_textbox(
            footer_rect,
            roman_str,
            fontname="times-roman",
            fontsize=10,
            color=(0.1, 0.1, 0.1),
            align=fitz.TEXT_ALIGN_CENTER
        )
    else:
        # Chapter page: starts at Arabic 1 on index 12 (PDF Page 13)
        arabic_num = idx - 12 + 1
        page.insert_textbox(
            footer_rect,
            str(arabic_num),
            fontname="times-roman",
            fontsize=10,
            color=(0.1, 0.1, 0.1),
            align=fitz.TEXT_ALIGN_CENTER
        )

print("Stamped Roman and Arabic footer page numbers.")

# 2. Hierarchical PDF Outline / Bookmarks (1-based PDF page indices)
toc = [
    [1, "Preliminary Pages", 2],
    [2, "Certificate", 2],
    [2, "Project Proposal Approval Proforma", 3],
    [2, "Abstract", 4],
    [2, "Acknowledgement", 5],
    [2, "Declaration", 6],
    [2, "Table of Contents", 7],
    [2, "List of Figures", 9],
    [2, "List of Tables", 10],
    [2, "List of Abbreviations", 11],
    [1, "CHAPTER 1: INTRODUCTION", 13],
    [2, "1.1 Background", 13],
    [2, "1.2 Problem Statement", 13],
    [2, "1.3 Significance of the Project", 14],
    [2, "1.4 Objectives", 14],
    [2, "1.5 Purpose and Scope", 15],
    [2, "1.6 Applicability", 16],
    [2, "1.7 Key Contributions", 16],
    [1, "CHAPTER 2: SYSTEM ANALYSIS", 17],
    [2, "2.1 Existing System & Limitations", 17],
    [2, "2.2 Proposed System Architecture", 17],
    [2, "2.3 Advantages of Proposed System", 18],
    [2, "2.4 Requirements Analysis", 18],
    [2, "2.5 Hardware & Software Specifications", 19],
    [2, "2.6 Technology Stack & Survey", 19],
    [2, "2.7 Feasibility Analysis", 20],
    [1, "CHAPTER 3: SYSTEM DESIGN", 21],
    [2, "3.1 System Architecture", 21],
    [2, "3.2 Module Division", 21],
    [2, "3.3 End-to-End Fraud Detection Workflow", 22],
    [2, "3.4 Feature Engineering Pipeline (38 Features)", 22],
    [2, "3.5 Composite Risk Assessment & Scoring", 23],
    [2, "3.6 Entity-Relationship (ER) Diagram", 24],
    [2, "3.7 Data Flow Diagram (Context DFD)", 24],
    [2, "3.8 UML Diagrams (Use Case, Class, State)", 24],
    [2, "3.9 Project Schedule & Gantt Chart", 26],
    [2, "3.10 Cloud Deployment Architecture", 26],
    [1, "CHAPTER 4: IMPLEMENTATION AND TESTING", 28],
    [2, "4.1 Development Environment & Tech Stack", 28],
    [2, "4.2 Implementation Highlights", 28],
    [2, "4.3 REST API Endpoints Specification", 28],
    [2, "4.4 Testing Methodology & Execution Matrix", 29],
    [1, "CHAPTER 5: RESULTS AND DISCUSSIONS", 32],
    [2, "5.1 Application Overview & Live Production Screenshots", 32],
    [2, "5.2 Supervised Fraud Model Benchmark Results", 33],
    [2, "5.3 Duplicate & Anomaly Detection Findings", 34],
    [2, "5.4 Knowledge Graph Structural Results", 34],
    [2, "5.5 Hybrid Risk Scoring Stratification", 34],
    [2, "5.6 Discussion & Defect Resolution Summary", 35],
    [2, "5.7 Limitations of Experimental Results", 35],
    [1, "CHAPTER 6: CONCLUSION AND FUTURE WORK", 36],
    [2, "6.1 Conclusion", 36],
    [2, "6.2 Key Findings", 36],
    [2, "6.3 Limitations", 36],
    [2, "6.4 Future Scope", 36],
    [2, "6.5 Industry Applications", 36],
    [1, "CHAPTER 7: REFERENCES", 38],
]

doc.set_toc(toc)
print(f"Set hierarchical outline with {len(toc)} bookmark entries.")

# Save finalized PDF directly
doc.save(pdf_path, garbage=4, deflate=True)
doc.close()
print(f"Successfully finalized and saved {pdf_path}")
