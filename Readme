                         *************Image Text Extraction Project**********************

Project Overview
           The goal of this project is to develop a system that extracts and organizes text from images in a structured format.

Approach:

Approach Followed
1. Image Preprocessing
Resize Image: Resize the input image to ensure consistent dimensions for processing.
Color Space Conversion: Convert the image from BGR to RGB and HSV color spaces for better mask generation.
Color-Based Masking: Separate red and black texts using HSV color thresholds to extract relevant information from images.
Noise Reduction: Applied filters and morphological operations to enhance the text regions and remove noise from the image.
2. Text Extraction
Mask Application: Apply masks to extract regions of interest (text in different colors).
OCR with Tesseract: Use the Tesseract OCR engine to extract text from the masked images.
Text Filtering: Post-process extracted text by removing unnecessary characters, filtering single-character lines, and cleaning up the results.
3. Text Organization
Key-Value Pairing: Red text is treated as keys, while black text is considered as values. These are then paired in a structured dictionary format.
Custom Formatting: The final output is structured as a dictionary (JSON format), making it easy to interpret.

Future Enhancements:

 I planned to implement the following features in future iterations,
 Text Alignment with LLM: Use large language models (LLMs) for text alignment and ensuring the extracted text is contextually accurate.
 Image Classification: Further enhancement of image classification using OpenCV.
 Text Correctness: Improve text alignment and accuracy by integrating the OLAMA model to ensure correctness.

---------Running the Code------------------
To run this project locally, follow these steps:

1.Clone the Repository:

git clone [repository_url]
cd [repository_directory]
2.Install Dependencies: Make sure you have Python and pip installed, then run:

pip install -r requirements.txt
3.Set Up Tesseract: Install Tesseract OCR and ensure it's accessible in your system's PATH. Update the Tesseract paths in the script as needed.

4.Run the Server: 

python manage.py runserver

upload the file and get the output
