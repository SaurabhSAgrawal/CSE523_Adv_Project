import cv2
import numpy as np
from PIL import Image
from textract_api import *


def alignImages(im1, im2):
    MAX_MATCHES = 500
    GOOD_MATCH_PERCENT = 0.20
    # Convert images to grayscale
    im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    im2Gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

    # Detect ORB features and compute descriptors.
    orb = cv2.ORB_create(MAX_MATCHES)
    keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
    keypoints2, descriptors2 = orb.detectAndCompute(im2Gray, None)

    # Match features.
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = list(matcher.match(descriptors1, descriptors2, None))

    # Sort matches by score
    matches.sort(key=lambda x: x.distance, reverse=False)

    # Remove not so good matches
    numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
    matches = matches[:numGoodMatches]

    # Draw top matches
    imMatches = cv2.drawMatches(im1, keypoints1, im2, keypoints2, matches, None)
    cv2.imwrite("matches.jpg", imMatches, [int(cv2.IMWRITE_JPEG_QUALITY), 200])

    # Extract location of good matches
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        points1[i, :] = keypoints1[match.queryIdx].pt
        points2[i, :] = keypoints2[match.trainIdx].pt

    # Find homography
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

    # Use homography
    height, width, channels = im2.shape
    im1Reg = cv2.warpPerspective(im1, h, (width, height))

    return im1Reg, h


def create_bounding_box(document_type, file_name):
    if document_type == 'CCW9':
        imReference = cv2.imread('CCW9_blank.jpg', cv2.IMREAD_COLOR)
        im = cv2.imread(file_name, cv2.IMREAD_COLOR)
        imReg, _ = alignImages(im, imReference)

        # Align filled image
        aligned_image_filename = file_name[:-4] + '_aligned.jpg'
        cv2.imwrite(aligned_image_filename, imReg, [int(cv2.IMWRITE_JPEG_QUALITY), 200])

        # Crop checkbox
        image = Image.open(aligned_image_filename)
        # cropped = image.crop((160, 365, 1265, 669))
        # file = file_name[:-4] + '_checkbox.jpg'
        # cropped.save(file)
        # key_map, value_map, block_map = get_kv_map(file)
        # kvs = get_kv_relationship(key_map, value_map, block_map)
        # print_kvs(kvs, file_name, '_checkbox')

        # Crop part1 field
        # cropped = image.crop((160, 225, 1630, 870))
        cropped = image.crop((158, 232, 1630, 875))
        file = file_name[:-4] + '_part1.jpg'
        cropped.save(file)
        key_map, value_map, block_map = get_kv_map(file)
        kvs = get_kv_relationship(key_map, value_map, block_map)
        print_kvs(kvs, file_name, '_part1')

        # # Crop address field
        # cropped = image.crop((160, 670, 1630, 870))
        # file = file_name[:-4] + '_address.jpg'
        # cropped.save(file)
        # key_map, value_map, block_map = get_kv_map(file)
        # kvs = get_kv_relationship(key_map, value_map, block_map)
        # print_kvs(kvs, file_name, '_address')

        # Crop ssn field
        cropped = image.crop((95, 895, 1630, 1150))
        file = file_name[:-4] + '_ssn.jpg'
        cropped.save(file)
        key_map, value_map, block_map = get_kv_map(file)
        kvs = get_kv_relationship(key_map, value_map, block_map)
        print_kvs(kvs, file_name, '_ssn')

        # Crop date field
        cropped = image.crop((160, 1490, 1580, 1580))
        file = file_name[:-4] + '_date.jpg'
        cropped.save(file)
        key_map, value_map, block_map = get_kv_map(file)
        kvs = get_kv_relationship(key_map, value_map, block_map)
        print_kvs(kvs, file_name, '_date')

    if document_type == 'PUVC':
        imReference = cv2.imread('PUVC_blank.jpg', cv2.IMREAD_COLOR)
        im = cv2.imread(file_name, cv2.IMREAD_COLOR)
        imReg, _ = alignImages(im, imReference)

        # Align filled image
        aligned_image_filename = file_name[:-4] + '_aligned.jpg'
        cv2.imwrite(aligned_image_filename, imReg, [int(cv2.IMWRITE_JPEG_QUALITY), 200])

        # Crop part1
        image = Image.open(aligned_image_filename)
        # cropped = image.crop((160, 540, 1630, 955))
        cropped = image.crop((160, 540, 1630, 1630))
        file = file_name[:-4] + '_part1.jpg'
        cropped.save(file)
        key_map, value_map, block_map = get_kv_map(file)
        kvs = get_kv_relationship(key_map, value_map, block_map)
        print_kvs(kvs, file_name, '_part1')

    if document_type == 'CCAD':
        imReference = cv2.imread('CCAD_blank.jpg', cv2.IMREAD_COLOR)
        im = cv2.imread(file_name, cv2.IMREAD_COLOR)
        imReg, _ = alignImages(im, imReference)

        # Align filled image
        aligned_image_filename = file_name[:-4] + '_aligned.jpg'
        cv2.imwrite(aligned_image_filename, imReg, [int(cv2.IMWRITE_JPEG_QUALITY), 200])

        # Crop part1
        image = Image.open(aligned_image_filename)
        cropped = image.crop((100, 350, 1600, 840))
        file = file_name[:-4] + '_part1.jpg'
        cropped.save(file)
        key_map, value_map, block_map = get_kv_map(file)
        kvs = get_kv_relationship(key_map, value_map, block_map)
        print_kvs(kvs, file_name, '_part1')

        # Crop part2
        cropped = image.crop((100, 840, 1600, 1600))
        file = file_name[:-4] + '_part2.jpg'
        cropped.save(file)
        key_map, value_map, block_map = get_kv_map(file)
        kvs = get_kv_relationship(key_map, value_map, block_map)
        print_kvs(kvs, file_name, '_part2')

        # Crop part3
        cropped = image.crop((100, 1600, 1600, 2100))
        file = file_name[:-4] + '_part3.jpg'
        cropped.save(file)
        key_map, value_map, block_map = get_kv_map(file)
        kvs = get_kv_relationship(key_map, value_map, block_map)
        print_kvs(kvs, file_name, '_part3')
    
    if document_type == 'CCDD':
        imReference = cv2.imread('CCDD_blank.jpg', cv2.IMREAD_COLOR)
        im = cv2.imread(file_name, cv2.IMREAD_COLOR)
        imReg, _ = alignImages(im, imReference)

        # Align filled image
        aligned_image_filename = file_name[:-4] + '_aligned.jpg'
        cv2.imwrite(aligned_image_filename, imReg, [int(cv2.IMWRITE_JPEG_QUALITY), 200])

        # Crop main part
        image = Image.open(aligned_image_filename)
        # cropped = image.crop((160, 540, 1630, 955))
        cropped = image.crop((100, 690, 950, 1730))
        file = file_name[:-4] + 'mainBox.jpg'
        cropped.save(file)
        key_map, value_map, block_map = get_kv_map(file)
        kvs = get_kv_relationship(key_map, value_map, block_map)
        print_kvs(kvs, file_name, 'mainBox')
