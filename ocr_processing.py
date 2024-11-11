import easyocr
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image, ImageEnhance
import cv2
import numpy as np
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import os

os.environ["USE_TORCH"] = "1"


def extract_text_from_image(filename):
    # print("\n\n\n",filename,"\n\n\n")
    # Load the OCR model with high precision
    model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
    
    # Load the image from the file
    # image = Image.open(filename).convert('RGB')
    
    # Convert the image to a DocumentFile format expected by docTR
    doc = DocumentFile.from_images([filename])
    
    # Perform OCR on the image
    result = model(doc)
    
    # Extract text as a single string
    # extracted_text = result.render_text()
    # extracted_text = "\n".join([block[1] for page in result.pages for block in page.blocks])

    # print("\n\n\n", result, "\n\n\n")

    extracted_text = ""

    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                for word in line.words:
                    extracted_text += word.value + " "
                extracted_text += "\n"  # New line after each line
            extracted_text += "\n"  # New line after each block
    
    return extracted_text
    # return result

# def process_image_with_docTR(filename):
#     # Initialize the model directly with ocr_predictor()
#     model = ocr_predictor("db_resnet50", "crnn_vgg16_bn")  # Specify text detection and recognition models
    
#     # Load the document from the file path
#     document = DocumentFile.from_images([filename])
    
#     # Perform OCR on the document
#     result = model(document)
    
#     # Extract text from the result
#     extracted_text = "\n".join([block['value'] for block in result.export()['pages'][0]['blocks']])
    
#     return extracted_text



# def process_image_with_docTR(filename):
#     # Load docTR model
#     model = ocr_predictor(pretrained=True)
    
#     # Load image using docTR from file path
#     document = DocumentFile.from_images([filename])  # Ensure filename is a path
    
#     # Perform OCR
#     result = model(document)
    
#     # Extract and return text
#     extracted_text = "\n".join([block['value'] for block in result.export()['pages'][0]['blocks']])
    # return extracted_text

# import keras_ocr

# def process_image_with_kerasOCR(filename):
#     # Initialize pipeline
#     pipeline = keras_ocr.pipeline.Pipeline()
#     # Read image
#     image = keras_ocr.tools.read(filename)
#     # Perform OCR
#     prediction_groups = pipeline.recognize([image])
#     # Extract and return text
#     extracted_text = " ".join([text for text, box in prediction_groups[0]])
#     return extracted_text


# def advanced_preprocess_image(filename):
#     # Read the image with OpenCV
#     image = cv2.imread(filename)
    
#     # Convert to grayscale
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
#     # Apply GaussianBlur to reduce noise and improve contour detection
#     blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
#     # Use adaptive thresholding
#     thresh = cv2.adaptiveThreshold(
#         blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
#     )

#     # Optional: Denoise the image (useful for OCR)
#     denoised = cv2.fastNlMeansDenoising(thresh, None, 30, 7, 21)

#     # Convert back to PIL format
#     processed_image = Image.fromarray(denoised)
#     return processed_image

def preprocess_image(image):
    # Resize the image to a standard size that works well with OCR
    image = image.resize((1024, 1024))

    # Increase contrast and brightness
    contrast_enhancer = ImageEnhance.Contrast(image)
    image = contrast_enhancer.enhance(2)  # Adjust as needed

    brightness_enhancer = ImageEnhance.Brightness(image)
    image = brightness_enhancer.enhance(1.5)  # Adjust as needed

    # Increase sharpness
    sharpness_enhancer = ImageEnhance.Sharpness(image)
    image = sharpness_enhancer.enhance(2)  # Adjust as needed

    return image


# Initialize EasyOCR and TrOCR models
easyocr_reader = easyocr.Reader(['en'], gpu = True)  # Supports only English for this example
# processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-printed")
# model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-printed")

def process_image(filename, ocr_option):
    # Open the image and ensure it's in RGB format
    fname = filename
    image = Image.open(filename).convert("RGB")
    
    if ocr_option == "Faster":
        # Use EasyOCR for faster processing
        result = easyocr_reader.readtext(filename, detail=0)
        extracted_text = " ".join(result)
    
    elif ocr_option == "Better Precision":
        # Use TrOCR for better precision
        # Convert the image to a format compatible with TrOCR
        extracted_text = extract_text_from_image(filename)
        # pixel_values = processor(images=image, return_tensors="pt").pixel_values
        # generated_ids = model.generate(pixel_values)
        # extracted_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return extracted_text
