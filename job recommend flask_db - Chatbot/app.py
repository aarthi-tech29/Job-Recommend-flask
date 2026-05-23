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

from datetime import datetime, timedelta

app = Flask(__name__)

app.secret_key = "jobportal"

# =====================================================
# TIME AGO FUNCTION
# =====================================================

def time_ago(date_string):

    posted_date = datetime.strptime(
        date_string,
        "%Y-%m-%d"
    )

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

            job_type TEXT,

            posted_date TEXT
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
                "default",
                "2026-05-20"
            ),

            (
                "Google",
                "data scientist",
                "python,machine learning,pandas",
                "default",
                "2026-05-10"
            ),

            (
                "Amazon",
                "data engineer",
                "python,sql,spark,aws",
                "default",
                "2026-04-15"
            ),

            (
                "Microsoft",
                "data analyst",
                "excel,sql,power bi",
                "default",
                "2026-03-01"
            ),

            (
                "Meta",
                "ml engineer",
                "python,machine learning,tensorflow",
                "default",
                "2025-12-15"
            ),

            (
                "Infosys",
                "python developer",
                "python,flask,django",
                "default",
                "2025-11-01"
            ),

            (
                "TCS",
                "python developer",
                "python,django,flask",
                "default",
                "2025-05-15"
            ),

            (
                "Wipro",
                "data analyst",
                "excel,sql,power bi",
                "default",
                "2024-05-10"
            ),

            # =========================================
            # NOISY DATA
            # =========================================

            (
                "XYZ Corp",
                "java developer",
                "python,django",
                "default",
                "2026-05-22"
            ),

            (
                "FakeData Inc",
                "data scientist",
                "excel,power bi",
                "default",
                "2026-05-22"
            )
        ]

        cursor.executemany(

            """
            INSERT INTO jobs
            (company, role, skills, job_type, posted_date)

            VALUES (?, ?, ?, ?, ?)
            """,

            default_jobs
        )

        conn.commit()

    conn.close()

# =====================================================
# INITIALIZE DATABASE
# =====================================================

# =====================================================
# INITIALIZE DATABASE (FIXED)
# =====================================================

import os

# ⚠️ delete old broken DB (IMPORTANT FIX)
if os.path.exists("jobs.db"):
    os.remove("jobs.db")

create_database()
insert_default_jobs()

# =====================================================
# ROLE SKILL REFERENCE
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

    user_skills = set([

        s.lower().strip()

        for s in user_skills
    ])

    primary_jobs = []

    related_jobs = []

    conn = sqlite3.connect("jobs.db")

    cursor = conn.cursor()

    cursor.execute(

        """
        SELECT company, role, skills, posted_date
        FROM jobs
        """
    )

    data = cursor.fetchall()

    conn.close()

    for row in data:

        company = row[0]

        role = row[1]

        skills = set(row[2].split(","))

        posted_date = row[3]

        # =========================================
        # REMOVE NOISY DATA
        # =========================================

        reference_skills = role_skill_reference.get(role, set())

        if len(skills) == 0:
            continue

        # 1️⃣ must match role reference
        common_role = skills.intersection(reference_skills)
        if len(common_role) == 0:
            continue

        # 2️⃣ must match user skills
        common_user = skills.intersection(user_skills)
        if len(common_user) == 0:
            continue

        # 3️⃣ final score (better accuracy)
        score = (len(common_user) / len(skills)) * 100

        # =========================================
        # USER MATCH
        # =========================================

        matched = user_skills.intersection(
            skills
        )

        if len(matched) == 0:
            continue

        score = (
            len(matched) / len(skills)
        ) * 100

        # =========================================
        # MATCH LEVEL
        # =========================================

        if score >= 70:

            level = "Strong Match"

        elif score >= 40:

            level = "Moderate Match"

        else:

            level = "Weak Match"

        job_data = {

            "company": company,

            "role": role,

            "matched_skills": list(matched),

            "score": round(score, 2),

            "level": level,

            "posted_date": posted_date,

            "posted": time_ago(posted_date)
        }

        if role == user_role:

            primary_jobs.append(job_data)

        else:

            related_jobs.append(job_data)

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

        primary_jobs, related_jobs = job_portal(
            role,
            skills
        )

    return render_template(

        "index.html",

        primary_jobs=primary_jobs,

        related_jobs=related_jobs
    )

# =====================================================
# POST JOB
# =====================================================

# =====================================================
# POST JOB
# =====================================================

@app.route("/post-job", methods=["GET", "POST"])
def post_job():

    if request.method == "POST":

        company = request.form["company"]

        role = request.form["role"].lower().strip()

        # ✅ FIXED SKILLS PART (ONLY CHANGE)
        skills = request.form["skills"].split(",")

        skills = [
            s.lower().strip()
            for s in skills
        ]

        # ❌ DO NOT modify user input with reference skills
        clean_skills = list(set(skills))

        conn = sqlite3.connect("jobs.db")

        cursor = conn.cursor()

        cursor.execute(

            """
            INSERT INTO jobs
            (company, role, skills, job_type, posted_date)

            VALUES (?, ?, ?, ?, ?)
            """,

            (
                company,
                role,
                ",".join(clean_skills),
                "posted",
                datetime.now().strftime("%Y-%m-%d")
            )
        )

        conn.commit()

        conn.close()

        session["message"] = "Job Posted Successfully!"

        session["latest_job"] = {

            "company": company,

            "role": role,

            "skills": ", ".join(clean_skills),

            "posted_date":
            datetime.now().strftime("%Y-%m-%d"),

            "posted":
            "Today"
        }

        return redirect(
            url_for("post_job")
        )

    latest_job = session.pop(
        "latest_job",
        None
    )

    message = session.pop(
        "message",
        None
    )

    return render_template(

        "post_job.html",

        latest_job=latest_job,

        message=message
    )
