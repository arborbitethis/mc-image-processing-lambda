# AWS Lambda Function for Image Time Analysis

## Overview

This AWS Lambda function is triggered by a new object created in an S3 bucket. The function takes the image from the S3 bucket, analyzes it using OpenCV to determine an estimated time of day based on visual characteristics of the image, and compares that with the time information in the EXIF data.

## Requirements

- AWS Account
- Python 3.x
- OpenCV (`cv2`)
- NumPy (`numpy`)
- Boto3 (`boto3`)
- Pillow (`PIL`)
- Temporary File System Access (`tempfile`)
- Datetime (`datetime`)

## Dependencies

The required Python packages are listed in the `requirements.txt` file and can be installed using pip:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## How it Works

### Lambda Trigger

The Lambda function is designed to be triggered by an event in S3, specifically when a new object (image) is created.

### Image Download

The function uses Boto3 to download the image from the S3 bucket to a temporary file.

### EXIF Data

Pillow (PIL) is used to read the EXIF data from the image, which contains the timestamp indicating when the photo was taken. This time is classified into one of the following periods:

- Morning
- Day
- Evening
- Night

### Response

The function returns a JSON object containing both the estimated time of day based on visual characteristics and the actual time of day based on the EXIF data.

## Deployment

A github action handles deployment