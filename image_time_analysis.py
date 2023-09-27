import cv2
import numpy as np
import boto3
import tempfile
from PIL import Image
from datetime import datetime

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

        # Extract the timestamp from EXIF data
        actual_time = "Unknown"
        if exif_data and 306 in exif_data:  # 306 is the key for DateTime
            timestamp_str = exif_data[306]
            timestamp = datetime.strptime(timestamp_str, '%Y:%m:%d %H:%M:%S')
            hour = timestamp.hour
            if 5 <= hour < 12:
                actual_time = "Morning"
            elif 12 <= hour < 17:
                actual_time = "Day"
            elif 17 <= hour < 20:
                actual_time = "Evening"
            else:
                actual_time = "Night"

        fp.seek(0)
        
        # Read the image using OpenCV
        image_np = np.frombuffer(fp.read(), np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        
        # Calculate brightness of the image
        brightness = np.average(image)
        
        # Calculate average color of the image
        avg_color_per_row = np.average(image, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        
        # Determine estimated time of day based on brightness and average color
        estimated_time = "Unknown"
        
        if brightness > 100:
            if avg_color[0] > 100:  # Blue channel
                estimated_time = "Day"
            else:
                estimated_time = "Morning/Evening"
        else:
            if avg_color[0] < 50 and avg_color[1] < 50 and avg_color[2] < 50:  # Low RGB
                estimated_time = "Night"
            else:
                estimated_time = "Artificial Light/Evening"

    return {
        'statusCode': 200,
        'body': f'Estimated time of day is: {estimated_time}, Actual time of day from EXIF is: {actual_time}'
    }
