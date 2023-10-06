import boto3
import tempfile
import json
import logging
from PIL import Image, ExifTags, TiffTags

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recursive_serialize(obj):
    #print(f"Type of obj: {type(obj)}")  # Debugging print statement

    if isinstance(obj, dict):
        return {k: recursive_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recursive_serialize(e) for e in obj]
    elif isinstance(obj, tuple):
        return tuple([recursive_serialize(e) for e in obj])
    elif "IFDRational" in str(type(obj)):
        #print(f"Handling IFDRational: {obj}")  # Debugging print statement
        return float(obj.numerator) / float(obj.denominator)
    elif isinstance(obj, bytes):
        try:
            return obj.decode('utf-8')
        except UnicodeDecodeError:
            return obj.hex()
    else:
        return obj

def clean_exif_data(exif_data):
    clean_data = {}
    for tag, value in exif_data.items():
        tag_name = ExifTags.TAGS.get(tag, tag)
        
        # Skip undesired tags
        if tag_name in ['MakerNote', 'PrintImageMatching', 'UserComment']:
            continue

        clean_data[tag_name] = recursive_serialize(value)
    return clean_data


def lambda_handler(event, context):
    try:
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

        # Initialize DynamoDB resource and table
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('test1')

        # Write to DynamoDB
        table.put_item(
        Item={
                'image_key': key,
                'exif_data': exif_data_json  
            }
        )
        
        logger.info(f"Successfully wrote EXIF data for {key} to DynamoDB")
        return {'statusCode': 200, 'body': 'Successfully wrote to DynamoDB'}

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {'statusCode': 500, 'body': 'Internal Server Error'}
