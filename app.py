from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import random
import pdfplumber
from model.resume_parser import extract_skills
from model.job_matcher import match_jobs

app = Flask(__name__)

# ------------------------------
# Configuration
# ------------------------------
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# SQLAlchemy DB URI format: mysql+driver://username:password@host/dbname
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/careerbot_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------------
# Database Models
# ------------------------------
class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255))
    option_b = db.Column(db.String(255))
    option_c = db.Column(db.String(255))
    option_d = db.Column(db.String(255))
    correct_option = db.Column(db.String(1))  # A, B, C, or D

# ------------------------------
# Home Page & Resume Upload
# ------------------------------
@app.route('/', methods=['GET', 'POST'])
def home():
    year = datetime.now().year
    if request.method == 'POST':
        file = request.files.get('resume')
        if file and file.filename.endswith('.pdf'):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                with pdfplumber.open(filepath) as pdf:
                    content = ''.join(page.extract_text() or '' for page in pdf.pages)
            except Exception as e:
                print("❌ PDF extraction error:", e)
                content = ''

            try:
                resume = Resume(filename=filename, content=content)
                db.session.add(resume)
                db.session.commit()
            except Exception as e:
                print("❌ DB INSERT error:", e)

            skills = extract_skills(content)
            matches = match_jobs(skills)
            return render_template('result.html', skills=skills, matches=matches)

    return render_template('index.html', year=year)

# ------------------------------
# Upload Page
# ------------------------------
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('resume')
        if file and file.filename.endswith('.pdf'):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                with pdfplumber.open(filepath) as pdf:
                    content = ''.join(page.extract_text() or '' for page in pdf.pages)
            except Exception as e:
                print("❌ PDF parse error:", e)
                content = ''

            try:
                resume = Resume(filename=filename, content=content)
                db.session.add(resume)
                db.session.commit()
            except Exception as e:
                print("❌ DB INSERT error:", e)

            skills = extract_skills(content)
            matches = match_jobs(skills)
            return render_template('result.html', skills=skills, matches=matches)

    return render_template('upload.html')

# ------------------------------
# Result Page
# ------------------------------
@app.route('/result')
def result():
    return render_template('result.html', skills=[], matches=[])

# ------------------------------
# Chatbot Page
# ------------------------------
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

# ------------------------------
# Category Listing Page
# ------------------------------
@app.route('/category/<domain>')
def category_page(domain):
    domain_titles = {
        "software": "Software",
        "civil": "Civils",
        "banking": "Banking",
        "medical": "Medical",
        "agriculture": "Agriculture",
        "govt": "Government Exams"
    }

    job_roles = {
        "civil": ["ias", "ips", "group-i", "ifs"],
        "software": ["fullstack", "datascientist", "backend", "frontend", "devops"],
        "banking": ["po", "clerk", "so"],
        "medical": ["nurse", "doctor", "surgeon", "pharmacist"],
        "agriculture": ["agriculture-officer", "scientist", "researcher"],
        "govt": ["ssc", "rrb", "psu"]
    }

    title = domain_titles.get(domain, "Unknown Domain")
    roles = job_roles.get(domain, [])
    return render_template('category.html', domain=domain, title=title, roles=roles)

# ------------------------------
# Role-Specific Page
# ------------------------------
@app.route('/category/<domain>/<role>')
def role_page(domain, role):
    template_path = f'roles/{role}.html'
    try:
        return render_template(template_path, domain=domain)
    except Exception as e:
        print(f"❌ Template error for role '{role}':", e)
        return render_template('error.html', message=f"No detailed page found for {role.upper()}.")

# ------------------------------
# Quiz Page
# ------------------------------
@app.route('/quiz')
def quiz():
    try:
        questions = QuizQuestion.query.all()
        random.shuffle(questions)

        structured_questions = []
        for q in questions:
            structured_questions.append({
                'id': q.id,
                'question': q.question,
                'options': [
                    {'label': 'A', 'text': q.option_a},
                    {'label': 'B', 'text': q.option_b},
                    {'label': 'C', 'text': q.option_c},
                    {'label': 'D', 'text': q.option_d}
                ]
            })

        # ✅ Debug print to check if questions are loaded
        print("Loaded questions:", structured_questions)

        return render_template('quiz.html', questions=structured_questions)
    except Exception as e:
        print("Quiz DB error:", e)
        return render_template('error.html', message="Quiz loading failed.")


@app.route('/quiz/submit', methods=['POST'])
def quiz_submit():
    try:
        correct_answers = {str(q.id): q.correct_option for q in QuizQuestion.query.all()}
        score = 0
        for qid, correct in correct_answers.items():
            user_ans = request.form.get(f'q{qid}')
            if user_ans and user_ans.upper() == correct:
                score += 1

        return render_template('quiz_result.html', score=score, total=len(correct_answers))
    except Exception as e:
        print("Quiz submission error:", e)
        return render_template('error.html', message="Quiz submission failed.")

# ------------------------------
# Run the App
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
