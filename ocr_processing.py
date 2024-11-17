import easyocr
from PIL import Image, ImageEnhance
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


easyocr_reader = easyocr.Reader(['en'], gpu = True)  

def process_image(filename, ocr_option):

    if ocr_option == "Faster":
        # Use EasyOCR for faster processing
        result = easyocr_reader.readtext(filename, detail=0)
        extracted_text = " ".join(result)
    
    elif ocr_option == "Better Precision":
        extracted_text = extract_text_from_image(filename)
    
    return extracted_text
