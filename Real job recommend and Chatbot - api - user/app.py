from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import spacy
import sqlite3
from datetime import datetime, timedelta
import os
import PyPDF2
import re
from groq import Groq
import matplotlib.pyplot as plt

nlp = spacy.load("en_core_web_sm")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def extract_exp_location(message):

    message = message.lower()

    # EXPERIENCE
    exp_match = re.search(r"(\d+)\s*(year|years|yr|yrs)", message)

    if exp_match:
        exp = int(exp_match.group(1))
    elif "fresher" in message:
        exp = 0
    else:
        exp = None

    # LOCATION
    locations = ["chennai", "bengaluru", "hyderabad"]

    location = None
    for loc in locations:
        if loc in message:
            location = loc
            break

    return exp, location


def extract_role(message):

    roles = [
        "data scientist",
        "data engineer",
        "data analyst",
        "python developer",
        "java developer",
        "ml engineer",
    ]

    for role in roles:

        if role in message:
            return role

    return None
# =====================================================
# ADVANCED NLP EXTRACTION
# =====================================================

def extract_job_entities(message):

    # spaCy NLP
    doc = nlp(message)

    message = message.lower()

    role = None
    location = None
    exp = None

    # -----------------------------------
    # ROLE EXTRACTION
    # -----------------------------------

    roles = [
        "data scientist",
        "data engineer",
        "data analyst",
        "python developer",
        "java developer",
        "ml engineer"
    ]

    for r in roles:

        if r in message:

            role = r
            break

    # -----------------------------------
    # LOCATION EXTRACTION
    # -----------------------------------

    locations = [
        "chennai",
        "bengaluru",
        "hyderabad"
    ]

    for loc in locations:

        if loc in message:

            location = loc
            break

    # -----------------------------------
    # EXPERIENCE EXTRACTION
    # -----------------------------------

    exp_match = re.search(
        r'(\d+)\s*(year|years|yr|yrs)',
        message
    )

    if exp_match:

        exp = int(exp_match.group(1))

    elif "fresher" in message:

        exp = 0

    elif "entry" in message:

        exp = 2

    elif "intermediate" in message:

        exp = 5

    elif "advanced" in message:

        exp = 8

    return role, location, exp
# =====================================================
# EXTRACT EXPERIENCE
# =====================================================

def extract_experience(text):

    text = text.lower()

    # REMOVE NEWLINES
    text = text.replace("\n", " ")

    print(text)

    # FIND NUMBER BEFORE year/years
    match = re.search(
        r'(\d+)\s*(year|years|yr|yrs)',
        text
    )

    if match:

        return int(match.group(1))

    return 0
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = "jobportal"

# =====================================================
# EXTRACT TEXT FROM PDF
# =====================================================

def extract_resume_text(pdf_path):

    text = ""

    with open(pdf_path, "rb") as file:

        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:

            text += page.extract_text()

    return text.lower()

# =====================================================
# EXTRACT SKILLS
# =====================================================

def extract_skills(text):

    skills_db = [
        "python",
        "sql",
        "machine learning",
        "ml",
        "tensorflow",
        "flask",
        "django",
        "aws",
        "power bi",
        "excel",
        "java",
        "spring",
        "spark"
    ]

    found_skills = []

    for skill in skills_db:

        if skill in text:

            found_skills.append(skill)

    return list(set(found_skills))


# =====================================================
# PREDICT ROLE
# =====================================================

def predict_role(skills):

    skills = set(skills)

    # -----------------------------------
    # PYTHON DEVELOPER
    # -----------------------------------

    if {"flask", "django"}.intersection(skills):

        return "python developer"

    # -----------------------------------
    # ML ENGINEER
    # -----------------------------------

    elif {
        "tensorflow",
        "deep learning"
    }.intersection(skills):

        return "ml engineer"

    # -----------------------------------
    # DATA ENGINEER
    # -----------------------------------

    elif {
        "aws",
        "spark"
    }.intersection(skills):

        return "data engineer"

    # -----------------------------------
    # DATA ANALYST
    # -----------------------------------

    elif {
        "excel",
        "power bi",
        "tableau"
    }.intersection(skills):

        return "data analyst"

    # -----------------------------------
    # JAVA DEVELOPER
    # -----------------------------------

    elif {
        "java",
        "spring",
        "hibernate"
    }.intersection(skills):

        return "java developer"

    # -----------------------------------
    # DATA SCIENTIST
    # -----------------------------------

    elif {
        "machine learning",
        "ml",
        "statistics"
    }.intersection(skills):

        return "data scientist"

    return "python developer"

# =====================================================
# TIME AGO FUNCTION
# =====================================================


def time_ago(date_string):

    posted_date = datetime.strptime(date_string, "%Y-%m-%d")
    now = datetime.now()

    diff = now - posted_date
    days = diff.days

    if days == 0:
        return "Today"
    elif days == 1:
        return "1 day ago"
    elif days < 30:
        return f"{days} days ago"
    elif days < 365:
        months = days // 30
        return f"{months} months ago"
    else:
        years = days // 365
        return f"{years} years ago"


# =====================================================
# DATABASE SETUP
# =====================================================


