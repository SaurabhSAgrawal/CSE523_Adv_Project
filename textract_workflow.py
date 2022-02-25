import boto3
import sys
import re
from pdf2image import convert_from_path
import argparse


def get_kv_map(file_name):

    with open(file_name, 'rb') as file:
        img_test = file.read()
        bytes_test = bytearray(img_test)
        print('Image loaded', file_name)

    # Amazon Textract client
    # Update aws access key, secret key
    textract = boto3.client(
        'textract',
        region_name='us-east-1',
        aws_access_key_id='',
        aws_secret_access_key=''
    )

    response = textract.analyze_document(Document={'Bytes': bytes_test}, FeatureTypes=['FORMS'])

    blocks = response['Blocks']

    # get key and value maps
    key_map = {}
    value_map = {}
    block_map = {}
    for block in blocks:
        block_id = block['Id']
        block_map[block_id] = block
        if block['BlockType'] == "KEY_VALUE_SET":
            if 'KEY' in block['EntityTypes']:
                key_map[block_id] = block
            else:
                value_map[block_id] = block

    return key_map, value_map, block_map


def get_kv_relationship(key_map, value_map, block_map):
    kvs = {}
    for block_id, key_block in key_map.items():
        value_block = find_value_block(key_block, value_map)
        key = get_text(key_block, block_map)
        val = get_text(value_block, block_map)
        kvs[key] = val
    return kvs


def find_value_block(key_block, value_map):
    for relationship in key_block['Relationships']:
        if relationship['Type'] == 'VALUE':
            for value_id in relationship['Ids']:
                value_block = value_map[value_id]
    return value_block


def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] == 'SELECTED':
                            text += 'X '

    return text


def print_kvs(kvs, file_name, page_number):
    output_filename = file_name[:-4] + '_page' + str(page_number) + '.txt'
    with open(output_filename, 'w') as file:
        file.write('Key = Value\n')
        for key, value in kvs.items():
            file.write(key + '=' + value + '\n')
    print("File " + output_filename + " saved")


def search_value(kvs, search_key):
    for key, value in kvs.items():
        if re.search(search_key, key, re.IGNORECASE):
            return value


def main(document_type, file_name):
    handwritten_pages = {'CCW9': [2], 'CCDD': [2], 'CCAD': [2, 3], 'PUVC': [2, 3]}
    pages = convert_from_path(file_name, 500, poppler_path=r".\poppler-0.68.0_x86\poppler-0.68.0\bin")
    for i in range(len(pages)):
        if i + 1 in handwritten_pages[document_type]:
            name = file_name[:-4] + '_page' + str(i + 1) + '.jpg'
            pages[i].save(name, 'JPEG')
            key_map, value_map, block_map = get_kv_map(name)

            # Get Key Value relationship
            kvs = get_kv_relationship(key_map, value_map, block_map)
            print_kvs(kvs, file_name, i+1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--document_type", type=str, help="enter the document type")
    parser.add_argument("--file_name", type=str, help="enter the file name")
    args = parser.parse_args()
    main(args.document_type, args.file_name)
