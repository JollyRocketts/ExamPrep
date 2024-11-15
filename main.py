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
                # Fetch HTML content of the URL
                response = requests.get(link)
                response.raise_for_status()
                
                # Save HTML content to a file
                html_filename = "downloaded_link.html"
                with open(html_filename, "w", encoding="utf-8") as html_file:
                    html_file.write(response.text)
                
                # Process the saved HTML file with Textract
                extracted_text = textract.process(html_filename, method='html').decode('utf-8')
                text_filename = "link_extracted_text.txt"
                with open(text_filename, "w", encoding="utf-8") as text_file:
                    text_file.write(extracted_text)
                return render_template("select_summary.html", filename=text_filename)
            except requests.exceptions.RequestException as e:
                message = f"Error fetching the URL: {e}"
            except textract.exceptions.ShellError as e:
                message = f"Error processing the HTML file with Textract: {e}"
            except Exception as e:
                message = f"An unexpected error occurred: {e}"
            return render_template("ack.html", message=message)

        # Handle PDF file upload
        elif option == 'pdf' and 'pdf' in request.files and request.files['pdf'].filename != '':
            pdf_file = request.files['pdf']
            filename = pdf_file.filename
            pdf_file.save(filename)
            try:
                extracted_text = textract.process(filename).decode('utf-8')
                text_filename = f"{filename}_text.txt"
                with open(text_filename, "w", encoding="utf-8") as text_file:
                    text_file.write(extracted_text)
                return render_template("select_summary.html", filename=text_filename)
            except Exception as e:
                message = f"Error processing the PDF file: {e}"
                return render_template("ack.html", message=message)
        
        # Handle DOC file upload
        elif option == 'doc' and 'doc' in request.files and request.files['doc'].filename != '':
            doc_file = request.files['doc']
            filename = doc_file.filename
            doc_file.save(filename)
            try:
                extracted_text = textract.process(filename).decode('utf-8')
                text_filename = f"{filename}_text.txt"
                with open(text_filename, "w", encoding="utf-8") as text_file:
                    text_file.write(extracted_text)
                return render_template("select_summary.html", filename=text_filename)
            except Exception as e:
                message = f"Error processing the DOC file: {e}"
                return render_template("ack.html", message=message)

        # Handle PPT file upload
        elif option == 'ppt' and 'ppt' in request.files and request.files['ppt'].filename != '':
            ppt_file = request.files['ppt']
            filename = ppt_file.filename
            ppt_file.save(filename)
            try:
                extracted_text = textract.process(filename).decode('utf-8')
                text_filename = f"{filename}_text.txt"
                with open(text_filename, "w", encoding="utf-8") as text_file:
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
                with open(transcript_filename, 'w', encoding="utf-8") as transcript_file:
                    transcript_file.write(formatted_transcript)
                
                return render_template("select_summary.html", filename=transcript_filename)
            except Exception as e:
                message = f"Error fetching transcript for the video: {e}"
                return render_template("ack.html", message=message)
        
        else:
            message = "Please select a valid option and submit the required information."
            return render_template("ack.html", message=message)

@app.route('/summarize', methods=['POST'])
def summarize():
    filename = request.form.get('filename')
    summary_type = request.form.get('summary_type')
    summary_length = request.form.get('summary_length')
    
    with open(filename, 'r', encoding="utf-8") as file:
        text = file.read()

    max_input_length = 512  # Model's input token limit

    # Adjust summary length parameters based on user selection
    if summary_length == 'short':
        max_output_length = 50
    elif summary_length == 'medium':
        max_output_length = 130
    elif summary_length == 'long':
        max_output_length = 250
    else:
        max_output_length = 130  # Default to medium if no valid option

    # Truncate text if it exceeds the model's max input length
    truncated_text = text[:max_input_length]

    try:
        if summary_type == 'bart':
            # summary = bart_summarizer(truncated_text, max_length=max_output_length, min_length=30, do_sample=False)[0]['summary_text']
            summary = bart_summarizer(truncated_text, max_length=max_output_length, min_length=max_output_length // 2, do_sample=False)[0]['summary_text']
        elif summary_type == 'bert':
            # summary = bert_summarizer(truncated_text, max_length=max_output_length, min_length=30, do_sample=False)[0]['summary_text']
            summary = bert_summarizer(truncated_text, max_length=max_output_length, min_length=max_output_length // 2, do_sample=False)[0]['summary_text']
        else:
            summary = "Invalid summary type selected."
        
        summary_filename = f"{filename}_summary.txt"
        with open(summary_filename, 'w', encoding = "utf-8") as summary_file:
            summary_file.write(summary)
        
        message = f"Summary generated and saved to {summary_filename} using {summary_type.upper()} with {summary_length} length."
    except Exception as e:
        message = f"Error during summarization: {e}"
    
    return render_template("ack.html", message=message)


if __name__ == '__main__':
    app.run(debug=True)
