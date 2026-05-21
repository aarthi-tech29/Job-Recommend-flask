from flask import Flask, render_template, request

app = Flask(__name__)

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
# MAIN JOB DATABASE
# =====================================================

jobs = [

    {
        "company": "ABC Corp",
        "role": "java developer",
        "skills": {"java", "spring", "sql"}
    },

    {
        "company": "Google",
        "role": "data scientist",
        "skills": {"python", "machine learning", "pandas"}
    },

    {
        "company": "Amazon",
        "role": "data engineer",
        "skills": {"python", "sql", "spark", "aws"}
    },

    {
        "company": "Microsoft",
        "role": "data analyst",
        "skills": {"excel", "sql", "power bi"}
    },

    {
        "company": "Meta",
        "role": "ml engineer",
        "skills": {"python", "machine learning", "tensorflow"}
    },

    # WRONG DATA

    {
        "company": "XYZ Corp",
        "role": "java developer",
        "skills": {"python", "django"}
    },

    {
        "company": "FakeData Inc",
        "role": "data scientist",
        "skills": {"excel", "power bi"}
    }
]

# =====================================================
# ONLY USER POSTED JOBS
# =====================================================

posted_jobs = []

# =====================================================
# JOB PORTAL FUNCTION
# =====================================================

def job_portal(user_role, user_skills):

    user_role = user_role.lower().strip()

    user_skills = set([s.lower().strip() for s in user_skills])

    primary_jobs = []

    related_jobs = []

    # =====================================================
    # PROCESS JOBS
    # =====================================================

    for job in jobs:

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
        # REMOVE WRONG DATA
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

    message = ""

    if request.method == "POST":

        company = request.form["company"]

        role = request.form["role"].lower().strip()

        skills = request.form["skills"].split(",")

        skills = set([s.lower().strip() for s in skills])

        # =====================================================
        # NEW JOB
        # =====================================================

        new_job = {

            "company": company,

            "role": role,

            "skills": skills
        }

        # =====================================================
        # STORE JOB
        # =====================================================

        jobs.append(new_job)

        posted_jobs.append(new_job)

        print(posted_jobs)

        message = "Job Posted Successfully!"

    return render_template(

        "post_job.html",

        message=message,

        all_jobs=posted_jobs
    )

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    app.run(debug=True)