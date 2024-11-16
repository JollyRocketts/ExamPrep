import random
from transformers import pipeline

# Use a compatible model
question_generator = pipeline("text2text-generation", model="t5-small")

def generate_quiz(text, num_questions=5):
    """
    Generate a quiz with multiple-choice questions from input text.
    """
    quiz = []

    for _ in range(num_questions):
        # Generate a single question at a time
        question_output = question_generator(
            f"generate questions: {text}",
            max_length=512,
            num_return_sequences=1,  # Always return one question per call
            do_sample=True,  # Enable sampling (to introduce randomness)
            top_k=50,  # Use top-k sampling
            temperature=1.0  # Adjust temperature for diversity
        )
        
        question_text = question_output[0]['generated_text']
        correct_answer = extract_answer(question_text)
        incorrect_answers = generate_distractors(correct_answer, text)

        quiz.append({
            "question": question_text,
            "options": [correct_answer] + incorrect_answers,
            "answer": correct_answer
        })

        # Shuffle the options
        random.shuffle(quiz[-1]["options"])

    return quiz

def extract_answer(question):
    """
    Extract the correct answer from the question text.
    """
    # Simplistic approach: extract answer after '?'
    return question.split('?')[-1].strip()

def generate_distractors(correct_answer, context):
    """
    Generate distractor options related to the correct answer.
    """
    distractors = []
    words = context.split()

    for _ in range(3):  # Generate 3 distractors
        random_word = random.choice(words)
        if random_word != correct_answer and random_word not in distractors:
            distractors.append(random_word)

    return distractors
