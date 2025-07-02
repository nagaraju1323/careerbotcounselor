from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from datetime import datetime
import os
import pdfplumber
from model.resume_parser import extract_skills
from model.job_matcher import match_jobs

app = Flask(__name__)

# Upload folder setup
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL configuration (XAMPP)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'careerbot_db'

mysql = MySQL(app)

# Home + Upload route
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
                content = ''
                print("PDF extraction error:", e)

            # Save to MySQL
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO resumes (filename, content) VALUES (%s, %s)",
                (filename, content)
            )
            mysql.connection.commit()
            cur.close()

            # Analyze
            skills = extract_skills(content)
            matches = match_jobs(skills)

            return render_template('result.html', skills=skills, matches=matches)

    return render_template('index.html', year=year)



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('resume')
        if file and file.filename.endswith('.pdf'):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Extract content
            try:
                with pdfplumber.open(filepath) as pdf:
                    content = ''.join(page.extract_text() or '' for page in pdf.pages)
            except Exception as e:
                content = ''
                print("PDF parse error:", e)

            # Save to MySQL
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO resumes (filename, content) VALUES (%s, %s)",
                (filename, content)
            )
            mysql.connection.commit()
            cur.close()

            # Analyze
            skills = extract_skills(content)
            matches = match_jobs(skills)

            return render_template('result.html', skills=skills, matches=matches)

    return render_template('upload.html')


# Result page
@app.route('/result')
def result():
    return render_template('result.html', skills=[], matches=[])

# Chatbot page
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

# Category page
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

# Role-specific page
@app.route('/category/<domain>/<role>')
def role_page(domain, role):
    # Construct the expected path: templates/roles/{role}.html
    template_path = f'roles/{role}.html'
    try:
        return render_template(template_path, domain=domain)
    except Exception as e:
        print(f"Template loading error for role '{role}': {e}")
        return render_template('error.html', message=f"No detailed page found for {role.upper()}.")


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
