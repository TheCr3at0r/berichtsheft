import io
import os
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen.canvas import Canvas

from .models import Logbook
from datetime import date, timedelta

font_path = os.path.join(settings.STATIC_ROOT, "fonts", "Roboto-Regular.ttf")
pdfmetrics.registerFont(TTFont("Roboto", font_path))


def add_page_number(canvas: Canvas, doc):
    page_num = canvas.getPageNumber()
    canvas.setFont("Roboto", 12)
    canvas.drawRightString(A4[0] - doc.rightMargin, doc.bottomMargin / 2, f"{page_num}")


def build_week_table(week, styles):
    data = []
    table_style = []

    if week.entries.filter(category="OPS").exists():
        data.append(["Betriebliche Tätigkeiten", "Stunden"])
        for t in week.entries.filter(category="OPS"):
            if (
                t.name in ["Krank", "Urlaub", "Frei"]
                or "Feiertag" in t.name
                or "Abschlussprüfung" in t.name
            ):
                t.hours = f"{(t.hours / 8):.0f}".strip()
                t.hours += " Tage" if t.hours != "1" else " Tag"
            data.append([t.name, (f"{t.hours}" if type(t.hours) is float else t.hours)])
        table_style += [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
            ("TOPPADDING", (0, 0), (-1, 0), 5),
        ]

    if week.entries.filter(category="TRAIN").exists():
        data.append(["Unterweisungen / Schulungen", "Stunden"])
        for t in week.entries.filter(category="TRAIN"):
            if (
                t.name in ["Krank", "Urlaub", "Frei"]
                or "Feiertag" in t.name
                or "Abschlussprüfung" in t.name
            ):
                t.hours = f"{(t.hours / 8):.0f}".strip()
                t.hours += " Tage" if t.hours != "1" else " Tag"
            data.append([t.name, (f"{t.hours}" if type(t.hours) is float else t.hours)])
        table_style += [
            (
                "BACKGROUND",
                (0, len(week.entries.filter(category="OPS")) + 1),
                (-1, len(week.entries.filter(category="OPS")) + 1),
                colors.lightgrey,
            ),
            (
                "LINEBELOW",
                (0, len(week.entries.filter(category="OPS")) + 1),
                (-1, len(week.entries.filter(category="OPS")) + 1),
                0.5,
                colors.black,
            ),
            (
                "BOTTOMPADDING",
                (0, len(week.entries.filter(category="OPS")) + 1),
                (-1, len(week.entries.filter(category="OPS")) + 1),
                5,
            ),
            (
                "TOPPADDING",
                (0, len(week.entries.filter(category="OPS")) + 1),
                (-1, len(week.entries.filter(category="OPS")) + 1),
                5,
            ),
        ]
        if len(data) - len(week.entries.filter(category="OPS")) + 1 > 0:
            table_style.append(
                (
                    "LINEABOVE",
                    (0, len(week.entries.filter(category="OPS")) + 1),
                    (-1, len(week.entries.filter(category="OPS")) + 1),
                    0.5,
                    colors.black,
                )
            )

    if week.entries.filter(category="VOCAT").exists():
        data.append(["Berufsschulthemen", "Stunden"])
        for t in week.entries.filter(category="VOCAT"):
            if (
                t.name in ["Krank", "Urlaub", "Frei"]
                or "Feiertag" in t.name
                or "Abschlussprüfung" in t.name
            ):
                t.hours = f"{(t.hours / 8):.0f}".strip()
                t.hours += " Tage" if t.hours != "1" else " Tag"
            data.append([t.name, (f"{t.hours}" if type(t.hours) is float else t.hours)])
        table_style += [
            (
                "BACKGROUND",
                (0, len(data) - len(week.entries.filter(category="VOCAT")) - 1),
                (-1, len(data) - len(week.entries.filter(category="VOCAT")) - 1),
                colors.lightgrey,
            ),
            (
                "LINEBELOW",
                (0, len(data) - len(week.entries.filter(category="VOCAT")) - 1),
                (-1, len(data) - len(week.entries.filter(category="VOCAT")) - 1),
                0.5,
                colors.black,
            ),
            (
                "BOTTOMPADDING",
                (0, len(data) - len(week.entries.filter(category="VOCAT")) - 1),
                (-1, len(data) - len(week.entries.filter(category="VOCAT")) - 1),
                5,
            ),
            (
                "TOPPADDING",
                (0, len(data) - len(week.entries.filter(category="VOCAT")) - 1),
                (-1, len(data) - len(week.entries.filter(category="VOCAT")) - 1),
                5,
            ),
        ]
        if len(data) - len(week.entries.filter(category="VOCAT")) - 1 > 0:
            table_style.append(
                (
                    "LINEABOVE",
                    (0, len(data) - len(week.entries.filter(category="VOCAT")) - 1),
                    (-1, len(data) - len(week.entries.filter(category="VOCAT")) - 1),
                    0.5,
                    colors.black,
                )
            )

    table = Table(data, colWidths=[400, 100], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                *table_style,
                ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, -1), "Roboto"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("LINEBEFORE", (-1, 0), (-1, -1), 0.5, colors.black),
            ]
        )
    )
    return table