def create_database():

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    # JOB TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        role TEXT,
        skills TEXT,
        job_type TEXT,
        experience INTEGER,
        location TEXT,
        level TEXT,
        posted_date TEXT
    )
    """)
    # USER TABLE
    cursor.execute("""

    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        password TEXT,

        plan TEXT

    )

    """)
    


    # ⭐ NEW: CHAT HISTORY TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            bot_reply TEXT,
            created_at TEXT
        )
    """)
    # DEFAULT USERS

    cursor.execute("""
    SELECT COUNT(*) FROM users
    """)

    count = cursor.fetchone()[0]

    if count == 0:

        cursor.execute("""

        INSERT INTO users
        (username, password, plan)

        VALUES
        ('freeuser', '123', 'free')

        """)

        cursor.execute("""

        INSERT INTO users
        (username, password, plan)

        VALUES
        ('premiumuser', '123', 'premium')

        """)
    conn.commit()

    conn.close()


# =====================================================
# SAVE CHAT HISTORY (NEW)
# =====================================================


def save_chat(user_msg, bot_reply):

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chat_history (user_message, bot_reply, created_at)
        VALUES (?, ?, ?)
    """,
        (user_msg, bot_reply, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )

    conn.commit()
    conn.close()


# =====================================================
# JOB QUESTION FILTER (NEW)
# =====================================================


def is_job_question(msg):

    keywords = [
        "job",
        "jobs",
        "career",
        "skills",
        "company",
        "hire",
        "hiring",
        "role",
        "recommend",
        "latest",
        "experience",
        "fresher",
        "entry",
        "intermediate",
        "advanced",
        "trend",
        "trending",
        "market",
        "graph",
        "roadmap",
        "guidance",
        "career guidance",
        "learning",
        "learn",
        "certification",
        "certifications",
        "become",
        "suggest",
        "interview",
        "salary",
        "opening",
        "openings"
    ]

    return any(k in msg for k in keywords)


# =====================================================
# INSERT DEFAULT JOBS
# =====================================================


def insert_default_jobs():

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    count = cursor.fetchone()[0]

    if count == 0:

        default_jobs = [
            # CHENNAI
            ("Google", "data scientist", "python,ml,sql", 2, "chennai", "2026-05-20"),
            ("Amazon", "data engineer", "python,sql,aws", 3, "chennai", "2026-04-10"),
            (
                "Zoho",
                "python developer",
                "python,flask,django",
                1,
                "chennai",
                "2026-05-15",
            ),
            (
                "Infosys",
                "data analyst",
                "excel,sql,powerbi",
                0,
                "chennai",
                "2026-05-22",
            ),
            ("TCS", "ml engineer", "python,ml,tensorflow", 5, "chennai", "2026-03-18"),
            ("IBM", "data scientist", "python,ml,pandas", 7, "chennai", "2025-12-10"),
            # BENGALURU
            (
                "Microsoft",
                "data engineer",
                "python,sql,spark",
                4,
                "bengaluru",
                "2026-05-01",
            ),
            (
                "Flipkart",
                "data scientist",
                "python,ml,sql",
                2,
                "bengaluru",
                "2026-05-12",
            ),
            (
                "Wipro",
                "data analyst",
                "excel,sql,tableau",
                1,
                "bengaluru",
                "2026-04-25",
            ),
            (
                "Oracle",
                "java developer",
                "java,spring,sql",
                6,
                "bengaluru",
                "2026-03-30",
            ),
            (
                "Intel",
                "ml engineer",
                "python,ml,deep learning",
                8,
                "bengaluru",
                "2025-11-20",
            ),
            (
                "Accenture",
                "data scientist",
                "python,ml,aws",
                3,
                "bengaluru",
                "2026-05-18",
            ),
            # HYDERABAD
            ("Amazon", "data engineer", "python,sql,aws", 2, "hyderabad", "2026-05-10"),
            (
                "Google",
                "ml engineer",
                "python,ml,tensorflow",
                5,
                "hyderabad",
                "2026-04-05",
            ),
            (
                "Tech Mahindra",
                "data analyst",
                "excel,sql,powerbi",
                0,
                "hyderabad",
                "2026-05-21",
            ),
            (
                "Cognizant",
                "python developer",
                "python,django,flask",
                3,
                "hyderabad",
                "2026-03-28",
            ),
            (
                "Dell",
                "data scientist",
                "python,ml,statistics",
                6,
                "hyderabad",
                "2026-02-15",
            ),
            (
                "Capgemini",
                "java developer",
                "java,spring,hibernate",
                4,
                "hyderabad",
                "2026-05-02",
            ),
            # =========================================
            # NOISY DATA
            # =========================================
            ("XYZ Corp", "java developer", "python,django", 2, "chennai", "2024-05-23"),
            (
                "FakeData Inc",
                "data scientist",
                "java,spring",
                3,
                "bengaluru",
                "2025-05-23",
            ),
        ]
        cursor.executemany(
            """
        INSERT INTO jobs (
            company, role, skills,
            experience, location,
            level, posted_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            [(c, r, s, e, l, get_level(e), d) for (c, r, s, e, l, d) in default_jobs],
        )

        conn.commit()

    conn.close()


# reset DB
# if os.path.exists("jobs.db"):
#     os.remove("jobs.db")

