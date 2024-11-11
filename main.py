from flask import Flask, render_template, request
from transformers import pipeline
import os
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
        
        if option == 'file' and 'file' in request.files and request.files['file'].filename != '':
            f = request.files['file']
            filename = f.filename
            f.save(filename)
            
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                return render_template("select_ocr.html", filename=filename)
            else:
                return render_template("ack.html", message="File uploaded successfully but it is not an image.")
        
        elif option == 'link' and request.form.get('link'):
            link = request.form['link']
            with open("links.txt", "a") as link_file:
                link_file.write(link + "\n")
            message = f"Link '{link}' saved successfully!"
        
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
        
        else:
            message = "Please select a valid option and submit the required information."

        return render_template("ack.html", message=message)

@app.route('/process_image', methods=['POST'])
def process_image_route():
    filename = request.form.get('filename')
    ocr_option = request.form.get('ocr_option')
    
    output_text = process_image(filename, ocr_option)
    output_filename = f"{filename}_output.txt"
    with open(output_filename, 'w') as output_file:
        output_file.write(output_text)
    
    return render_template("select_summary.html", filename=output_filename)

@app.route('/summarize', methods=['POST'])
def summarize():
    filename = request.form.get('filename')
    summary_type = request.form.get('summary_type')
    
    with open(filename, 'r') as file:
        text = file.read()
    
    try:
        if summary_type == 'bart':
            summary = bart_summarizer(text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
        elif summary_type == 'bert':
            summary = bert_summarizer(text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
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
