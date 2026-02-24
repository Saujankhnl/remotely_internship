from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from io import BytesIO


def generate_professional_resume(profile, experiences, educations, projects, user):
    """Generate a professional resume PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.6*inch, rightMargin=0.6*inch)

    styles = getSampleStyleSheet()
    # Define custom styles
    name_style = ParagraphStyle('Name', parent=styles['Title'], fontSize=22, textColor=HexColor('#1a1a2e'), spaceAfter=4)
    headline_style = ParagraphStyle('Headline', parent=styles['Normal'], fontSize=11, textColor=HexColor('#4F46E5'), spaceAfter=8)
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'], fontSize=9, textColor=HexColor('#666666'), spaceAfter=12)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=13, textColor=HexColor('#1a1a2e'), spaceAfter=6, spaceBefore=12, borderWidth=0, borderPadding=0)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=4)
    sub_title_style = ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=11, textColor=HexColor('#333333'), spaceAfter=2, fontName='Helvetica-Bold')
    meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=9, textColor=HexColor('#888888'), spaceAfter=4)

    elements = []

    # Name
    elements.append(Paragraph(profile.full_name or user.username, name_style))

    # Headline
    if profile.headline:
        elements.append(Paragraph(profile.headline, headline_style))

    # Contact info line
    contact_parts = []
    if user.email: contact_parts.append(user.email)
    if profile.phone: contact_parts.append(profile.phone)
    if profile.location: contact_parts.append(profile.location)
    if contact_parts:
        elements.append(Paragraph(' | '.join(contact_parts), contact_style))

    # Links
    links = []
    if profile.linkedin: links.append(f'LinkedIn: {profile.linkedin}')
    if profile.github: links.append(f'GitHub: {profile.github}')
    if links:
        elements.append(Paragraph(' | '.join(links), meta_style))

    # Divider
    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#E5E7EB'), spaceAfter=8))

    # Summary/Bio
    if profile.bio:
        elements.append(Paragraph('PROFESSIONAL SUMMARY', section_style))
        elements.append(Paragraph(profile.bio, body_style))

    # Skills
    if profile.skills:
        elements.append(Paragraph('SKILLS', section_style))
        skills_list = [s.strip() for s in profile.skills.split(',') if s.strip()]
        elements.append(Paragraph(' &bull; '.join(skills_list), body_style))

    # Experience
    if experiences:
        elements.append(Paragraph('EXPERIENCE', section_style))
        for exp in experiences:
            date_range = ''
            if exp.start_date:
                date_range = exp.start_date.strftime('%b %Y')
                if exp.is_current:
                    date_range += ' - Present'
                elif exp.end_date:
                    date_range += f' - {exp.end_date.strftime("%b %Y")}'

            title_line = f'{exp.title}'
            if exp.company_name:
                title_line += f' at {exp.company_name}'
            elements.append(Paragraph(title_line, sub_title_style))

            meta_parts = []
            if date_range: meta_parts.append(date_range)
            if exp.location: meta_parts.append(exp.location)
            if exp.employment_type: meta_parts.append(exp.get_employment_type_display())
            if meta_parts:
                elements.append(Paragraph(' | '.join(meta_parts), meta_style))

            if exp.description:
                elements.append(Paragraph(exp.description, body_style))
            elements.append(Spacer(1, 4))

    # Education
    if educations:
        elements.append(Paragraph('EDUCATION', section_style))
        for edu in educations:
            title_line = ''
            if edu.degree:
                title_line = edu.degree
                if edu.field_of_study:
                    title_line += f' in {edu.field_of_study}'
            elements.append(Paragraph(title_line or edu.school, sub_title_style))

            meta_parts = [edu.school]
            if edu.start_year and edu.end_year:
                meta_parts.append(f'{edu.start_year} - {edu.end_year}')
            elif edu.end_year:
                meta_parts.append(str(edu.end_year))
            elements.append(Paragraph(' | '.join(meta_parts), meta_style))

            if edu.description:
                elements.append(Paragraph(edu.description, body_style))
            elements.append(Spacer(1, 4))

    # Projects
    if projects:
        elements.append(Paragraph('PROJECTS', section_style))
        for proj in projects:
            elements.append(Paragraph(proj.name, sub_title_style))
            if proj.technologies:
                elements.append(Paragraph(f'Technologies: {proj.technologies}', meta_style))
            if proj.description:
                elements.append(Paragraph(proj.description, body_style))
            if proj.url:
                elements.append(Paragraph(f'URL: {proj.url}', meta_style))
            elements.append(Spacer(1, 4))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_modern_resume(profile, experiences, educations, projects, user):
    """Modern template with color accent and two-column-like header"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.4*inch, bottomMargin=0.5*inch, leftMargin=0.6*inch, rightMargin=0.6*inch)

    styles = getSampleStyleSheet()
    name_style = ParagraphStyle('Name', parent=styles['Title'], fontSize=26, textColor=HexColor('#4F46E5'), spaceAfter=4)
    headline_style = ParagraphStyle('Headline', parent=styles['Normal'], fontSize=12, textColor=HexColor('#374151'), spaceAfter=8)
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'], fontSize=9, textColor=HexColor('#6B7280'), spaceAfter=12)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=12, textColor=HexColor('#4F46E5'), spaceAfter=6, spaceBefore=14, fontName='Helvetica-Bold')
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=4)
    sub_title_style = ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=11, textColor=HexColor('#111827'), spaceAfter=2, fontName='Helvetica-Bold')
    meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=9, textColor=HexColor('#9CA3AF'), spaceAfter=4)

    elements = []

    elements.append(Paragraph(profile.full_name or user.username, name_style))
    if profile.headline:
        elements.append(Paragraph(profile.headline, headline_style))

    contact_parts = []
    if user.email: contact_parts.append(user.email)
    if profile.phone: contact_parts.append(profile.phone)
    if profile.location: contact_parts.append(profile.location)
    if contact_parts:
        elements.append(Paragraph(' &#9670; '.join(contact_parts), contact_style))

    links = []
    if profile.linkedin: links.append(f'LinkedIn: {profile.linkedin}')
    if profile.github: links.append(f'GitHub: {profile.github}')
    if links:
        elements.append(Paragraph(' | '.join(links), meta_style))

    elements.append(HRFlowable(width="100%", thickness=2, color=HexColor('#4F46E5'), spaceAfter=10))

    if profile.bio:
        elements.append(Paragraph('About Me', section_style))
        elements.append(Paragraph(profile.bio, body_style))

    if profile.skills:
        elements.append(Paragraph('Technical Skills', section_style))
        skills_list = [s.strip() for s in profile.skills.split(',') if s.strip()]
        elements.append(Paragraph(' &middot; '.join(skills_list), body_style))

    if experiences:
        elements.append(Paragraph('Work Experience', section_style))
        for exp in experiences:
            date_range = ''
            if exp.start_date:
                date_range = exp.start_date.strftime('%b %Y')
                if exp.is_current:
                    date_range += ' &mdash; Present'
                elif exp.end_date:
                    date_range += f' &mdash; {exp.end_date.strftime("%b %Y")}'
            title_line = exp.title
            if exp.company_name:
                title_line += f' | {exp.company_name}'
            elements.append(Paragraph(title_line, sub_title_style))
            meta_parts = []
            if date_range: meta_parts.append(date_range)
            if exp.location: meta_parts.append(exp.location)
            if meta_parts:
                elements.append(Paragraph(' &middot; '.join(meta_parts), meta_style))
            if exp.description:
                elements.append(Paragraph(exp.description, body_style))
            elements.append(Spacer(1, 4))

    if educations:
        elements.append(Paragraph('Education', section_style))
        for edu in educations:
            title_line = edu.degree if edu.degree else edu.school
            if edu.field_of_study:
                title_line += f' &mdash; {edu.field_of_study}'
            elements.append(Paragraph(title_line, sub_title_style))
            meta_parts = [edu.school]
            if edu.start_year and edu.end_year:
                meta_parts.append(f'{edu.start_year}&ndash;{edu.end_year}')
            elements.append(Paragraph(' &middot; '.join(meta_parts), meta_style))
            if edu.description:
                elements.append(Paragraph(edu.description, body_style))
            elements.append(Spacer(1, 4))

    if projects:
        elements.append(Paragraph('Projects', section_style))
        for proj in projects:
            elements.append(Paragraph(proj.name, sub_title_style))
            if proj.technologies:
                elements.append(Paragraph(f'Tech: {proj.technologies}', meta_style))
            if proj.description:
                elements.append(Paragraph(proj.description, body_style))
            elements.append(Spacer(1, 4))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_minimal_resume(profile, experiences, educations, projects, user):
    """Clean minimal template"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.7*inch, rightMargin=0.7*inch)

    styles = getSampleStyleSheet()
    name_style = ParagraphStyle('Name', parent=styles['Title'], fontSize=20, textColor=HexColor('#000000'), spaceAfter=2, fontName='Helvetica-Bold')
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'], fontSize=9, textColor=HexColor('#555555'), spaceAfter=10)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=11, textColor=HexColor('#000000'), spaceAfter=4, spaceBefore=10, fontName='Helvetica-Bold', borderWidth=0)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=13, spaceAfter=3)
    sub_title_style = ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=10, spaceAfter=1, fontName='Helvetica-Bold')
    meta_style = ParagraphStyle('Meta', parent=styles['Normal'], fontSize=9, textColor=HexColor('#777777'), spaceAfter=3)

    elements = []

    elements.append(Paragraph(profile.full_name or user.username, name_style))
    contact_parts = []
    if user.email: contact_parts.append(user.email)
    if profile.phone: contact_parts.append(profile.phone)
    if profile.location: contact_parts.append(profile.location)
    if profile.linkedin: contact_parts.append(profile.linkedin)
    if contact_parts:
        elements.append(Paragraph(' | '.join(contact_parts), contact_style))

    elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#CCCCCC'), spaceAfter=6))

    if profile.bio:
        elements.append(Paragraph('Summary', section_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#EEEEEE'), spaceAfter=4))
        elements.append(Paragraph(profile.bio, body_style))

    if profile.skills:
        elements.append(Paragraph('Skills', section_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#EEEEEE'), spaceAfter=4))
        elements.append(Paragraph(profile.skills, body_style))

    if experiences:
        elements.append(Paragraph('Experience', section_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#EEEEEE'), spaceAfter=4))
        for exp in experiences:
            date_range = ''
            if exp.start_date:
                date_range = exp.start_date.strftime('%b %Y')
                if exp.is_current:
                    date_range += ' - Present'
                elif exp.end_date:
                    date_range += f' - {exp.end_date.strftime("%b %Y")}'
            title_line = exp.title
            if exp.company_name:
                title_line += f', {exp.company_name}'
            elements.append(Paragraph(title_line, sub_title_style))
            if date_range:
                elements.append(Paragraph(date_range, meta_style))
            if exp.description:
                elements.append(Paragraph(exp.description, body_style))
            elements.append(Spacer(1, 3))

    if educations:
        elements.append(Paragraph('Education', section_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#EEEEEE'), spaceAfter=4))
        for edu in educations:
            title_line = f'{edu.degree} - {edu.school}' if edu.degree else edu.school
            elements.append(Paragraph(title_line, sub_title_style))
            if edu.end_year:
                elements.append(Paragraph(str(edu.end_year), meta_style))
            elements.append(Spacer(1, 3))

    if projects:
        elements.append(Paragraph('Projects', section_style))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#EEEEEE'), spaceAfter=4))
        for proj in projects:
            elements.append(Paragraph(proj.name, sub_title_style))
            if proj.description:
                elements.append(Paragraph(proj.description, body_style))
            elements.append(Spacer(1, 3))

    doc.build(elements)
    buffer.seek(0)
    return buffer


TEMPLATE_GENERATORS = {
    'professional': generate_professional_resume,
    'modern': generate_modern_resume,
    'minimal': generate_minimal_resume,
}
