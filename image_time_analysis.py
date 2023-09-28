import boto3
import tempfile
import json
from PIL import Image

def lambda_handler(event, context):
    # Initialize S3 client
    s3_client = boto3.client('s3')

    # Extract bucket and object key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Download the image to a temporary file
    with tempfile.NamedTemporaryFile() as fp:
        s3_client.download_fileobj(bucket, key, fp)
        fp.seek(0)
        
        # Read EXIF data using PIL
        image_pil = Image.open(fp)
        exif_data = image_pil._getexif()

        # Convert EXIF data to JSON
        exif_data_json = json.dumps(exif_data, default=str) if exif_data else json.dumps({})

    return {
        'statusCode': 200,
        'body': exif_data_json
    }