create_database()


def get_level(exp):

    if exp == 0:
        return "fresher"
    elif 1 <= exp <= 3:
        return "entry"
    elif 4 <= exp <= 6:
        return "intermediate"
    else:
        return "advanced"


insert_default_jobs()


# =====================================================
# ROLE SKILL REFERENCE
# =====================================================

role_skill_reference = {

    # =========================================
    # DATA SCIENTIST
    # =========================================

    "data scientist": {

        "python",
        "ml",
        "pandas",
        "numpy",
        "sql",
        "statistics",
        "tensorflow",
        "data visualization"

    },

    # =========================================
    # DATA ENGINEER
    # =========================================

    "data engineer": {

        "python",
        "sql",
        "spark",
        "aws",
        "etl",
        "hadoop",
        "airflow",
        "data warehouse"

    },

    # =========================================
    # DATA ANALYST
    # =========================================

    "data analyst": {

        "excel",
        "sql",
        "power bi",
        "tableau",
        "python",
        "data visualization",
        "statistics"

    },

    # =========================================
    # PYTHON DEVELOPER
    # =========================================

    "python developer": {

        "python",
        "flask",
        "django",
        "sql",
        "api",
        "git",
        "html",
        "css"

    },

    # =========================================
    # JAVA DEVELOPER
    # =========================================

    "java developer": {

        "java",
        "spring",
        "hibernate",
        "sql",
        "microservices",
        "api",
        "maven",
        "git"

    },

    # =========================================
    # ML ENGINEER
    # =========================================

    "ml engineer": {

        "python",
        "ml",
        "tensorflow",
        "pytorch",
        "deep learning",
        "nlp",
        "computer vision",
        "sql"

    }
}
career_guidance = {

    "ml engineer": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "TensorFlow",
        "MLOps"
    ],

    "data scientist": [
        "Python",
        "Statistics",
        "Machine Learning",
        "Data Visualization",
        "SQL"
    ],

    "data engineer": [
        "Python",
        "SQL",
        "Spark",
        "AWS",
        "ETL"
    ],

    "python developer": [
        "Python",
        "Flask",
        "Django",
        "APIs",
        "SQL"
    ],

    "java developer": [
        "Java",
        "Spring",
        "Hibernate",
        "Microservices",
        "SQL"
    ]
}
# =====================================================
# SKILL GAP ANALYSIS
# =====================================================

def skill_gap_analysis(role, user_skills):

    role = role.lower()

    user_skills = set([
        s.lower().strip()
        for s in user_skills
    ])

    required_skills = role_skill_reference.get(
        role,
        set()
    )

    missing_skills = required_skills - user_skills

    return list(missing_skills)


# =====================================================
# JOB PORTAL FUNCTION (UNCHANGED)
# =====================================================


def job_portal(user_role, user_skills, user_exp, user_location):
    if user_role is not None:
        user_role = user_role.lower().strip()

    user_skills = set([s.lower().strip() for s in user_skills])

    primary_jobs = []
    related_jobs = []

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute(
        """SELECT company, role, skills, experience, location, level, posted_date FROM jobs"""
    )
    data = cursor.fetchall()
    conn.close()

    for row in data:

        company, role, skills_str, job_exp, job_loc, job_level, posted_date = row

        skills = set(skills_str.split(","))

        reference_skills = role_skill_reference.get(role, set())

        if len(skills) == 0:
            continue

        if len(skills.intersection(reference_skills)) == 0:
            continue

        matched = skills.intersection(user_skills)

        if len(matched) == 0:
            continue
        user_level = None

        if user_exp is not None:
            user_level = get_level(user_exp)
        if user_exp is not None:
            if job_exp is not None and abs(job_exp - user_exp) > 2:
                continue

        if user_location and job_loc != user_location:
            continue
        if user_level is not None:
            if job_level != user_level:
                continue
        score = (len(matched) / len(skills)) * 100
        # =========================================
        # USER MATCH
        # ===========================
        level = (
            "Strong Match"
            if score >= 70
            else "Moderate Match" if score >= 40 else "Weak Match"
        )

        job_data = {
            "company": company,
            "role": role,
            "matched_skills": list(matched),
            "score": round(score, 2),
            "match_level": level,  # AI match level
            "job_level": job_level,  # fresher/entry/intermediate
            "experience": job_exp,
            "location": job_loc,
            "posted_date": posted_date,
            "posted": time_ago(posted_date),
        }

        if user_role is not None and role.lower() == user_role.lower():
            primary_jobs.append(job_data)
        else:
            related_jobs.append(job_data)

    return primary_jobs, related_jobs
    # =====================================================
    # ML JOB RECOMMENDATION
    # =====================================================

