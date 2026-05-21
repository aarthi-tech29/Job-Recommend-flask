from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session
)

import sqlite3

app = Flask(__name__)

app.secret_key = "jobportal"

# =====================================================
# CREATE DATABASE
# =====================================================

def create_database():

    conn = sqlite3.connect("jobs.db")

    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS jobs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company TEXT,

            role TEXT,

            skills TEXT,

            job_type TEXT
        )

    """)

    conn.commit()

    conn.close()

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

            (
                "ABC Corp",
                "java developer",
                "java,spring,sql",
                "default"
            ),

            (
                "Google",
                "data scientist",
                "python,machine learning,pandas",
                "default"
            ),

            (
                "Amazon",
                "data engineer",
                "python,sql,spark,aws",
                "default"
            ),

            (
                "Microsoft",
                "data analyst",
                "excel,sql,power bi",
                "default"
            ),

            (
                "Meta",
                "ml engineer",
                "python,machine learning,tensorflow",
                "default"
            ),

            # =========================================
            # NOISY DATA
            # =========================================

            (
                "XYZ Corp",
                "java developer",
                "python,django",
                "default"
            ),

            (
                "FakeData Inc",
                "data scientist",
                "excel,power bi",
                "default"
            )
        ]

        cursor.executemany(

            """
            INSERT INTO jobs
            (company, role, skills, job_type)

            VALUES (?, ?, ?, ?)
            """,

            default_jobs
        )

        conn.commit()

    conn.close()

# =====================================================
# INITIALIZE DATABASE
# =====================================================

create_database()

insert_default_jobs()

# =====================================================
# ROLE - SKILL REFERENCE
# =====================================================

role_skill_reference = {

    "java developer":
        {"java", "spring", "hibernate", "sql"},

    "python developer":
        {"python", "django", "flask"},

    "data analyst":
        {"excel", "sql", "power bi", "tableau"},

    "data scientist":
        {"python", "machine learning", "pandas", "numpy"},

    "data engineer":
        {"python", "sql", "spark", "aws"},

    "ml engineer":
        {"python", "machine learning", "tensorflow"}
}

# =====================================================
# JOB RECOMMENDATION FUNCTION
# =====================================================

def job_portal(user_role, user_skills):

    user_role = user_role.lower().strip()

    user_skills = set([s.lower().strip() for s in user_skills])

    primary_jobs = []

    related_jobs = []

    conn = sqlite3.connect("jobs.db")

    cursor = conn.cursor()

    cursor.execute(

        "SELECT company, role, skills FROM jobs"
    )

    data = cursor.fetchall()

    conn.close()

    all_jobs = []

    for row in data:

        all_jobs.append({

            "company": row[0],

            "role": row[1],

            "skills": set(row[2].split(","))
        })

    # =====================================================
    # PROCESS JOBS
    # =====================================================

    for job in all_jobs:

        job_role = job["role"]

        job_skills = set(job["skills"])

        # =====================================================
        # VALIDATION
        # =====================================================

        reference_skills = role_skill_reference.get(job_role, set())

        common = job_skills.intersection(reference_skills)

        if len(job_skills) == 0:
            continue

        match_ratio = len(common) / len(job_skills)

        # =====================================================
        # REMOVE NOISY DATA
        # =====================================================

        if match_ratio < 0.3:

            print("Wrong data removed ->", job["company"])

            continue

        # =====================================================
        # USER MATCHING
        # =====================================================

        matched = user_skills.intersection(job_skills)

        if len(matched) == 0:
            continue

        score = (len(matched) / len(job_skills)) * 100

        # =====================================================
        # MATCH LEVEL
        # =====================================================

        if score >= 70:

            level = "Strong Match"

        elif score >= 40:

            level = "Moderate Match"

        else:

            level = "Weak Match"

        # =====================================================
        # STORE RESULT
        # =====================================================

        job_data = {

            "company": job["company"],

            "role": job_role,

            "matched_skills": list(matched),

            "score": round(score, 2),

            "level": level
        }

        # =====================================================
        # PRIMARY / RELATED
        # =====================================================

        if job_role == user_role:

            primary_jobs.append(job_data)

        else:

            related_jobs.append(job_data)

    # =====================================================
    # SORT RESULTS
    # =====================================================

    primary_jobs.sort(

        key=lambda x: x["score"],

        reverse=True
    )

    related_jobs.sort(

        key=lambda x: x["score"],

        reverse=True
    )

    return primary_jobs, related_jobs

# =====================================================
# HOME PAGE
# =====================================================

@app.route("/", methods=["GET", "POST"])
def home():

    primary_jobs = []

    related_jobs = []

    if request.method == "POST":

        role = request.form["role"]

        skills = request.form["skills"].split(",")

        primary_jobs, related_jobs = job_portal(role, skills)

    return render_template(

        "index.html",

        primary_jobs=primary_jobs,

        related_jobs=related_jobs
    )

# =====================================================
# POST JOB PAGE
# =====================================================

@app.route("/post-job", methods=["GET", "POST"])
def post_job():

    # =====================================================
    # SAVE JOB
    # =====================================================

    if request.method == "POST":

        company = request.form["company"]

        role = request.form["role"].lower().strip()

        skills = request.form["skills"].split(",")

        skills = [s.lower().strip() for s in skills]

        conn = sqlite3.connect("jobs.db")

        cursor = conn.cursor()

        cursor.execute(

            """
            INSERT INTO jobs
            (company, role, skills, job_type)

            VALUES (?, ?, ?, ?)
            """,

            (
                company,
                role,
                ",".join(skills),
                "posted"
            )
        )

        conn.commit()

        conn.close()

        # STORE TEMP DATA
        session["latest_job"] = {

            "company": company,

            "role": role,

            "skills": skills
        }

        session["message"] = "Job Posted Successfully!"

        # REDIRECT
        return redirect(url_for("post_job"))

    # =====================================================
    # SHOW ONLY ONCE
    # =====================================================

    latest_job = session.pop("latest_job", None)

    message = session.pop("message", None)

    return render_template(

        "post_job.html",

        latest_job=latest_job,

        message=message
    )

    # =====================================================
    # GET LATEST JOB
    # =====================================================

    if "latest_job" in session:

        latest_job = session["latest_job"]

    message = session.pop("message", None)

    return render_template(

        "post_job.html",

        latest_job=latest_job,

        message=message
    )

# =====================================================
# API - GET ALL JOBS
# =====================================================

@app.route("/api/jobs", methods=["GET"])
def get_jobs():

    conn = sqlite3.connect("jobs.db")

    cursor = conn.cursor()

    cursor.execute(

        """
        SELECT company, role, skills, job_type
        FROM jobs
        """
    )

    data = cursor.fetchall()

    conn.close()

    jobs = []

    for row in data:

        jobs.append({

            "company": row[0],

            "role": row[1],

            "skills": row[2].split(","),

            "job_type": row[3]
        })

    return jsonify({

        "all_jobs": jobs
    })

# =====================================================
# API - POST NEW JOB
# =====================================================

@app.route("/api/post-job", methods=["POST"])
def api_post_job():

    data = request.json

    company = data["company"]

    role = data["role"].lower().strip()

    skills = data["skills"]

    skills = [s.lower().strip() for s in skills]

    conn = sqlite3.connect("jobs.db")

    cursor = conn.cursor()

    cursor.execute(

        """
        INSERT INTO jobs
        (company, role, skills, job_type)

        VALUES (?, ?, ?, ?)
        """,

        (
            company,
            role,
            ",".join(skills),
            "posted"
        )
    )

    conn.commit()

    conn.close()

    return jsonify({

        "message": "Job Posted Successfully"
    })

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    app.run(debug=True)