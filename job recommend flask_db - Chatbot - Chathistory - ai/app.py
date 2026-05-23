from flask import Flask, render_template, request, jsonify, redirect, url_for, session

import sqlite3
from datetime import datetime, timedelta
import os

import re


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
app = Flask(__name__)
app.secret_key = "jobportal"


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

    # ⭐ NEW: CHAT HISTORY TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            bot_reply TEXT,
            created_at TEXT
        )
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
        "advanced"
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
if os.path.exists("jobs.db"):
    os.remove("jobs.db")

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
    "java developer": {"java", "spring", "hibernate", "sql"},
    "python developer": {"python", "django", "flask"},
    "data analyst": {"excel", "sql", "power bi"},
    "data scientist": {"python", "machine learning", "pandas"},
    "data engineer": {"python", "sql", "spark", "aws"},
    "ml engineer": {"python", "machine learning", "tensorflow"},
}


# =====================================================
# JOB PORTAL FUNCTION (UNCHANGED)
# =====================================================


def job_portal(user_role, user_skills, user_exp, user_location):
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
        user_level = get_level(user_exp)

        if job_exp is not None and abs(job_exp - user_exp) > 2:
            continue

        if user_location and job_loc != user_location:
            continue

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

        if role.lower() == user_role.lower():
            primary_jobs.append(job_data)
        else:
            related_jobs.append(job_data)

    return primary_jobs, related_jobs


# =====================================================
# HOME
# =====================================================


@app.route("/", methods=["GET", "POST"])
def home():

    primary_jobs = []
    related_jobs = []

    if request.method == "POST":

        role = request.form["role"]
        skills = request.form["skills"].split(",")

        experience = int(request.form["experience"])
        location = request.form["location"]

        primary_jobs, related_jobs = job_portal(role, skills, experience, location)

    return render_template(
        "index.html", primary_jobs=primary_jobs, related_jobs=related_jobs
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
    # NLP JOB SEARCH
    # =====================================================

    if (
        "job" in message
        or "jobs" in message
        or "experience" in message
        or "fresher" in message
        or "entry" in message
        or "intermediate" in message
        or "advanced" in message
    ):

        exp, location = extract_exp_location(message)

        role = extract_role(message)

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
                exp = 2

        if location is None:
            location = "chennai"

        if role is None:
            role = "data scientist"

        role_skills = {
            "data scientist": ["python", "ml"],
            "data engineer": ["python", "sql"],
            "data analyst": ["sql", "excel"],
            "python developer": ["python", "flask"],
            "java developer": ["java", "spring"],
            "ml engineer": ["python", "tensorflow"],
        }

        skills = role_skills.get(role, ["python"])

        primary_jobs, related_jobs = job_portal(role, skills, exp, location)

        html = "<h3>Recommended Jobs</h3>"

        jobs = primary_jobs + related_jobs

        if len(jobs) == 0:

            html += "<p>No matching jobs found.</p>"

        else:

            for job in jobs[:5]:

                html += f"""
                <div class='chat-job-card'>
                    <h4>{job['company']}</h4>

                    <p><b>Role:</b> {job['role']}</p>

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

        save_chat(message, html)

        return jsonify({"reply": html})

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

            if exp is None:
                exp = 2  # default fallback

            if location is None:
                location = "chennai"  # default fallback
            primary_jobs, related_jobs = job_portal(role, skills, exp, location)
            html = ""

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
                posted_date,
                experience,
                location,
                level
            FROM jobs
            ORDER BY posted_date DESC
        """)

        jobs = cursor.fetchall()
        conn.close()

        html = "<h3>Latest Jobs</h3>"

        for job in jobs:

            posted_date = datetime.strptime(job[3], "%Y-%m-%d")
            six_months_ago = datetime.now() - timedelta(days=180)

            if posted_date < six_months_ago:
                continue

            role = job[1]
            skills_set = set(job[2].split(","))
            reference_skills = role_skill_reference.get(role, set())

            if len(skills_set) == 0:
                continue

            common_role = skills_set.intersection(reference_skills)

            if len(common_role) == 0:
                continue

            score = (len(common_role) / len(skills_set)) * 100

            html += f"""
            <div class='chat-job-card'>
                <h4>{job[0]}</h4>
                <p><b>Role:</b> {job[1]}</p>
                <p><b>Skills:</b> {job[2]}</p>
                <p><b>Match:</b> {score:.2f}%</p>
                <p><b>Date:</b> {job[3]}</p>
                <p><b>Experience:</b> {job[4]} years</p>
                <p><b>Location:</b> {job[5]}</p>
                <p><b>Level:</b> {job[6]}</p>
                <span class='posted'>{time_ago(job[3])}</span>
            </div>
            """

        save_chat(message, html)
        return jsonify({"reply": html})

    # =====================================================
    # SKILLS
    # =====================================================

    if "skills" in message:

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

    if "career" in message:

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
    # RECOMMEND
    # =====================================================

    if "recommend" in message:

        reply = """
        <div class='chat-job-card'>
        Tell me your role and skills 😊<br><br>
        Example:<br><br>
        role - Data Scientist, skill - python
        </div>
        """

        save_chat(message, reply)
        return jsonify({"reply": reply})

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