def ml_job_recommendation(user_skills):

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        company,
        role,
        skills,
        experience,
        location,
        level,
        posted_date
    FROM jobs
    """)

    jobs = cursor.fetchall()

    conn.close()
    
    # -----------------------------------
    # JOB SKILLS
    # -----------------------------------

    job_skill_texts = []

    for job in jobs:

        job_skill_texts.append(job[2])

    # -----------------------------------
    # USER SKILLS
    # -----------------------------------

    user_text = " ".join(user_skills)

    # -----------------------------------
    # TF-IDF
    # -----------------------------------

    documents = [user_text] + job_skill_texts

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(documents)

    # -----------------------------------
    # COSINE SIMILARITY
    # -----------------------------------

    similarity_scores = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    )

    similarity_scores = similarity_scores.flatten()

    # -----------------------------------
    # STORE RESULTS
    # -----------------------------------

    recommendations = []

    for i, score in enumerate(similarity_scores):
            # CONVERT TO PERCENTAGE
        similarity = score * 100

        # REMOVE LOW MATCH JOBS
        if similarity < 40:
            continue

        company, role, skills, exp, loc, level, posted = jobs[i]
        # -----------------------------------
        # REMOVE NOISY DATA
        # -----------------------------------

        reference_skills = role_skill_reference.get(role, set())

        job_skills_set = set(skills.split(","))

        if len(job_skills_set.intersection(reference_skills)) == 0:
            continue
        recommendations.append({

            "company": company,
            "role": role,
            "skills": skills,
            "experience": exp,
            "location": loc,
            "level": level,
            "posted_date": posted,
            "score": round(similarity, 2)

        })

    # -----------------------------------
    # SORT HIGH TO LOW
    # -----------------------------------

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return recommendations
# =====================================================
# JOB TREND PREDICTION
# =====================================================

def job_trend_prediction():

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT role, skills
    FROM jobs
    """)

    jobs = cursor.fetchall()

    conn.close()

    # -----------------------------------
    # COUNT SKILLS
    # -----------------------------------

    skill_count = {}

    role_count = {}

    for role, skills in jobs:

        # ROLE COUNT
        role_count[role] = role_count.get(role, 0) + 1

        # SKILL COUNT
        for skill in skills.split(","):

            skill = skill.strip().lower()

            skill_count[skill] = (
                skill_count.get(skill, 0) + 1
            )

    # -----------------------------------
    # SORT
    # -----------------------------------

    trending_skills = sorted(
        skill_count.items(),
        key=lambda x: x[1],
        reverse=True
    )

    trending_roles = sorted(
        role_count.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return trending_skills, trending_roles
# =====================================================
# EXPERIENCE LEVEL GRAPH
# =====================================================

def experience_level_graph():

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT level
    FROM jobs
    """)

    data = cursor.fetchall()

    conn.close()

    # -----------------------------------
    # COUNT LEVELS
    # -----------------------------------

    level_count = {
        "fresher": 0,
        "entry": 0,
        "intermediate": 0,
        "advanced": 0
    }

    for row in data:

        level = row[0]

        if level in level_count:

            level_count[level] += 1

    return level_count
# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("jobs.db")
        cursor = conn.cursor()

        cursor.execute("""

        SELECT plan
        FROM users
        WHERE username=? AND password=?

        """, (username, password))

        user = cursor.fetchone()

        conn.close()

        if user:

            session["plan"] = user[0]

            return redirect(url_for("home"))

        else:

            return "Invalid Login"

    return render_template("login.html")
# =====================================================
# HOME
# =====================================================


@app.route("/", methods=["GET", "POST"])
def home():

    primary_jobs = []
    related_jobs = []
    missing_skills = []

    if request.method == "POST":

        role = request.form["role"]
        skills = request.form["skills"].split(",")

        experience = int(request.form["experience"])
        location = request.form["location"]

        primary_jobs, related_jobs = job_portal(role, skills, experience, location)
        missing_skills = skill_gap_analysis(role, skills)
                                            
    return render_template(
        "index.html", primary_jobs=primary_jobs, related_jobs=related_jobs, missing_skills=missing_skills
    )


# =====================================================
# POST JOB
# =====================================================


@app.route("/post-job", methods=["GET", "POST"])
def post_job():

    if request.method == "POST":

        company = request.form["company"]

        role = request.form["role"].lower().strip()

        # FIXED SKILLS PART (ONLY CHANGE)
        skills = request.form["skills"].split(",")

        skills = [s.lower().strip() for s in skills]

        # DO NOT modify user input with reference skills
        clean_skills = list(set(skills))

        conn = sqlite3.connect("jobs.db")

        cursor = conn.cursor()

        experience = int(request.form["experience"])
        location = request.form["location"].lower()

        level = get_level(experience)

        cursor.execute(
            """
        INSERT INTO jobs
        (
            company,
            role,
            skills,
            job_type,
            experience,
            location,
            level,
            posted_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                company,
                role,
                ",".join(clean_skills),
                "posted",
                experience,
                location,
                level,
                datetime.now().strftime("%Y-%m-%d"),
            ),
        )
        conn.commit()

        conn.close()

        session["message"] = "Job Posted Successfully!"

        session["latest_job"] = {
            "company": company,
            "role": role,
            "skills": ", ".join(clean_skills),
            "posted_date": datetime.now().strftime("%Y-%m-%d"),
            "posted": "Today",
        }

        return redirect(url_for("post_job"))

    latest_job = session.pop("latest_job", None)

    message = session.pop("message", None)

    return render_template("post_job.html", latest_job=latest_job, message=message)
# =====================================================
# RESUME ANALYZER
# =====================================================

