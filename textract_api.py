import boto3
import re
import time


def get_kv_map(file_name):
    # with open(file_name, 'rb') as file:
    #     file_test = file.read()
    #     bytes_test = bytearray(file_test)
    #     print('File loaded', file_name)

    # Amazon Textract client
    # Update region_name, aws access key, secret key
    textract = boto3.client(
        'textract',
        region_name='us-east-1',
        aws_access_key_id='',
        aws_secret_access_key=''
    )

    # Update aws access key, secret key, S3 bucket name
    s3 = boto3.resource('s3',
                        aws_access_key_id='',
                        aws_secret_access_key=''
                        )
    bucket = 'textract-console-us-east-1-c85e0f69-be1d-4e20-a271-10940f0064b0'

    s3.Bucket(bucket).upload_file(file_name, file_name)

    # response = textract.analyze_document(Document={'Bytes': bytes_test}, FeatureTypes=['FORMS'])
    response = textract.start_document_analysis(DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': file_name}},
                                                FeatureTypes=['FORMS'])
    job_id = response['JobId']
    response = textract.get_document_analysis(JobId=job_id)
    while response['JobStatus'] == 'IN_PROGRESS':
        response = textract.get_document_analysis(JobId=job_id)
        # print(response['JobStatus'])
        time.sleep(1)
    pages = [response]

    # get key and value maps
    key_map = {}
    value_map = {}
    block_map = {}

    while nextToken := response.get('NextToken'):
        response = textract.get_document_analysis(JobId=job_id, NextToken=nextToken)
        pages.append(response)

    for response in pages:
        blocks = response['Blocks']

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


def print_kvs(kvs, file_name, ext):
    output_filename = file_name[:-4] + str(ext) + '.txt'
    with open(output_filename, 'w') as file:
        file.write('Key = Value\n')
        for key, value in kvs.items():
            file.write(key + '= ' + value + '\n')
    print("File " + output_filename + " saved")


def search_value(kvs, search_key):
    for key, value in kvs.items():
        if re.search(search_key, key, re.IGNORECASE):
            return value
