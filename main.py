from flask import Flask, render_template, request, redirect, url_for, session
from transformers import pipeline
import os
import textract
import requests
from ocr_processing import process_image
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from quiz_generator import generate_quiz

app = Flask(__name__)
app.secret_key = "Fg4bCUP3odF0ZvMgIS3wqJudc30Us0nv"

# Load summarization pipelines
bart_summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
bert_summarizer = pipeline("summarization", model="bert-base-uncased")

# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def main():
    return render_template("index.html")

@app.route('/process_image', methods=['POST'])
def process_image_route():
    filename = request.form.get('filename')
    ocr_option = request.form.get('ocr_option')
    
    output_text = process_image(filename, ocr_option)
    output_filename = f"{filename}_output.txt"
    with open(output_filename, 'w') as output_file:
        output_file.write(output_text)
    
    return render_template("select_summary.html", filename=output_filename)

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if request.method == 'POST':
#         option = request.form.get('option')
#         file = request.files['file']

#         if file and option:
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)

#             if option == 'quiz':
#                 if not filename.endswith('.txt'):
#                     return render_template("ack.html", message="Only text files are supported for quiz generation.")
#                 return redirect(url_for('select_quiz', filename=filename))
#             # Other options (e.g., image, link) remain as they are.

#     return render_template("ack.html", message="Invalid file upload or option selected.")


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        option = request.form.get('option')

        # if option == 'quiz':
        #     return render_template("select_quiz.html", filename=request.form.get('filename'))
        
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
        elif option == 'quiz' and 'quiz' in request.files and request.files['quiz'].filename != '':
            quiz_file = request.files['quiz']
            # print("\n\n\n\n\n")
            # print("Quiz File?:", quiz_file)
            # print("\n\n\n\n\n")
            filename = quiz_file.filename
            # print("\n\n\n\n\n")
            # print("Filename:", filename)
            # print("\n\n\n\n\n")
            quiz_file.save(filename)
            try:
                # extracted_text = textract.process(filename).decode('utf-8')
                # text_filename = f"{filename}_text.txt"
                # with open(filename, "w", encoding="utf-8") as text_file:
                #     text_file.write(extracted_text)
                # return render_template("select_summary.html", filename=filename)
                # return redirect('/select_quiz/<filename>')
                return render_template("select_quiz.html", filename=filename)
            except Exception as e:
                message = f"Error processing the TXT file: {e}"
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

        else:
            message = "Please select a valid option and submit the required information."
            return render_template("ack.html", message=message)


# @app.route('/select_quiz/<filename>')
# def select_quiz(filename):
#     return render_template("select_quiz.html", filename=filename)


@app.route('/generate_quiz', methods=['POST'])
def generate_quiz_route():
    filename = request.form.get('filename')
    if not filename or not os.path.exists(filename):
        return render_template("ack.html", message="The file for quiz generation was not found.")
    
    num_questions = int(request.form.get('num_questions', 5))  # Default to 5 questions
    try:
        with open(filename, 'r') as file:
            text = file.read()

        quiz = generate_quiz(text, num_questions)
        session['quiz'] = quiz  # Store the quiz in the session for result evaluation
        return render_template("quiz.html", quiz=quiz)
    except Exception as e:
        message = f"Error generating quiz: {e}"
        return render_template("ack.html", message=message)



@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    user_answers = request.form.to_dict()
    quiz = session.get('quiz', [])
    results = []
    score = 0

    for i, q in enumerate(quiz):
        user_answer = user_answers.get(f'q{i + 1}')
        correct = user_answer == q['answer']
        if correct:
            score += 1
        results.append({
            "question": q['question'],
            "user_answer": user_answer,
            "correct_answer": q['answer'],
            "correct": correct
        })

    total = len(quiz)
    return render_template("results.html", score=score, total=total, results=results)



@app.route('/summarize', methods=['POST'])
def summarize():
    filename = request.form.get('filename')
    summary_type = request.form.get('summary_type')
    summary_length = request.form.get('summary_length')

    with open(filename, 'r', encoding="utf-8") as file:
        text = file.read()

    max_input_length = 512  # Model's input token limit

    if summary_length == 'short':
        max_output_length = 50
    elif summary_length == 'medium':
        max_output_length = 130
    elif summary_length == 'long':
        max_output_length = 250
    else:
        max_output_length = 130

    truncated_text = text[:max_input_length]

    try:
        if summary_type == 'bart':
            summary = bart_summarizer(truncated_text, max_length=max_output_length, min_length=max_output_length // 2, do_sample=False)[0]['summary_text']
        elif summary_type == 'bert':
            summary = bert_summarizer(truncated_text, max_length=max_output_length, min_length=max_output_length // 2, do_sample=False)[0]['summary_text']
        else:
            summary = "Invalid summary type selected."

        summary_filename = f"{filename}_summary.txt"
        with open(summary_filename, 'w', encoding="utf-8") as summary_file:
            summary_file.write(summary)

        message = f"Summary generated and saved to {summary_filename} using {summary_type.upper()} with {summary_length} length."
    except Exception as e:
        message = f"Error during summarization: {e}"

    return render_template("ack.html", message=message)


if __name__ == '__main__':
    app.run(debug=True)
