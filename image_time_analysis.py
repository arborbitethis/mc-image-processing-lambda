import cv2
import boto3
import tempfile
import array
from PIL import Image
from datetime import datetime

def average_brightness(image):
    total_brightness = 0
    total_pixels = 0
    height, width, _ = image.shape

    for x in range(height):
        for y in range(width):
            pixel = image[x, y]
            total_brightness += sum(pixel)/3  # Average of RGB
            total_pixels += 1
    
    avg_brightness = total_brightness / total_pixels
    return avg_brightness

def average_color(image):
    total_color = [0, 0, 0]
    total_pixels = 0
    height, width, _ = image.shape

    for x in range(height):
        for y in range(width):
            pixel = image[x, y]
            total_color[0] += pixel[0]
            total_color[1] += pixel[1]
            total_color[2] += pixel[2]
            total_pixels += 1

    avg_color = [x / total_pixels for x in total_color]
    return avg_color

def lambda_handler(event, context):
    # Initialize S3 client
    s3_client = boto3.client('s3')

    # Extract bucket and object key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Download the image to a temporary file
    # Read the image to a temporary file
    with tempfile.NamedTemporaryFile() as fp:
        s3_client.download_fileobj(bucket, key, fp)
        fp.seek(0)

        # Create an array from the buffer
        image_buffer = array('B', fp.read())

        # Read the image using OpenCV
        image = cv2.imdecode(image_buffer, cv2.IMREAD_COLOR)
        
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
        
        brightness = average_brightness(image)
        avg_color = average_color(image)

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
