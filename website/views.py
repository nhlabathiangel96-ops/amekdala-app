import json
from flask import Blueprint, render_template, flash, request, jsonify, url_for, redirect
from flask_login import login_required, current_user
from . models import Note, TestResult, User
from . import db
import os
from google import genai
from dotenv import load_dotenv

# Load the secret key from the .env file
load_dotenv()

# 1. Create the client using your API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    # Fetch test results (for the Grades page later)
    results = TestResult.query.filter_by(user_id=current_user.id).order_by(
        TestResult.date_taken.desc()).all()

    # Dummy data for the new dashboard
    tasks = [
        {"name": "Math Assignment 1", "due": "Friday, 24 Oct", "status": "Pending"},
        {"name": "Read Ubonakele Chapter 2",
            "due": "Monday, 27 Oct", "status": "Pending"},
        {"name": "Physics Lab Report", "due": "Overdue", "status": "Overdue"}
    ]

    return render_template("home.html", user=current_user, results=results, tasks=tasks)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    data = request.get_json()
    noteId = data.get('noteId')

    note = Note.query.get(noteId)

    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({}), 200


@views.route('/subject/<subject_name>')
@login_required
def subject_dashboard(subject_name):
    # This takes the URL (e.g., 'mathematics') and formats it nicely (e.g., 'Mathematics')
    formatted_name = subject_name.capitalize()

    # If you wanted to handle special names like 'isiNdebele', you could do:
    if subject_name.lower() == 'isindebele':
        formatted_name = 'IsiNdebele'
    elif subject_name.lower() == 'life-sciences':
        formatted_name = 'Life Sciences'
    elif subject_name.lower() == 'physics':
        formatted_name = 'Physical Sciences'

    return render_template('subject.html', subject_name=formatted_name)


@views.route('/subject/<subject_name>/diagnostic')
@login_required
def diagnostic_tests(subject_name):
    # Format the name for display
    formatted_name = subject_name.capitalize()
    if subject_name.lower() == 'isindebele':
        formatted_name = 'IsiNdebele'
    elif subject_name.lower() == 'life-sciences':
        formatted_name = 'Life Sciences'
    elif subject_name.lower() == 'physics':
        formatted_name = 'Physical Sciences'

    return render_template('diagnostic.html', subject_name=formatted_name)


@views.route('/quiz')
@login_required
def quiz():
    return render_template("quiz.html")


@views.route('/submit-quiz', methods=['POST'])
@login_required
def submit_quiz():
    q1_answer = request.form.get('q1')
    q2_answer = request.form.get('q2')

    correct_answers = {'q1': 'B', 'q2': 'B'}
    score = 0
    total_questions = len(correct_answers)

    if q1_answer == correct_answers['q1']:
        score += 1
    if q2_answer == correct_answers['q2']:
        score += 1

    percentage = int((score / total_questions) * 100)

    # --- NEW CODE: SAVE TO DATABASE ---
    new_result = TestResult(
        score=percentage,
        subject="Mathematics",
        test_type="Pre-Test",
        user_id=current_user.id
    )
    db.session.add(new_result)
    db.session.commit()
    # ----------------------------------

    return render_template('results.html', score=percentage, correct=score, total=total_questions)


@views.route('/subject/<subject_name>/ai-guide')
@login_required
def ai_guide(subject_name):
    # 1. Format the name
    formatted_name = subject_name.capitalize()
    if subject_name.lower() == 'isindebele':
        formatted_name = 'IsiNdebele'
    elif subject_name.lower() == 'life-sciences':
        formatted_name = 'Life Sciences'
    elif subject_name.lower() == 'physics':
        formatted_name = 'Physical Sciences'

    # 2. The prompt
    prompt = f"Act as a Grade 12 South African tutor. Provide a short, encouraging, 3-point study guide for {formatted_name}. Keep it under 100 words and focus on how to avoid mental fatigue."

    # 3. The AI call
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        ai_text = response.text
    except Exception as e:
        ai_text = "Sorry, the AI is currently unavailable. Please try again later."
        print(f"AI Error: {e}")

    return render_template('ai_guide.html', subject_name=formatted_name, ai_text=ai_text)

# Route to show the learning style quiz


@views.route('/learning-style-quiz')
@login_required
def learning_style_quiz():
    return render_template('learning_style.html')

# Route to save the quiz result


@views.route('/save-learning-style', methods=['POST'])
@login_required
def save_learning_style():
    style = request.form.get('style')
    current_user.learning_style = style
    db.session.commit()
    flash(
        f'Your learning style has been saved as {style}!', category='success')
    return redirect(url_for('views.hotspot'))

# Route to show the Hotspot (find partners)


@views.route('/hotspot')
@login_required
def hotspot():
    # Find all users with the same learning style (excluding the current user)
    partners = User.query.filter(
        User.learning_style == current_user.learning_style,
        User.id != current_user.id
    ).all()
    return render_template('hotspot.html', partners=partners)


@views.route('/subject/<subject_name>/library')
@login_required
def content_library(subject_name):
    formatted_name = subject_name.capitalize()
    if subject_name.lower() == 'isindebele':
        formatted_name = 'IsiNdebele'
    elif subject_name.lower() == 'life-sciences':
        formatted_name = 'Life Sciences'
    elif subject_name.lower() == 'physics':
        formatted_name = 'Physical Sciences'

    return render_template('library.html', subject_name=formatted_name)


@views.route('/subject/<subject_name>/papers')
@login_required
def papers(subject_name):
    # Check what the URL actually is
    formatted_name = subject_name.capitalize()

    # Standardize the name for the template logic
    if 'life' in subject_name.lower():
        formatted_name = 'Life Sciences'
        subject_name = 'life-sciences'  # Force the name to match our HTML logic
    elif 'isi' in subject_name.lower():
        formatted_name = 'IsiNdebele'
        subject_name = 'isindebele'
    elif 'phys' in subject_name.lower():
        formatted_name = 'Physical Sciences'
        subject_name = 'physics'
    elif 'math' in subject_name.lower():
        subject_name = 'mathematics'
    elif 'eng' in subject_name.lower():
        subject_name = 'english'

    return render_template('papers.html', subject_name=formatted_name, subject_key=subject_name)


@views.route('/grades')
@login_required
def grades():
    results = TestResult.query.filter_by(user_id=current_user.id).order_by(
        TestResult.date_taken.desc()).all()
    return render_template('grades.html', results=results)


@views.route('/calendar')
@login_required
def school_calendar():
    return render_template('calendar.html')
