import io
import csv

import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes, units


DEBUG = False


def annotate(c, position, text):
    margin_left = 31
    margin_bottom = 10

    sender_margin_left = 31
    sender_margin_bottom = 90

    positions = {
        'bottomleft': (margin_left, margin_bottom),
        'bottomright': (margin_left + 297 / 2, margin_bottom),
        'topleft': (margin_left, margin_bottom + 210 / 2),
        'topright': (margin_left + 297 / 2, margin_bottom + 210 / 2),

        'sender_bottomleft': (sender_margin_left, sender_margin_bottom),
        'sender_bottomright': (sender_margin_left + 297 / 2,
                               sender_margin_bottom),
        'sender_topleft': (sender_margin_left,
                           sender_margin_bottom + 210 / 2),
        'sender_topright': (sender_margin_left + 297 / 2,
                            sender_margin_bottom + 210 / 2),
    }
    pos = positions[position]
    c.drawString(pos[0] * units.mm, pos[1] * units.mm, text)

    sender_pos = positions['sender_' + position]
    with open('sender.txt', 'r') as f:
        sender = f.read().strip()
    c.drawString(sender_pos[0] * units.mm, sender_pos[1] * units.mm,
                 f"Absender: {sender}")


def find_data(post_row):
    with open("shirts.csv", 'r') as f:
        reader = csv.DictReader(f)
        rows = [d for d in reader if d['Shipping Name'] == post_row['NAME']]

    if len(rows) != 1:
        raise ValueError(f"{len(rows)} matches for {post_row}")

    row = rows[0]

    lines = []

    if DEBUG:
        lines.append(row['Shipping Name'])

    lines.append('{} {}'.format(row['T Shirt Size'], row['T Shirt Color']))

    if row['T Shirt 2 Size']:
        assert row['T Shirt 2 Color']
        lines.append('{} {}'.format(row['T Shirt 2 Size'],
                                    row['T Shirt 2 Color']))
    else:
        assert not row['T Shirt 2 Color']

    if row['Comments']:
        lines.append(row['Comments'])

    return ' + '.join(lines)


def get_overlay_pdf(data_post):
    post_reader = csv.DictReader(data_post, delimiter=';')
    canvas_data = io.BytesIO()
    output_canvas = canvas.Canvas(canvas_data,
                                  pagesize=pagesizes.landscape(pagesizes.A4))

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

        output_canvas.setFont("Helvetica", 8)
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
