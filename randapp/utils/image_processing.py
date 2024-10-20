from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import cv2
import pytesseract
import os
import numpy as np


pytesseract.pytesseract.tesseract_cmd = r'C:\tesseract-ocr-w64-setup-5.4.0.20240606.exe'


def process_image(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)

    # Grayscale Conversion
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Noise Reduction (Denoising)
    denoised_image = cv2.fastNlMeansDenoising(gray_image, None, 30, 7, 21)

    # Binarization (Thresholding)
    _, binary_image = cv2.threshold(denoised_image, 150, 255, cv2.THRESH_BINARY)

    # Edge Detection using Canny
    edges = cv2.Canny(binary_image, 50, 150)

    # Morphological Operations (Erosion and Dilation)
    kernel = np.ones((2, 2), np.uint8)
    dilated_image = cv2.dilate(edges, kernel, iterations=1)

    # Skew Correction
    coords = np.column_stack(np.where(dilated_image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = dilated_image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    skew_corrected_image = cv2.warpAffine(dilated_image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Use PyTesseract to extract text from the processed image
    extracted_text = pytesseract.image_to_string(skew_corrected_image)

    # Convert extracted text into dictionary format (example for splitting lines by key-value pairs)
    extracted_dict = {}
    for line in extracted_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            extracted_dict[key.strip()] = value.strip()

    return extracted_dict

def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        uploaded_file_url = fs.url(filename)

        # Get the path of the uploaded file
        image_path = os.path.join('media', filename)
        
        # Process the image and extract text
        extracted_text_dict = process_image(image_path)

        # Render the template with extracted text in dictionary format
        return render(request, 'upload.html', {'extracted_data': extracted_text_dict, 'uploaded_file_url': uploaded_file_url})

    return render(request, 'upload.html')
