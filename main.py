from flask import Flask, render_template, request
from transformers import pipeline
import os
import textract
import requests
from ocr_processing import process_image
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

app = Flask(__name__)

# Load summarization pipelines
bart_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
bert_summarizer = pipeline("summarization", model="bert-base-uncased")

@app.route('/')
def main():
    return render_template("index.html")

# @app.route('/success', methods=['POST'])
# def success():
#     if request.method == 'POST':
#         option = request.form.get('option')
        
#         # Image upload option
#         if option == 'image' and 'file' in request.files and request.files['file'].filename != '':
#             f = request.files['file']
#             filename = f.filename
#             f.save(filename)
            
#             if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
#                 # Redirect to OCR mode selection
#                 return render_template("select_ocr.html", filename=filename)
#             else:
#                 return render_template("ack.html", message="File uploaded successfully but it is not an image.")
        
#         # PDF upload option
#         elif option == 'pdf' and 'pdf' in request.files and request.files['pdf'].filename != '':
#             pdf_file = request.files['pdf']
#             pdf_filename = pdf_file.filename
#             pdf_file.save(pdf_filename)
#             text = textract.process(pdf_filename).decode('utf-8')
#             text_filename = f"{pdf_filename}_text.txt"
#             with open(text_filename, 'w') as text_file:
#                 text_file.write(text)

#             return render_template("select_summary.html", filename=text_filename)
        
#         # PPT upload option
#         elif option == 'ppt' and 'ppt' in request.files and request.files['ppt'].filename != '':
#             ppt_file = request.files['ppt']
#             ppt_filename = ppt_file.filename
#             ppt_file.save(ppt_filename)
#             text = textract.process(ppt_filename).decode('utf-8')
#             text_filename = f"{ppt_filename}_text.txt"
#             with open(text_filename, 'w') as text_file:
#                 text_file.write(text)
#             return render_template("select_summary.html", filename=text_filename)
        
#         # DOC upload option
#         elif option == 'doc' and 'doc' in request.files and request.files['doc'].filename != '':
#             doc_file = request.files['doc']
#             doc_filename = doc_file.filename
#             doc_file.save(doc_filename)
#             text = textract.process(doc_filename).decode('utf-8')
#             text_filename = f"{doc_filename}_text.txt"
#             with open(text_filename, 'w') as text_file:
#                 text_file.write(text)
#             return render_template("select_summary.html", filename=text_filename)
        
#         # Link option using Textract
#         elif option == 'link' and request.form.get('link'):
#             link = request.form['link']
#             try:
#                 # Fetch HTML content of the URL
#                 response = requests.get(link)
#                 response.raise_for_status()
#                 html_content = response.content
                
#                 # Save HTML content to a temporary file
#                 temp_html_filename = "temp_page.html"
#                 with open(temp_html_filename, 'wb') as html_file:
#                     html_file.write(html_content)
                
#                 # Use Textract to extract text from the HTML file
#                 extracted_text = textract.process(temp_html_filename).decode('utf-8')
#                 text_filename = f"{link.split('//')[-1].split('/')[0]}_text.txt"
#                 with open(text_filename, 'w') as text_file:
#                     text_file.write(extracted_text)
                
#                 os.remove(temp_html_filename)  # Clean up temporary file
#                 return render_template("select_summary.html", filename=text_filename)
#             except Exception as e:
#                 message = f"Error fetching or processing the link: {e}"
        
#         # YouTube video option
#         elif option == 'video' and request.form.get('video'):
#             video_url = request.form['video']
#             video_id = video_url.split('v=')[-1]
            
#             try:
#                 transcript = YouTubeTranscriptApi.get_transcript(video_id)
#                 formatter = TextFormatter()
#                 formatted_transcript = formatter.format_transcript(transcript)
                
#                 transcript_filename = f"{video_id}_transcript.txt"
#                 with open(transcript_filename, 'w') as transcript_file:
#                     transcript_file.write(formatted_transcript)
                
#                 return render_template("select_summary.html", filename=transcript_filename)
#             except Exception as e:
#                 message = f"Error fetching transcript for the video: {e}"
        
#         else:
#             message = "Please select a valid option and submit the required information."

#         return render_template("ack.html", message=message)

# Route for processing OCR on an uploaded image
@app.route('/process_image', methods=['POST'])
def process_image_route():
    filename = request.form.get('filename')
    ocr_option = request.form.get('ocr_option')
    
    output_text = process_image(filename, ocr_option)
    output_filename = f"{filename}_output.txt"
    with open(output_filename, 'w') as output_file:
        output_file.write(output_text)
    
    return render_template("select_summary.html", filename=output_filename)

# Route for summarizing text from a processed file
# @app.route('/summarize', methods=['POST'])
# def summarize():
#     filename = request.form.get('filename')
#     summary_type = request.form.get('summary_type')
    
#     with open(filename, 'r') as file:
#         text = file.read()
    
#     try:
#         print("\n\n\n\n\n")
#         print(f"Input Text Length: {len(text)}")


