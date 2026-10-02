"""
scripts/viva_helpers.py
-----------------------
Utility module to create styled docx elements:
- Page setup (A4, standard margins)
- Header / Footer with page numbers
- Headings with academic colors
- Callout boxes (VIVA ANSWER, IMPORTANT, EXAMINER MAY ASK, COMMON MISTAKE, etc.)
- Beautiful styled tables with colored headers and alternating rows
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# Color Palette Constants
COLOR_NAVY = RGBColor(15, 44, 89)      # #0F2C59 (Main Titles & Headers)
COLOR_SLATE = RGBColor(30, 58, 138)    # #1E3A8A (Section Titles)
COLOR_CHARCOAL = RGBColor(34, 34, 34)  # #222222 (Body Text)
COLOR_MUTED = RGBColor(71, 85, 105)    # #475569 (Secondary / Labels)
COLOR_GREEN = RGBColor(16, 185, 129)   # #10B981 (Viva Dialogue)
COLOR_AMBER = RGBColor(217, 119, 6)    # #D97706 (Warnings / Remember)
COLOR_RED = RGBColor(220, 38, 38)      # #DC2626 (Mistakes)
COLOR_PURPLE = RGBColor(139, 92, 246)  # #8B5CF6 (Examiner Questions)

HEX_NAVY = "0F2C59"
HEX_SLATE = "1E3A8A"
HEX_BORDER = "CBD5E1"
HEX_ZEBRA = "F8FAFC"

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner padding for a table cell in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{margin_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex):
    """Apply background color to a cell."""
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_left_border(cell, color_hex, size="36"):
    """Set custom thick left border on callout boxes and remove top/right/bottom."""
    borders_xml = f'''
    <w:tcBorders {nsdecls("w")}>
        <w:top w:val="none"/>
        <w:left w:val="single" w:sz="{size}" w:space="0" w:color="{color_hex}"/>
        <w:bottom w:val="none"/>
        <w:right w:val="none"/>
    </w:tcBorders>
    '''
    cell._tc.get_or_add_tcPr().append(parse_xml(borders_xml))

def setup_document():
    """Initializes Document with A4 dimensions and standard margins."""
    doc = docx.Document()
    
    # Page setup: A4
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.15)
        section.right_margin = Inches(1.0)

        # Header
        header = section.header
        header_p = header.paragraphs[0]
        header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = header_p.add_run("BDS VIVA PREPARATION GUIDE — Insurance Claim Fraud Detection")
        hrun.font.name = "Times New Roman"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = COLOR_MUTED

        # Footer
        footer = section.footer
        footer_p = footer.paragraphs[0]
        footer_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        frun = footer_p.add_run("Aditya Bhardwaj (Roll: TDDS003A)  |  Bachelor of Data Science (Semester V)")
        frun.font.name = "Times New Roman"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = COLOR_MUTED

    # Normal Style configuration
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(11)
    font.color.rgb = COLOR_CHARCOAL
    style.paragraph_format.line_spacing = 1.15
    style.paragraph_format.space_after = Pt(4)
    style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    return doc

def add_title(doc, text, subtitle=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(20)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY

    if subtitle:
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(16)
        r2 = p2.add_run(subtitle)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(12)
        r2.font.bold = True
        r2.font.color.rgb = COLOR_SLATE

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(15)
    run.font.bold = True
    run.font.color.rgb = COLOR_NAVY
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = COLOR_SLATE
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11.5)
    run.font.bold = True
    run.font.color.rgb = COLOR_CHARCOAL
    return p

def add_body(doc, text, bold_prefix=""):
    p = doc.add_paragraph()
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_NAVY
    r = p.add_run(text)
    return p

def add_bullet(doc, text, bold_prefix=""):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.bold = True
        r_pre.font.color.rgb = COLOR_NAVY
    r = p.add_run(text)
    return p

def add_callout(doc, box_type, text, title=None):
    """
    Creates a distinct callout block with custom border and shading.
    box_type can be:
    - 'VIVA ANSWER': Green
    - 'IMPORTANT': Amber
    - 'REMEMBER': Blue/Navy
    - 'EXAMINER MAY ASK': Purple
    - 'COMMON MISTAKE': Red
    - 'TECHNICAL EXPLANATION': Slate
    - 'SIMPLE HINGLISH EXPLANATION': Teal
    """
    configs = {
        'VIVA ANSWER': {'border': '10B981', 'bg': 'ECFDF5', 'icon': '🗣️ VIVA MEIN KAISE BOLNA HAI:', 'color': RGBColor(6, 95, 70)},
        'IMPORTANT': {'border': 'F59E0B', 'bg': 'FFFBEB', 'icon': '⚠️ IMPORTANT FOR VIVA:', 'color': RGBColor(146, 64, 14)},
        'REMEMBER': {'border': '0F2C59', 'bg': 'F1F5F9', 'icon': '📌 REMEMBER:', 'color': RGBColor(15, 44, 89)},
        'EXAMINER MAY ASK': {'border': '8B5CF6', 'bg': 'F5F3FF', 'icon': '❓ EXAMINER CROSS-QUESTION:', 'color': RGBColor(91, 33, 182)},
        'COMMON MISTAKE': {'border': 'EF4444', 'bg': 'FEF2F2', 'icon': '❌ DON\'T SAY (COMMON MISTAKE):', 'color': RGBColor(153, 27, 27)},
        'TECHNICAL EXPLANATION': {'border': '3B82F6', 'bg': 'EFF6FF', 'icon': '🔬 TECHNICAL DEFINITION:', 'color': RGBColor(30, 64, 175)},
        'SIMPLE HINGLISH EXPLANATION': {'border': '0D9488', 'bg': 'F0FDFA', 'icon': '💡 SIMPLE HINGLISH SAMJHANE KE LIYE:', 'color': RGBColor(17, 94, 89)},
    }
    
    cfg = configs.get(box_type, configs['REMEMBER'])
    
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.1)
    set_cell_margins(cell, top=100, bottom=100, left=160, right=140)
    set_cell_shading(cell, cfg['bg'])
    set_cell_left_border(cell, cfg['border'], size="32")
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    hdr_label = title if title else cfg['icon']
    r_hdr = p.add_run(f"{hdr_label}\n")
    r_hdr.font.bold = True
    r_hdr.font.size = Pt(10)
    r_hdr.font.color.rgb = cfg['color']
    
    r_txt = p.add_run(text)
    r_txt.font.size = Pt(10.5)
    r_txt.font.italic = (box_type == 'VIVA ANSWER')
    
    # Add empty paragraph after table for spacing
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(4)

def add_table_data(doc, arg1, arg2=None, col_widths=None):
    """Creates a beautifully formatted academic data table.
    Supports either:
      add_table_data(doc, headers, rows, col_widths)
    OR
      add_table_data(doc, full_table_matrix, col_widths)
    """
    if isinstance(arg2, (list, tuple)) and (len(arg2) == 0 or isinstance(arg2[0], (int, float))):
        # Called as (doc, full_matrix, col_widths)
        headers = arg1[0]
        rows = arg1[1:]
        col_widths = arg2
    elif arg2 is None:
        headers = arg1[0]
        rows = arg1[1:]
    else:
        # Called as (doc, headers, rows, col_widths)
        headers = arg1
        rows = arg2

    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    # Header row
    hdr_row = tbl.rows[0]
    for i, h_text in enumerate(headers):
        cell = hdr_row.cells[i]
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        set_cell_shading(cell, HEX_NAVY)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(h_text)
        r.font.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    # Data rows
    for r_idx, row_data in enumerate(rows):
        row = tbl.rows[r_idx + 1]
        bg = HEX_ZEBRA if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            set_cell_margins(cell, top=70, bottom=70, left=120, right=120)
            set_cell_shading(cell, bg)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(str(val))
            r.font.size = Pt(9)

    # Set column widths if provided
    if col_widths:
        for row in tbl.rows:
            for c_idx, w in enumerate(col_widths):
                row.cells[c_idx].width = Inches(w)

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(4)

def add_qa_card(doc, arg1, arg2, arg3, arg4, arg5=None):
    """Adds a full 4-part structured viva question card.
    Supports either:
      add_qa_card(doc, question_text, short_ans, detailed_ans, viva_ans)
    OR
      add_qa_card(doc, q_num, question_text, short_ans, detailed_ans, viva_ans)
    """
    if arg5 is None:
        question_text = str(arg1)
        short_ans = str(arg2)
        detailed_ans = str(arg3)
        viva_ans = str(arg4)
    else:
        question_text = f"Q{arg1}. {arg2}"
        short_ans = str(arg3)
        detailed_ans = str(arg4)
        viva_ans = str(arg5)

    add_heading_3(doc, question_text)
    
    # Short Answer
    p_short = doc.add_paragraph()
    r_s_lbl = p_short.add_run("Short Answer: ")
    r_s_lbl.font.bold = True
    r_s_lbl.font.color.rgb = COLOR_NAVY
    p_short.add_run(short_ans)
    
    # Detailed Technical Answer
    p_det = doc.add_paragraph()
    r_d_lbl = p_det.add_run("Technical Explanation: ")
    r_d_lbl.font.bold = True
    r_d_lbl.font.color.rgb = COLOR_SLATE
    p_det.add_run(detailed_ans)
    
    # Viva Dialogue Callout
    add_callout(doc, "VIVA ANSWER", viva_ans, title="🗣️ VIVA MEIN EXAMINER KO AISE BOLO:")
