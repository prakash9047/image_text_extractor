import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.conf import settings

# Set Tesseract paths
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

def home(request):
    """Render the home page."""
    return render(request, 'home.html')

def preprocess_image(image_path):
    """
    Enhanced preprocessing with better color separation and noise reduction.
    """
    # Read image and resize for better processing
    image = cv2.imread(image_path)
    height = 2000
    aspect_ratio = image.shape[1] / image.shape[0]
    width = int(height * aspect_ratio)
    image = cv2.resize(image, (width, height))
    
    # Convert to RGB and various color spaces
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Create masks for red text
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    
    # Combine red masks
    mask_red1 = cv2.inRange(image_hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(image_hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    
    # Create mask for black text
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])
    mask_black = cv2.inRange(image_hsv, lower_black, upper_black)
    
    # Enhance masks
    kernel = np.ones((2,2), np.uint8)
    mask_red = cv2.dilate(mask_red, kernel, iterations=1)
    mask_black = cv2.dilate(mask_black, kernel, iterations=1)
    
    # Remove noise
    mask_red = cv2.medianBlur(mask_red, 3)
    mask_black = cv2.medianBlur(mask_black, 3)
    
    return image_rgb, mask_red, mask_black

def extract_text_by_color(image, mask):
    """
    Enhanced text extraction with better accuracy.
    """
    # Apply mask and create white background
    result = cv2.bitwise_and(image, image, mask=mask)
    white_bg = np.full(image.shape, 255, dtype=np.uint8)
    result = cv2.bitwise_or(result, white_bg, mask=cv2.bitwise_not(mask))
    
    # Convert to grayscale for OCR
    gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    
    # Apply threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # OCR configuration
    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
    
    # Extract text
    text = pytesseract.image_to_string(binary, config=custom_config)
    
    # Clean and filter text
    lines = []
    for line in text.split('\n'):
        cleaned = line.strip()
        if cleaned and len(cleaned) > 1:  # Filter out single characters
            lines.append(cleaned)
    
    return lines

def extract_and_format_text(image_path):
    """
    Extract and format text into key-value pairs.
    """
    # Get preprocessed image and masks
    image, mask_red, mask_black = preprocess_image(image_path)
    
    # Extract text by color
    red_text = extract_text_by_color(image, mask_red)
    black_text = extract_text_by_color(image, mask_black)
    
    # Format results into dictionary
    result = {}
    
    # Process red text (keys) first
    for red_line in red_text:
        # Clean the key
        key = red_line.strip().rstrip(':')
        if key:
            result[key] = ""
    
    # Match black text (values) with keys
    keys = list(result.keys())
    current_key_idx = 0
    
    for black_line in black_text:
        if current_key_idx < len(keys):
            # If the black text doesn't contain a key, add it as a value
            if black_line not in result:
                result[keys[current_key_idx]] = black_line
                current_key_idx += 1
    
    # Clean up empty values
    final_result = {k: v for k, v in result.items() if v}
    
    return final_result

def upload_image(request):
    """
    Handle image upload and processing.
    """
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            uploaded_file = request.FILES['image']
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)  # Save to MEDIA_ROOT
            filename = fs.save(uploaded_file.name, uploaded_file)
            image_url = fs.url(filename)  # Get the URL to serve the image
            
            # Full file path
            image_path = os.path.join(fs.location, filename)
            
            # Extract and format text (assuming this is defined somewhere)
            extracted_text = extract_and_format_text(image_path)
            
            return JsonResponse({
                'extracted_data': extracted_text,
                'uploaded_file_url': image_url,  # Return the image URL for display
                'status': 'success'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return render(request, 'upload.html')