@app.route("/resume", methods=["GET", "POST"])
def resume():
    # =========================================
    # PREMIUM CHECK
    # =========================================

    if session.get("plan") != "premium":

        return """

        <h2>
        Premium Users Only 🔒
        </h2>

        """

    jobs = []

    extracted = {}

    if request.method == "POST":

        file = request.files["resume"]

        path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            file.filename
        )

        file.save(path)

        # -----------------------------
        # EXTRACT TEXT
        # -----------------------------

        text = extract_resume_text(path)

        # -----------------------------
        # EXTRACT DETAILS
        # -----------------------------

        skills = extract_skills(text)

        experience = extract_experience(text)

        role = predict_role(skills)

        # -----------------------------
        # JOB RECOMMENDATION
        # -----------------------------

        primary_jobs, related_jobs = job_portal(
            role,
            skills,
            experience,
            None
        )

        jobs = primary_jobs 

        extracted = {

            "role": role,
            "skills": skills,
            "experience": experience
        }

    return render_template(
        "resume.html",
        jobs=jobs,
        extracted=extracted
    )

    
# ===================================================
# ========API ENDPOINT FOR AI CHATBOT (NEW)========
# ===================================================   
def ask_ai(message):

    completion = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[

            {
                "role": "system",
                "content": """

                        You are an AI Career Assistant for a Job Portal.

                        You ONLY answer questions related to:

                        - jobs
                        - careers
                        - skills
                        - salary
                        - interview questions
                        - certifications
                        - learning path
                        - roadmap
                        - resume
                        - hiring
                        - AI careers
                        - technology careers

                        Examples:
                        - How to become ML Engineer
                        - Best skills for Data Science
                        - SQL interview questions
                        - Salary for Python Developer
                        - Certifications for cloud jobs
                        Keep responses:
                        - short
                        - professional
                        - easy to read
                        - maximum 6 bullet points
                        - avoid very long paragraphs
                        
                        If user asks unrelated questions,
                        reply ONLY:

                        I answer only job-related questions.

                        """
            },

            {
                "role": "user",
                "content": message
            }

        ]

    )

    reply = completion.choices[0].message.content

    reply = reply.replace("\n", "<br>")

    reply = f"""

    <div class='ai-chat-card'>

        <h3>AI Career Assistant</h3>

        <div class='ai-response'>

            {reply}

        </div>

    </div>

    """

    return reply
