from datetime import datetime
from pathlib import Path

from fpdf import FPDF
from PIL import Image

from app.config import Settings
from app.utils.files import safe_filename


def _wrap_text(
    pdf: FPDF,
    text: str,
    max_width: float,
):

    lines = []
    current = ""

    for word in text.split():

        candidate = (
            f"{current} {word}"
        ).strip()

        if pdf.get_string_width(
            candidate
        ) <= max_width:

            current = candidate

        else:

            if current:

                lines.append(current)

            current = word

    if current:

        lines.append(current)

    return lines


def save_pdf(
    layout: list[dict],
    settings: Settings,
    title: str = "ComicCraft Comic",
) -> Path:

    if not layout:

        raise ValueError(
            "Cannot export an empty comic."
        )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in layout:

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            18,
        )

        pdf.cell(
            0,
            12,
            text=(
                f"Panel {panel['panel_number']}: "
                f"{panel['title']}"
            ),
            new_x="LMARGIN",
            new_y="NEXT",
        )

        image_path = Path(
            panel["image_path"]
        )

        with Image.open(image_path) as image:

            width, height = image.size

        ratio = min(
            180 / width,
            115 / height,
        )

        render_width = width * ratio
        render_height = height * ratio

        pdf.image(
            str(image_path),
            x=(210 - render_width) / 2,
            y=30,
            w=render_width,
            h=render_height,
        )

        pdf.set_y(
            30 + render_height + 8
        )

        pdf.set_font(
            "Helvetica",
            "I",
            10,
        )

        for line in _wrap_text(
            pdf,
            panel["scene_description"],
            180,
        ):

            pdf.cell(
                0,
                5,
                text=line,
                new_x="LMARGIN",
                new_y="NEXT",
            )

        sections = [
            (
                "Caption",
                panel["caption"],
            ),
            (
                "Narration",
                panel["narration"],
            ),
            (
                "Dialogue",
                panel.get("dialogue", ""),
            ),
        ]

        for label, text in sections:

            if not text:
                continue

            pdf.ln(2)

            pdf.set_font(
                "Helvetica",
                "B",
                11,
            )

            pdf.cell(
                0,
                6,
                text=label,
                new_x="LMARGIN",
                new_y="NEXT",
            )

            pdf.set_font(
                "Helvetica",
                "",
                10,
            )

            for line in _wrap_text(
                pdf,
                text,
                180,
            ):

                pdf.cell(
                    0,
                    5,
                    text=line,
                    new_x="LMARGIN",
                    new_y="NEXT",
                )

    filename = (
        f"{safe_filename(title)}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    output = (
        settings.export_dir / filename
    )

    pdf.output(str(output))

    return output