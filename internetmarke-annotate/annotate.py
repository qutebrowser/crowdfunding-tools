import io
import csv

import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes, units


def annotate(c, position, text):
    margin_left = 20
    margin_top = 80

    positions = {
        'topleft': (margin_left * units.mm,
                    margin_top * units.mm),
        'topright': (margin_left + 420 / 2 * units.mm,
                     margin_top * units.mm),
        'bottomleft': (margin_left * units.mm,
                       margin_top + 297 / 2 * units.mm),
        'bottomright': (margin_left + 420 / 2 * units.mm,
                        margin_top + 297 / 2 * units.mm),
    }
    c.drawString(0, 0, "origin")
    c.drawString(*positions[position], text)


def find_data(post_row):
    with open("shirts.csv", 'r') as f:
        reader = csv.DictReader(f)
        rows = [d for d in reader if d['Shipping Name'] == post_row['NAME']]

    if len(rows) != 1:
        raise ValueError(f"{len(rows)} matches for {post_row}")
    return rows[0]['Email']  # FIXME


def get_overlay_pdf(data_post):
    post_reader = csv.DictReader(data_post, delimiter=';')
    canvas_data = io.BytesIO()
    output_canvas = canvas.Canvas(canvas_data, pagesize=pagesizes.landscape(pagesizes.A4))

    next(post_reader)  # Sender

    while True:
        try:
            topleft = next(post_reader)
            topright = next(post_reader)
            bottomleft = next(post_reader)
            bottomright = next(post_reader)
        except StopIteration:
            break

        topleft_data = find_data(topleft)
        topright_data = find_data(topright)
        bottomleft_data = find_data(bottomleft)
        bottomright_data = find_data(bottomright)

        output_canvas.translate(pagesizes.A4[0], 0)
        output_canvas.rotate(90)

        annotate(output_canvas, 'topleft', topleft_data)
        annotate(output_canvas, 'topright', topright_data)
        annotate(output_canvas, 'bottomleft', bottomleft_data)
        annotate(output_canvas, 'bottomright', bottomright_data)

        output_canvas.showPage()

    output_canvas.save()
    canvas_data.seek(0)
    return canvas_data


def overlay(original, annotations, output):
    output_pdf = PyPDF2.PdfFileWriter()
    original_pdf = PyPDF2.PdfFileReader(original)
    annotations_pdf = PyPDF2.PdfFileReader(annotations)

    pages = original_pdf.getNumPages()
    assert pages == annotations_pdf.getNumPages()

    for orig_page, ann_page in zip(original_pdf.pages, annotations_pdf.pages):
        orig_page.mergePage(ann_page)
        output_pdf.addPage(orig_page)

    output_pdf.write(output)


def main():
    for name in ["int", "de"]:
        with open(f"{name}.pdf", 'rb') as f_orig, \
             open(f"{name}_output.pdf", 'wb') as f_out, \
             open(f"{name}.csv", 'r', encoding='latin1') as f_post_csv:
            overlay_pdf = get_overlay_pdf(f_post_csv)
            overlay(f_orig, overlay_pdf, f_out)


if __name__ == '__main__':
    main()
