import io

import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes


def annotate():
    data = io.BytesIO()

    c = canvas.Canvas(data, pagesize=pagesizes.A4)
    c.drawString(100, 100, "Hello World")
    c.save()

    data.seek(0)
    return data


def overlay(original, annotations, output):
    output_pdf = PyPDF2.PdfFileWriter()
    original_pdf = PyPDF2.PdfFileReader(original)
    annotations_pdf = PyPDF2.PdfFileReader(annotations)

    # pages = original_pdf.getNumPages()
    # assert pages == annotations_pdf.getNumPages()

    for orig_page, ann_page in zip(original_pdf.pages, annotations_pdf.pages):
        orig_page.mergePage(ann_page)
        output_pdf.addPage(orig_page)

    output_pdf.write(output)


def main():
    annotations = annotate()

    with open("stamps.pdf", 'rb') as f_orig, open("output.pdf", 'wb') as f_out:
        overlay(f_orig, annotations, f_out)


if __name__ == '__main__':
    main()