# =====================================================
# CHATBOT
# =====================================================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    message = data.get(
        "message",
        ""
    ).lower().strip()

    # =====================================================
    # GREETING
    # =====================================================

    if message in ["hi", "hello", "hey"]:

        return jsonify({

            "reply":
            """
            Hello 👋<br><br>

            Ask me about:<br><br>

            • Latest jobs<br>
            • Skills<br>
            • Careers<br>
            • Hiring<br>
            • Recommendations
            """
        })

    # =====================================================
    # RECOMMENDATION
    # =====================================================

    if "role" in message and "skill" in message:

        try:

            role_part = message.split(
                "role -"
            )[1]

            role = role_part.split(",")[0].strip()

            skills_part = message.split(
                "skill -"
            )[1]

            skills = [

                s.strip().lower()

                for s in skills_part.split(",")
            ]

            primary_jobs, related_jobs = job_portal(
                role,
                skills
            )

            html = ""

            if primary_jobs:

                html += "<h3>Primary Jobs</h3>"

                for job in primary_jobs:

                    html += f"""

                    <div class='chat-job-card'>

                        <h4>{job['company']}</h4>

                        <p>
                        <b>Role:</b>
                        {job['role']}
                        </p>

                        <p>
                        <b>Match:</b>
                        {job['score']}%
                        </p>

                        <p>
                        <b>Level:</b>
                        {job['level']}
                        </p>

                        <p>
                        <b>Date:</b>
                        {job['posted_date']}
                        </p>

                        <span class='posted'>
                        {job['posted']}
                        </span>

                    </div>
                    """

            if related_jobs:

                html += "<h3>Related Jobs</h3>"

                for job in related_jobs[:3]:

                    html += f"""

                    <div class='chat-job-card'>

                        <h4>{job['company']}</h4>

                        <p>
                        <b>Role:</b>
                        {job['role']}
                        </p>

                        <p>
                        <b>Match:</b>
                        {job['score']}%
                        </p>

                        <p>
                        <b>Level:</b>
                        {job['level']}
                        </p>

                        <p>
                        <b>Date:</b>
                        {job['posted_date']}
                        </p>

                        <span class='posted'>
                        {job['posted']}
                        </span>

                    </div>
                    """

            return jsonify({

                "reply": html
            })

        except:

            return jsonify({

                "reply":
                """
                Please use format:<br><br>

                role - Data Scientist, skill - python
                """
            })

    # =====================================================
    # LATEST JOBS
    # =====================================================

    if "latest" in message or message == "jobs" or message == "show jobs":

        conn = sqlite3.connect("jobs.db")

        cursor = conn.cursor()

        cursor.execute(

            """
            SELECT company, role, skills, posted_date
            FROM jobs
            ORDER BY posted_date DESC
            """
        )

        jobs = cursor.fetchall()

        conn.close()

        html = "<h3>Latest Jobs</h3>"

        for job in jobs:

            # =========================================
            # SHOW ONLY LAST 6 MONTH JOBS
            # =========================================

            posted_date = datetime.strptime(
                job[3],
                "%Y-%m-%d"
            )

            six_months_ago = datetime.now() - timedelta(days=180)

            if posted_date < six_months_ago:

                continue

            # =========================================
            # REMOVE NOISY DATA
            # =========================================

            # REMOVE NOISY DATA

            role = job[1]
            skills_set = set(job[2].split(","))
            reference_skills = role_skill_reference.get(role, set())

            if len(skills_set) == 0:
                continue

            # 1️⃣ must match role reference
            common_role = skills_set.intersection(reference_skills)
            if len(common_role) == 0:
                continue

            # 2️⃣ final score (optional but safe)
            score = (len(common_role) / len(skills_set)) * 100
            html += f"""

            <div class='chat-job-card'>

                <h4>{job[0]}</h4>

                <p>
                <b>Role:</b>
                {job[1]}
                </p>

                <p>
                <b>Skills:</b>
                {job[2]}
                </p>

                <p>
                <b>Date:</b>
                {job[3]}
                </p>

                <span class='posted'>
                {time_ago(job[3])}
                </span>

            </div>
            """

        return jsonify({

            "reply": html
        })

    # =====================================================
    # SKILLS
    # =====================================================

    elif "skills" in message:

        return jsonify({

            "reply":
            """
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
        })

    # =====================================================
    # CAREERS
    # =====================================================

    elif "career" in message:

        return jsonify({

            "reply":
            """
            <div class='chat-job-card'>

            <h4>Top Careers</h4>

            <p>• Python Developer</p>
            <p>• Data Scientist</p>
            <p>• ML Engineer</p>
            <p>• Data Engineer</p>
            <p>• Data Analyst</p>

            </div>
            """
        })

    # =====================================================
    # HIRING
    # =====================================================

    elif "hiring" in message:

        return jsonify({

            "reply":
            """
            <div class='chat-job-card'>

            <h4>Companies Hiring</h4>

            <p>• Google</p>
            <p>• Amazon</p>
            <p>• Oracle</p>
            <p>• Infosys</p>
            <p>• Microsoft</p>

            </div>
            """
        })

    # =====================================================
    # RECOMMEND
    # =====================================================

    elif "recommend" in message:

        return jsonify({

            "reply":
            """
            <div class='chat-job-card'>

            Tell me your role and skills 😊<br><br>

            Example:<br><br>

            role - Data Scientist, skill - python

            </div>
            """
        })

    # =====================================================
    # OTHER QUESTIONS
    # =====================================================

    return jsonify({

        "reply":
        """
        I answer only job portal related questions 😊
        """
    })

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    app.run(debug=True)