#         if summary_type == 'bart':
#             summary = bart_summarizer(text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
#         elif summary_type == 'bert':
#             summary = bert_summarizer(text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
#         else:
#             summary = "Invalid summary type selected."
        
#         print(f"Generated Summary: {summary}")
#         print("\n\n\n\n\n")

        
#         summary_filename = f"{filename}_summary.txt"
#         with open(summary_filename, 'w') as summary_file:
#             summary_file.write(summary)
        
#         message = f"Summary generated and saved to {summary_filename} using {summary_type.upper()}."
#     except Exception as e:
#         message = f"Error during summarization: {e}"
    
#     return render_template("ack.html", message=message)


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        option = request.form.get('option')
        
        # Handle image upload
        if option == 'image' and 'image' in request.files and request.files['image'].filename != '':
            f = request.files['image']
            filename = f.filename
            f.save(filename)
            
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                return render_template("select_ocr.html", filename=filename)
            else:
                return render_template("ack.html", message="File uploaded successfully but it is not an image.")
        
        # Handle URL link submission
        elif option == 'link' and request.form.get('link'):
            link = request.form['link']
            try:
                link_text = textract.process(link, method='html').decode('utf-8')
                link_filename = "link_text.txt"
                with open(link_filename, "w") as link_file:
                    link_file.write(link_text)
                return render_template("select_summary.html", filename=link_filename)
            except Exception as e:
                message = f"Error processing the link: {e}"
                return render_template("ack.html", message=message)

        # Handle PDF file upload
        elif option == 'pdf' and 'pdf' in request.files and request.files['pdf'].filename != '':
            f = request.files['pdf']
            filename = f.filename
            f.save(filename)
            try:
                extracted_text = textract.process(filename).decode('utf-8')
                text_filename = f"{filename}_text.txt"
                with open(text_filename, "w") as text_file:
                    text_file.write(extracted_text)
                return render_template("select_summary.html", filename=text_filename)
            except Exception as e:
                message = f"Error processing the PDF file: {e}"
                return render_template("ack.html", message=message)
        
        # Handle DOC file upload
        elif option == 'doc' and 'doc' in request.files and request.files['doc'].filename != '':
            f = request.files['doc']
            filename = f.filename
            f.save(filename)
            try:
                extracted_text = textract.process(filename).decode('utf-8')
                text_filename = f"{filename}_text.txt"
                with open(text_filename, "w") as text_file:
                    text_file.write(extracted_text)
                return render_template("select_summary.html", filename=text_filename)
            except Exception as e:
                message = f"Error processing the DOC file: {e}"
                return render_template("ack.html", message=message)

        # Handle PPT file upload
        elif option == 'ppt' and 'ppt' in request.files and request.files['ppt'].filename != '':
            f = request.files['ppt']
            filename = f.filename
            f.save(filename)
            try:
                extracted_text = textract.process(filename).decode('utf-8')
                text_filename = f"{filename}_text.txt"
                with open(text_filename, "w") as text_file:
                    text_file.write(extracted_text)
                return render_template("select_summary.html", filename=text_filename)
            except Exception as e:
                message = f"Error processing the PPT file: {e}"
                return render_template("ack.html", message=message)
        
        # Handle YouTube video URL
        elif option == 'video' and request.form.get('video'):
            video_url = request.form['video']
            video_id = video_url.split('v=')[-1]
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                formatter = TextFormatter()
                formatted_transcript = formatter.format_transcript(transcript)
                
                transcript_filename = f"{video_id}_transcript.txt"
                with open(transcript_filename, 'w') as transcript_file:
                    transcript_file.write(formatted_transcript)
                
                return render_template("select_summary.html", filename=transcript_filename)
            except Exception as e:
                message = f"Error fetching transcript for the video: {e}"
                return render_template("ack.html", message=message)
        
        else:
            message = "Please select a valid option and submit the required information."

        return render_template("ack.html", message=message)

# Updated summarization logic in the `summarize` route
@app.route('/summarize', methods=['POST'])
def summarize():
    filename = request.form.get('filename')
    summary_type = request.form.get('summary_type')
    
    with open(filename, 'r') as file:
        text = file.read()

    max_input_length = 512  # Model's input token limit
    max_output_length = 130  # Desired summary length

    # Truncate text if it exceeds the model's max input length
    truncated_text = text[:max_input_length]

    try:
        if summary_type == 'bart':
            summary = bart_summarizer(truncated_text, max_length=max_output_length, min_length=30, do_sample=False)[0]['summary_text']
        elif summary_type == 'bert':
            summary = bert_summarizer(truncated_text, max_length=max_output_length, min_length=30, do_sample=False)[0]['summary_text']
        else:
            summary = "Invalid summary type selected."
        
        summary_filename = f"{filename}_summary.txt"
        with open(summary_filename, 'w') as summary_file:
            summary_file.write(summary)
        
        message = f"Summary generated and saved to {summary_filename} using {summary_type.upper()}."
    except Exception as e:
        message = f"Error during summarization: {e}"
    
    return render_template("ack.html", message=message)



if __name__ == '__main__':
    app.run(debug=True)