def create_signature_table(signature_date):
    date_str = signature_date.strftime("%d.%m.%Y")
    date_style = ParagraphStyle(
        name="sig_date", fontName="Roboto", fontSize=10, alignment=1  # zentriert
    )
    sig_style = ParagraphStyle(
        name="sig_text",
        parent=date_style,
        alignment=0,
        textColor=colors.grey,
        fontSize=11,
    )
    student_sig_path = os.path.join(
        settings.STATIC_ROOT, "images", "signature_student.png"
    )
    trainer_sig_path = os.path.join(
        settings.STATIC_ROOT, "images", "signature_trainer.png"
    )

    student_img = (
        Image(student_sig_path, width=120, height=30)
        if os.path.exists(student_sig_path)
        else ""
    )
    trainer_img = (
        Image(trainer_sig_path, width=120, height=30)
        if os.path.exists(trainer_sig_path)
        else ""
    )
    student_cell = Table(
        [[Paragraph(date_str, date_style), student_img]],
        colWidths=[75, 50],
    )
    trainer_cell = Table(
        [[Paragraph(date_str, date_style), trainer_img]],
        colWidths=[75, 50],
    )

    data = [
        [student_cell, "", trainer_cell],
        [
            Paragraph("Datum, Unterschrift Auszubildende/r", sig_style),
            "",
            Paragraph("Datum, Unterschrift Ausbildende/r oder Ausbilder/in", sig_style),
        ],
        [
            Paragraph("Zur Kenntnis genommen:", sig_style),
            "",
            Paragraph("Sonstige Sichtvermerke:", sig_style),
        ],
        [
            Paragraph("Datum, Unterschrift gesetzliche/r Vertreter/in", sig_style),
            "",
            Paragraph("Datum, Unterschrift Betriebsrat", sig_style),
        ],
        [
            "",
            "",
            Paragraph("Datum, Unterschrift Berufsschule", sig_style),
        ],
    ]

    col_widths = [225, 50, 225]
    tbl = Table(data, colWidths=col_widths, hAlign="LEFT")
    tbl.setStyle(
        TableStyle(
            [
                ("LINEBELOW", (0, 0), (0, 0), 1, colors.grey),
                ("LINEBELOW", (2, 0), (2, 0), 1, colors.grey),
                ("VALIGN", (0, 1), (-1, 1), "TOP"),
                ("VALIGN", (0, 3), (-1, 3), "TOP"),
                ("LINEABOVE", (0, 3), (0, 3), 1, colors.grey),
                ("LINEABOVE", (2, 3), (2, 3), 1, colors.grey),
                ("LINEABOVE", (2, 4), (2, 4), 1, colors.grey),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 30),
            ]
        )
    )
    return tbl


def generate_logbook_pdf(logbook: Logbook) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=60,
        bottomMargin=60,
    )
    # Styles setup
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = "Roboto"

    story = []
    # Cover page

    logo_path = os.path.join(settings.STATIC_ROOT, "images", "logo.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=150, height=40)
        logo.hAlign = "RIGHT"
        story.append(logo)
        story.append(Spacer(1, 20))

    story.append(Paragraph("Ausbildungsnachweis", styles["Title"]))
    story.append(Spacer(1, 12))

    cover_table_data = []
    for field, name in [
        ("student_name", "Name"),
        ("student_address", "Adresse"),
        ("profession", "Ausbildungsberuf"),
        ("specialty", "Fachrichtung/Schwerpunkt"),
        ("company", "Ausbildungsbetrieb"),
        ("trainer_name", "Verantwortliche/r Ausbilder/in"),
    ]:
        if hasattr(logbook, field):
            value = getattr(logbook, field)
            cover_table_data.append((name, value))
    cover_table_data.append(("Beginn der Ausbildung", f"01.09.{logbook.start_year}"))
    cover_table_data.append(("Ende der Ausbildung", f"30.08.{logbook.start_year+3}"))
    story.append(
        Table(
            cover_table_data,
            colWidths=[200, 300],
            style=[
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTNAME", (0, 0), (-1, -1), "Roboto"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
            ],
        )
    )
    story.append(PageBreak())

    for year in logbook.years.all():
        # start_date is always the first of september
        # when it falls on the weekend, its the monday after
        # end_date is always the friday after the start_date
        start_date = date(
            year=logbook.start_year + year.year_number - 1, month=9, day=1
        )
        if start_date.weekday() > 4:
            start_date += timedelta(days=7 - start_date.weekday())
        end_date = start_date + timedelta(days=4 - start_date.weekday())
        for week in year.weeks.all():
            if week.week_number != 1:
                start_date = end_date + timedelta(days=3)
                end_date = start_date + timedelta(days=4 - start_date.weekday())
            signature_date = end_date + timedelta(days=(0 - end_date.weekday()) % 7)

            story.append(
                Table(
                    [
                        ("Ausbildungsnachweis (wöchentlich)", logo),
                        ("Name des Auszubildenden:", logbook.student_name),
                        ("Ausbildungsjahr", year.year_number),
                        (
                            "Ausbildungswoche vom:",
                            f"{start_date.strftime("%d.%m.%Y")} bis {end_date.strftime("%d.%m.%Y")}",
                        ),
                    ],
                    colWidths=[350, 150],
                    style=[
                        ("FONTSIZE", (0, 1), (-1, -1), 12),
                        ("FONTSIZE", (0, 0), (-1, 0), 18),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                        ("TOPPADDING", (0, 0), (-1, 0), 10),
                        ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
                        ("ALIGN", (0, 0), (0, -1), "LEFT"),
                        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ],
                )
            )
            story.append(Spacer(1, 12))
            story.append(build_week_table(week, styles))
            story.append(Spacer(1, 24))
            story.append(
                Paragraph(
                    "Durch die nachfolgende Unterschrift wird die Richtigkeit und Vollständigkeit der obigen Angaben bestätigt.",
                    style=ParagraphStyle(
                        "disclaimer", fontSize=11, fontName="Roboto", leading=16
                    ),
                )
            )
            story.append(Spacer(1, 12))
            story.append(create_signature_table(signature_date))
            story.append(PageBreak())

    doc.build(story, onLaterPages=add_page_number)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
