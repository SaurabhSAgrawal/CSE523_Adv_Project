from pdf2image import convert_from_path
import argparse
from textract_api import *
from pathlib import Path
from PyPDF2 import PdfFileWriter, PdfFileReader
from bounding_box_creation import create_bounding_box

# handwritten_pages = {'CCW9': [2], 'CCDD': [2], 'CCAD': [2, 3], 'PUVC': [2, 3]}
handwritten_pages = {'CCW9': [2], 'CCDD': [2], 'CCAD': [6, 12, 20, 21], 'PUVC': [14]}


def main(document_type, file_name):
    pages = convert_from_path(file_name, 220)
    for i in range(len(pages)):
        if i + 1 in handwritten_pages[document_type]:
            name = file_name[:-4] + '_page' + str(i + 1) + '.jpg'
            pages[i].save(name, 'JPEG')
            if document_type in ['CCW9', 'PUVC', 'CCDD']:
                create_bounding_box(document_type, name)
            # key_map, value_map, block_map = get_kv_map(name)
            #
            # # Get Key Value relationship
            # kvs = get_kv_relationship(key_map, value_map, block_map)
            # print_kvs(kvs, file_name, i+1)


def extract_from_pdf(document_type, file_name):
    pdf = PdfFileReader(open(file_name, "rb"), strict=False)
    output = PdfFileWriter()
    for page in range(pdf.numPages):
        if page + 1 in handwritten_pages[document_type]:
            output.addPage(pdf.getPage(page))
    name = file_name[:-4] + "_hand-written-page.pdf"
    with open(name, "wb") as outputStream:
        output.write(outputStream)

    key_map, value_map, block_map = get_kv_map(name)
    # Get Key Value relationship
    kvs = get_kv_relationship(key_map, value_map, block_map)
    print_kvs(kvs, file_name, '_pdf')


def image(file_name):
    key_map, value_map, block_map = get_kv_map(file_name)
    # Get Key Value relationship
    kvs = get_kv_relationship(key_map, value_map, block_map)
    print_kvs(kvs, file_name, '')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--document_type", type=str, help="enter the document type")
    parser.add_argument("--file_name", type=str, help="enter the file name")
    args = parser.parse_args()
    main(args.document_type, args.file_name)
    # extract_from_pdf(args.document_type, args.file_name)
    # image(args.file_name)
