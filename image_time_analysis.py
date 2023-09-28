import boto3
import tempfile
import json
from PIL import Image, ExifTags, TiffTags

def clean_exif_data(exif_data):
    clean_data = {}
    for tag, value in exif_data.items():
        tag_name = ExifTags.TAGS.get(tag, tag)
        
        if isinstance(value, bytes):
            try:
                clean_value = value.decode('utf-8')
            except UnicodeDecodeError:
                clean_value = value.hex()
        
        elif "IFDRational" in str(type(value)):  # Check if the type is IFDRational
            # You can customize this; here we convert the rational to a float
            clean_value = float(value.numerator) / float(value.denominator)
        
        else:
            clean_value = value

        clean_data[tag_name] = clean_value

    return clean_data


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
        if exif_data:
            # Clean and convert EXIF data to JSON
            clean_data = clean_exif_data(exif_data)
            exif_data_json = json.dumps(clean_data)
        else:
            exif_data_json = json.dumps({})


    return {
        'statusCode': 200,
        'body': exif_data_json
    }
