import boto3
import tempfile
import json
from PIL import Image, ExifTags

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
        try:
            image_pil = Image.open(fp)
            raw_exif_data = image_pil._getexif()
        except Exception as e:
            return {
                'statusCode': 500,
                'body': f"Error reading EXIF data: {str(e)}"
            }

        # Map EXIF data to human-readable tags
        if raw_exif_data:
            exif_data = {ExifTags.TAGS.get(tag, tag): value for tag, value in raw_exif_data.items()}
        else:
            exif_data = {}

        # Convert EXIF data to JSON
        exif_data_json = json.dumps(exif_data, default=str)

    return {
        'statusCode': 200,
        'body': exif_data_json
    }