# =====================================================
# CHAT HISTORY (NEW)
# =====================================================
@app.route("/chat-history")
def chat_history():

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_message, bot_reply, created_at
        FROM chat_history
        ORDER BY id DESC
    """)

    data = cursor.fetchall()
    conn.close()

    html = "<h2>Chat History</h2>"

    for row in data:

        html += f"""
        <div style="background:white;padding:10px;margin:10px;border-radius:10px">
            <p><b>User:</b> {row[0]}</p>
            <p><b>Bot:</b> {row[1]}</p>
            <p style="color:gray;font-size:12px">{row[2]}</p>
        </div>
        """

    return html


# =====================================================
# CHATBOT
# =====================================================
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    message = data.get("message", "").lower().strip()

    # =====================================================
    # BLOCK NON-JOB QUESTIONS
    # =====================================================

    if not is_job_question(message):
        reply = "I only answer job-related questions like jobs, skills, companies, and careers."
        save_chat(message, reply)
        return jsonify({"reply": reply})

    # =====================================================
    # GREETING
    # =====================================================

    if message in ["hi", "hello", "hey"]:

        reply = """
        Hello 👋<br><br>

        Ask me about:<br><br>

        • Latest jobs<br>
        • Skills<br>
        • Careers<br>
        • Hiring<br>
        • Recommendations
        """

        save_chat(message, reply)
        return jsonify({"reply": reply})
    # =====================================================
    # LATEST JOBS
    # =====================================================

    if "latest" in message or message == "jobs" or message == "show jobs":

        conn = sqlite3.connect("jobs.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                company,
                role,
                skills,
                experience,
                location,
                level,
                posted_date
            FROM jobs
            ORDER BY posted_date DESC
        """)

        jobs = cursor.fetchall()
        conn.close()

        html = "<h3>Latest Jobs</h3>"

        for job in jobs:

            posted_date = datetime.strptime(job[6], "%Y-%m-%d")
            six_months_ago = datetime.now() - timedelta(days=180)

            if posted_date < six_months_ago:
                continue

            role = job[1]
            skills_set = set(job[2].split(","))
            if len(skills_set) == 0:
                continue

            score = 100

            html += f"""
            <div class='chat-job-card'>

                <h4>{job[0]}</h4>

                <p><b>Role:</b> {job[1]}</p>

                <p><b>Skills:</b> {job[2]}</p>

                <p><b>Match:</b> {score:.2f}%</p>

                <p><b>Date:</b> {job[6]}</p>

                <p><b>Experience:</b> {job[3]} years</p>

                <p><b>Location:</b> {job[4]}</p>

                <p><b>Level:</b> {job[5]}</p>

                <span class='posted'>
                {time_ago(job[6])}
                </span>

            </div>
            """

        save_chat(message, html)
        return jsonify({"reply": html})
    # =====================================================
    # JOB TRENDS
    # =====================================================

    if (
        (
            "trend" in message
            or "trending" in message
            or "trends" in message
        )

        and

        "experience" not in message
        and "market" not in message
        and "graph" not in message
    ):

        trending_skills, trending_roles = (
            job_trend_prediction()
        )

        html = """

        <div class='chat-job-card'>

            <h3>Job Trend Prediction</h3>

            <h4>Trending Skills</h4>

        """

        for skill, count in trending_skills[:5]:

            html += f"""

            <p>
            • {skill.upper()}
            ({count} jobs)
            </p>

            """

        html += """

        <h4>High Demand Roles</h4>

        """

        for role, count in trending_roles[:5]:

            html += f"""

            <p>
            • {role.title()}
            ({count} openings)
            </p>

            """

        html += """

        <br>

        <p>
        Python + AI + Cloud skills
        are highly trending in the market.
        </p>

        </div>

        """

        save_chat(message, html)

        return jsonify({"reply": html})

    # =====================================================
    # EXPERIENCE GRAPH
    # =====================================================

    if (
        "experience trends" in message
        or "market demand" in message
        or "experience graph" in message
        ):
            # PREMIUM CHECK
        if session.get("plan") == "free":

            return jsonify({

                "reply": """

                <div class='chat-job-card'>

                    <h3>Premium Feature 🔒</h3>

                    <p>
                    Upgrade to Premium
                    to access Market Demand Graphs.
                    </p>

                </div>

                """

            })
        levels = experience_level_graph()

        labels = list(levels.keys())

        counts = list(levels.values())

        plt.figure(figsize=(8,5))

        plt.bar(
                labels,
                counts,
                color=["green", "blue", "orange", "red"]
            )

        plt.title("Market Demand by Experience Level")

        plt.xlabel("Experience Level")

        plt.ylabel("Number of Jobs")
        
        plt.tight_layout()

        plt.savefig("static/graph.png")
        
        plt.close()

        html = """

        <div class='chat-job-card'>

            <h3>Market Demand Analysis</h3>

            <img src="/static/graph.png"
            width="100%">

        </div>

        """

        save_chat(message, html)

        return jsonify({"reply": html})
    # =========================================
    # AI CAREER GUIDANCE
    # =========================================

    if (
        "roadmap" in message
        or "career guidance" in message
        or "career roadmap" in message
        or "learning path" in message
        
    ):

        role = extract_role(message)

        if role is None:

            role = "ml engineer"

        roadmap = career_guidance.get(role, [])

        html = f"""

        <div class='chat-job-card'>

            <h3>AI Career Guidance</h3>

            <p>
            To become a
            <b>{role.title()}</b>
            learn:
            </p>

        """

        for step in roadmap:

            html += f"""

            <p>
            ➜ {step}
            </p>

            """

        html += "</div>"

        save_chat(message, html)

        return jsonify({"reply": html})
    # =====================================================
    # RECOMMEND
    # =====================================================

    if (
        message == "recommendation"
        or message == "recommendations"
        or message == "recommend"
        or message == "recommend jobs"
    ):

        reply = """

        <div class='chat-job-card'>

            <h3>Select Recommendation Type</h3>

            <div class='recommend-buttons'>

                <button onclick="sendSuggestion('python recommendation')">
                Python Recommendation
                </button>

                <button onclick="sendSuggestion('java recommendation')">
                Java Recommendation
                </button>

                <button onclick="sendSuggestion('data scientist recommendation')">
                Data Scientist Recommendation
                </button>

                <button onclick="sendSuggestion('data engineer recommendation')">
                Data Engineer Recommendation
                </button>

                <button onclick="sendSuggestion('data analyst recommendation')">
                Data Analyst Recommendation
                </button>

                <button onclick="sendSuggestion('ml recommendation')">
                ML Recommendation
                </button>

            </div>

            <br>

            <p><b>OR</b></p>

            <p>
            role - Data Scientist,
            skill - python
            </p>

        </div>

        """
        save_chat(message, reply)

        return jsonify({"reply": reply})

    # =====================================================
    # RECOMMENDATION
    # =====================================================

    if "role" in message and "skill" in message:

        try:

            role_part = message.split("role -")[1]
            role = role_part.split(",")[0].strip()

            skills_part = message.split("skill -")[1]
            skills = [s.strip().lower() for s in skills_part.split(",")]
            exp, location = extract_exp_location(message)


            primary_jobs, related_jobs = job_portal(role, skills, exp, location)
            missing_skills = skill_gap_analysis(
                                role,
                                skills
                                )
            html = ""
            if len(missing_skills) > 0:

                html += f"""

                <div class='chat-job-card'>

                    <h3>Skill Gap Analysis</h3>

                    <p>
                    AI detected some important skills
                    needed for becoming a strong
                    <b>{role.title()}</b>.
                    </p>

                """

                for skill in missing_skills:

                    html += f"""

                    <div class='skill-gap-item'>

                        Recommended Skill:
                        <b>{skill.upper()}</b>

                    </div>

                    """

                html += """

                    <br>

                    <p>
                    📈 Learning these skills can improve
                    your job match score and career growth.
                    </p>

                </div>

                """
            if primary_jobs:
                html += "<h3>Primary Jobs</h3>"

                for job in primary_jobs:
                    html += f"""
                    <div class='chat-job-card'>
                        <h4>{job['company']}</h4>
                        <p><b>Role:</b> {job['role']}</p>
                        <p><b>Match:</b> {job['score']}%</p>
                        <p><b>Level:</b> {job['job_level']}</p>
                        <p><b>Date:</b> {job['posted_date']}</p>
                        <span class='posted'>{job['posted']}</span>
                    </div>
                    """

            if related_jobs:
                html += "<h3>Related Jobs</h3>"

                for job in related_jobs[:3]:
                    html += f"""
                    <div class='chat-job-card'>
                        <h4>{job['company']}</h4>
                        <p><b>Role:</b> {job['role']}</p>
                        <p><b>Match:</b> {job['score']}%</p>
                        <p><b>Level:</b> {job['job_level']}</p>
                        <p><b>Date:</b> {job['posted_date']}</p>
                        <span class='posted'>{job['posted']}</span>
                    </div>
                    """

            save_chat(message, html)
            return jsonify({"reply": html})

        except:

            reply = """
            Please use format:<br><br>
            role - Data Scientist, skill - python
            """

            save_chat(message, reply)
            return jsonify({"reply": reply})

    # =====================================================
    # ML RECOMMENDATION
    # =====================================================

    if (
    "recommendation" in message
    or "python recommendation" in message
    or "java recommendation" in message
    or "data scientist recommendation" in message
    or "data engineer recommendation" in message
    or "data analyst recommendation" in message
    or "ml recommendation" in message
    ):

        skills = []

        # -----------------------------------
        # PYTHON
        # -----------------------------------

        if "python" in message:
            title = "Python Recommended Jobs"
            skills = [
                "python",
                "flask",
                "django",
                "sql"
            ]

        # -----------------------------------
        # JAVA
        # -----------------------------------

        elif "java" in message:
            title = "Java Recommended Jobs"
            skills = [
                "java",
                "spring",
                "hibernate",
                "sql"
            ]

        # -----------------------------------
        # DATA SCIENTIST
        # -----------------------------------

        elif "data scientist" in message:
            title = "Data Scientist Recommended Jobs"
            skills = [
                "python",
                "ml",
                "pandas"
            ]

        # -----------------------------------
        # DATA ENGINEER
        # -----------------------------------

        elif "data engineer" in message:
            title = "Data Engineer Recommended Jobs"
            skills = [
                "python",
                "sql",
                "spark",
                "aws"
            ]

        # -----------------------------------
        # DATA ANALYST
        # -----------------------------------

        elif "data analyst" in message:
            title = "Data Analyst Recommended Jobs"
            skills = [
                "excel",
                "sql",
                "power bi"
            ]

        # -----------------------------------
        # ML ENGINEER
        # -----------------------------------

        elif "ml" in message:
            title = "ML Recommended Jobs"
            skills = [
                "python",
                "tensorflow",
                "ml"
            ]

        # -----------------------------------
        # DEFAULT
        # -----------------------------------

        else:

            skills = [
                "python",
                "sql"
            ]

        # -----------------------------------
        # ML RECOMMENDATION
        # -----------------------------------

        jobs = ml_job_recommendation(skills)

        html = f"<h3>{title}</h3>"

                # FREE USER
        if session.get("plan") == "free":

            jobs_to_show = jobs[:3]

        # PREMIUM USER
        else:

            jobs_to_show = jobs[:10]

        for job in jobs_to_show:

            html += f"""

            <div class='chat-job-card'>

                <h4>{job['company']}</h4>

                <p><b>Role:</b>
                {job['role']}</p>

                <p><b>Skills:</b>
                {job['skills']}</p>

                <p><b>Experience:</b>
                {job['experience']} years</p>

                <p><b>Location:</b>
                {job['location']}</p>

                <p><b>Level:</b>
                {job['level']}</p>

                <p><b>Similarity:</b>
                {job['score']}%</p>

                <span class='posted'>
                {time_ago(job['posted_date'])}
                </span>

            </div>
            """

        save_chat(message, html)

        return jsonify({"reply": html})
    # =====================================================
    # SKILLS
    # =====================================================

    if (
    message == "skills"
    or message == "popular skills"
    ):

        reply = """
        <div class='chat-job-card'>
        <h4>Popular Skills</h4>
        <p>• Python</p>
        <p>• SQL</p>
        <p>• Machine Learning</p>
        <p>• AWS</p>
        <p>• Flask</p>
        <p>• Django</p>
        <p>• Power BI</p>
        </div>
        """

        save_chat(message, reply)
        return jsonify({"reply": reply})

    # =====================================================
    # CAREERS
    # =====================================================

    if (
    message == "career"
    or message == "careers"
    or message == "top careers"
    ):

        reply = """
        <div class='chat-job-card'>
        <h4>Top Careers</h4>
        <p>• Python Developer</p>
        <p>• Data Scientist</p>
        <p>• ML Engineer</p>
        <p>• Data Engineer</p>
        <p>• Data Analyst</p>
        </div>
        """

        save_chat(message, reply)
        return jsonify({"reply": reply})

    # =====================================================
    # HIRING
    # =====================================================

    if "hiring" in message:

        reply = """
        <div class='chat-job-card'>
        <h4>Companies Hiring</h4>
        <p>• Google</p>
        <p>• Amazon</p>
        <p>• Oracle</p>
        <p>• Infosys</p>
        <p>• Microsoft</p>
        </div>
        """

        save_chat(message, reply)
        return jsonify({"reply": reply})
   

    # =====================================================
    # AI CHATBOT
    # =====================================================

    if (

        "suggest" in message
        or "become" in message
        or "skill" in message
        or "skills" in message
        or "career" in message
        or "interview" in message
        or "certification" in message
        or "certifications" in message
        or "roadmap" in message
        or "salary" in message
        or "learning" in message
        or "learn" in message
        or "sql" in message
        or "resume" in message
        or "future" in message
        or "scope" in message
        

    ):
        # PREMIUM CHECK
        if session.get("plan") == "free":

            reply = """

            <div class='chat-job-card'>

                <h3>Premium Feature 🔒</h3>

                <p>
                Upgrade to Premium
                for AI Career Assistant.
                </p>

            </div>

            """

            return jsonify({"reply": reply})
        ai_reply = ask_ai(message)

        save_chat(message, ai_reply)

        return jsonify({
            "reply": ai_reply
        })


    # =====================================================
    # NLP JOB SEARCH
    # =====================================================

    if (

        (
            "job" in message
            or "jobs" in message
            or "experience" in message
            or "fresher" in message
            or "entry" in message
            or "intermediate" in message
            or "advanced" in message
            or "opening" in message
            or "openings" in message
        )

        and

        "resume" not in message
        and "salary" not in message
        and "interview" not in message
        and "certification" not in message
        and "roadmap" not in message
    ):

        role, location, exp = extract_job_entities(message)
        if role is None and (
            "opening" in message
            or "openings" in message
            ):
    
            conn = sqlite3.connect("jobs.db")
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    company,
                    role,
                    skills,
                    experience,
                    location,
                    level,
                    posted_date
                FROM jobs
                ORDER BY posted_date DESC
            """)

            jobs = cursor.fetchall()

            conn.close()

            html = "<h3>Latest Openings</h3>"

            for job in jobs[:5]:

                html += f"""

                <div class='chat-job-card'>

                    <h4>{job[0]}</h4>

                    <p><b>Role:</b> {job[1]}</p>

                    <p><b>Experience:</b> {job[3]} years</p>

                    <p><b>Location:</b> {job[4]}</p>

                    <p><b>Level:</b> {job[5]}</p>

                    <span class='posted'>
                    {time_ago(job[6])}
                    </span>

                </div>

                """

            return jsonify({"reply": html})

        if exp is None:

            if "fresher" in message:
                exp = 0

            elif "entry" in message:
                exp = 2

            elif "intermediate" in message:
                exp = 5

            elif "advanced" in message:
                exp = 8

            else:
                exp = None

        if location is None:
            location = None

        if role is None:
            role = None

        role_skills = {
            "data scientist": ["python", "ml"],
            "data engineer": ["python", "sql"],
            "data analyst": ["sql", "excel"],
            "python developer": ["python", "flask"],
            "java developer": ["java", "spring"],
            "ml engineer": ["python", "tensorflow"],
        }

        skills = role_skills.get(role, ["python"])

        primary_jobs, related_jobs = job_portal(
            role,
            skills,
            exp,
            location
        )
        html = ""
        # =========================================
        # PRIMARY JOBS
        # =========================================

        if primary_jobs:

            html += "<h3>Primary Jobs</h3>"

            for job in primary_jobs[:5]:

                html += f"""
                <div class='chat-job-card'>

                    <h4>{job['company']}</h4>

                    <p><b>Role:</b>
                    {job['role']}</p>

                    <p><b>Experience:</b>
                    {job['experience']} years</p>

                    <p><b>Location:</b>
                    {job['location']}</p>

                    <p><b>Level:</b>
                    {job['job_level']}</p>

                    <p><b>Match:</b>
                    {job['score']}%</p>

                    <span class='posted'>
                    {job['posted']}
                    </span>

                </div>
                """

        # =========================================
        # RELATED JOBS
        # =========================================

        if related_jobs:

            html += "<h3>Related Jobs</h3>"

            for job in related_jobs[:3]:

                html += f"""
                <div class='chat-job-card'>

                    <h4>{job['company']}</h4>

                    <p><b>Role:</b>
                    {job['role']}</p>

                    <p><b>Experience:</b>
                    {job['experience']} years</p>

                    <p><b>Location:</b>
                    {job['location']}</p>

                    <p><b>Level:</b>
                    {job['job_level']}</p>

                    <p><b>Match:</b>
                    {job['score']}%</p>

                    <span class='posted'>
                    {job['posted']}
                    </span>

                </div>
                """

        if len(primary_jobs) == 0 and len(related_jobs) == 0:

            html = "<p>No matching jobs found.</p>"

        save_chat(message, html)

        return jsonify({"reply": html})


    



    # =====================================================
    # OTHER QUESTIONS
    # =====================================================

    reply = "I answer only job portal related questions 😊"

    save_chat(message, reply)
    return jsonify({"reply": reply})


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)
# app.run(debug=False)