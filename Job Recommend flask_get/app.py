# #===============================================================================
# #============================Using thunder client for testing========================================
# #===============================================================================

# from flask import Flask, request, jsonify

# app = Flask(__name__)


# # =====================================================
# # JOB PORTAL FUNCTION
# # =====================================================
# def job_portal(user_role, user_skills):

#     # normalize input
#     user_role = user_role.lower().strip()

#     user_skills = set([s.lower().strip() for s in user_skills])

#     # =====================================================
#     # ROLE-SKILL REFERENCE
#     # =====================================================
#     role_skill_reference = {
#         "java developer": {"java", "spring", "hibernate", "sql"},
#         "python developer": {"python", "django", "flask"},
#         "data analyst": {"excel", "sql", "power bi", "tableau", "data visualization"},
#         "data scientist": {"python", "machine learning", "pandas", "numpy", "statistics"},
#         "data engineer": {"python", "sql", "spark", "hadoop", "etl", "aws"},
#         "ml engineer": {"python", "machine learning", "tensorflow", "pytorch"}
#     }

#     # =====================================================
#     # JOB DATABASE
#     # =====================================================
#     jobs = [

#         {"company": "ABC Corp",
#          "role": "java developer",
#          "skills": {"java", "spring", "sql"}},

#         {"company": "XYZ Corp",
#          "role": "java developer",
#          "skills": {"python", "django"}},   # wrong data

#         {"company": "Google",
#          "role": "data scientist",
#          "skills": {"python", "machine learning", "pandas"}},

#         {"company": "Amazon",
#          "role": "data engineer",
#          "skills": {"python", "sql", "spark", "aws"}},

#         {"company": "Microsoft",
#          "role": "data analyst",
#          "skills": {"excel", "sql", "power bi"}},

#         {"company": "Meta",
#          "role": "ml engineer",
#          "skills": {"python", "machine learning", "tensorflow"}},

#         {"company": "FakeData Inc",
#          "role": "data scientist",
#          "skills": {"excel", "power bi"}}   # wrong data
#     ]

#     primary_jobs = []
#     related_jobs = []

#     # =====================================================
#     # JOB PROCESSING
#     # =====================================================
#     for job in jobs:

#         job_role = job["role"]

#         job_skills = set([s.lower() for s in job["skills"]])

#         # =====================================================
#         # STEP 1 : VALIDATION
#         # =====================================================
#         reference_skills = role_skill_reference.get(job_role, set())

#         if len(job_skills) == 0:
#             continue

#         common = job_skills.intersection(reference_skills)

#         match_ratio = len(common) / len(job_skills)

#         # remove wrong company data
#         if match_ratio < 0.3:
#             continue

#         # =====================================================
#         # STEP 2 : USER MATCH
#         # =====================================================
#         matched = user_skills.intersection(job_skills)

#         if len(matched) == 0:
#             continue

#         score = (len(matched) / len(job_skills)) * 100

#         # =====================================================
#         # MATCH LEVEL
#         # =====================================================
#         if score >= 70:
#             level = "Strong Match"

#         elif score >= 40:
#             level = "Moderate Match"

#         else:
#             level = "Weak Match"

#         job_data = {
#             "company": job["company"],
#             "role": job_role,
#             "matched_skills": list(matched),
#             "matched_count": len(matched),
#             "total_skills": len(job_skills),
#             "match_percentage": round(score, 2),
#             "match_level": level
#         }

#         # =====================================================
#         # ROLE-FIRST LOGIC
#         # =====================================================
#         if job_role == user_role:
#             primary_jobs.append(job_data)

#         else:
#             related_jobs.append(job_data)

#     # =====================================================
#     # SORTING
#     # =====================================================
#     primary_jobs.sort(
#         key=lambda x: x["match_percentage"],
#         reverse=True
#     )

#     related_jobs.sort(
#         key=lambda x: x["match_percentage"],
#         reverse=True
#     )

#     return {
#         "primary_jobs": primary_jobs,
#         "related_jobs": related_jobs
#     }


# # =====================================================
# # HOME ROUTE
# # =====================================================
# @app.route("/")
# def home():
#     return """
#     <h2>AI Job Portal API</h2>
#     <p>Use POST /recommend to get job recommendations</p>
#     """


# # =====================================================
# # API ROUTE
# # =====================================================
# @app.route("/recommend", methods=["POST"])
# def recommend_jobs():

#     data = request.get_json()

#     if not data:
#         return jsonify({
#             "error": "No input data provided"
#         }), 400

#     user_role = data.get("role", "")

#     user_skills = data.get("skills", [])

#     # validation
#     if user_role == "":
#         return jsonify({
#             "error": "Role is required"
#         }), 400

#     if not isinstance(user_skills, list):
#         return jsonify({
#             "error": "Skills must be a list"
#         }), 400

#     # function call
#     result = job_portal(user_role, user_skills)

#     # no jobs
#     if not result["primary_jobs"] and not result["related_jobs"]:
#         return jsonify({
#             "message": "No jobs found"
#         })

#     return jsonify(result)


# # =====================================================
# # MAIN
# # =====================================================
# if __name__ == "__main__":
#     app.run(debug=True)

# #=================================================================================
# #================================== using browser directly===================================
# #=======================================================================================

# from flask import Flask, request, jsonify

# # =====================================================
# # CREATE FLASK APP
# # =====================================================
# app = Flask(__name__)


# # =====================================================
# # JOB PORTAL FUNCTION
# # =====================================================
# def job_portal(user_role, user_skills):

#     # ---------------- NORMALIZE INPUT ----------------
#     user_role = user_role.lower().strip()

#     user_skills = set([s.lower().strip() for s in user_skills])

#     # =====================================================
#     # ROLE - SKILL REFERENCE
#     # =====================================================
#     role_skill_reference = {

#         "java developer":
#             {"java", "spring", "hibernate", "sql"},

#         "python developer":
#             {"python", "django", "flask"},

#         "data analyst":
#             {"excel", "sql", "power bi", "tableau", "data visualization"},

#         "data scientist":
#             {"python", "machine learning", "pandas", "numpy", "statistics"},

#         "data engineer":
#             {"python", "sql", "spark", "hadoop", "etl", "aws"},

#         "ml engineer":
#             {"python", "machine learning", "tensorflow", "pytorch"}
#     }

#     # =====================================================
#     # JOB DATABASE
#     # =====================================================
#     jobs = [

#         {
#             "company": "ABC Corp",
#             "role": "java developer",
#             "skills": {"java", "spring", "sql"}
#         },

#         {
#             "company": "XYZ Corp",
#             "role": "java developer",
#             "skills": {"python", "django"}
#         },  # wrong data

#         {
#             "company": "Google",
#             "role": "data scientist",
#             "skills": {"python", "machine learning", "pandas"}
#         },

#         {
#             "company": "Amazon",
#             "role": "data engineer",
#             "skills": {"python", "sql", "spark", "aws"}
#         },

#         {
#             "company": "Microsoft",
#             "role": "data analyst",
#             "skills": {"excel", "sql", "power bi"}
#         },

#         {
#             "company": "Meta",
#             "role": "ml engineer",
#             "skills": {"python", "machine learning", "tensorflow"}
#         },

#         {
#             "company": "FakeData Inc",
#             "role": "data scientist",
#             "skills": {"excel", "power bi"}
#         }  # wrong data
#     ]

#     # =====================================================
#     # STORE RESULTS
#     # =====================================================
#     primary_jobs = []

#     related_jobs = []

#     # =====================================================
#     # PROCESS JOBS
#     # =====================================================
#     for job in jobs:

#         job_role = job["role"]

#         job_skills = set([s.lower() for s in job["skills"]])

#         # =====================================================
#         # STEP 1 : VALIDATION
#         # =====================================================
#         reference_skills = role_skill_reference.get(job_role, set())

#         if len(job_skills) == 0:
#             continue

#         common = job_skills.intersection(reference_skills)

#         match_ratio = len(common) / len(job_skills)

#         # REMOVE WRONG COMPANY DATA
#         if match_ratio < 0.3:
#             continue

#         # =====================================================
#         # STEP 2 : USER MATCH
#         # =====================================================
#         matched = user_skills.intersection(job_skills)

#         if len(matched) == 0:
#             continue

#         score = (len(matched) / len(job_skills)) * 100

#         # =====================================================
#         # MATCH LEVEL
#         # =====================================================
#         if score >= 70:
#             level = "Strong Match"

#         elif score >= 40:
#             level = "Moderate Match"

#         else:
#             level = "Weak Match"

#         # =====================================================
#         # STORE JOB DATA
#         # =====================================================
#         job_data = {

#             "company": job["company"],

#             "role": job_role,

#             "matched_skills": list(matched),

#             "matched_count": len(matched),

#             "total_skills": len(job_skills),

#             "match_percentage": round(score, 2),

#             "match_level": level
#         }

#         # =====================================================
#         # ROLE-FIRST LOGIC
#         # =====================================================
#         if job_role == user_role:

#             primary_jobs.append(job_data)

#         else:

#             related_jobs.append(job_data)

#     # =====================================================
#     # SORT RESULTS
#     # =====================================================
#     primary_jobs.sort(
#         key=lambda x: x["match_percentage"],
#         reverse=True
#     )

#     related_jobs.sort(
#         key=lambda x: x["match_percentage"],
#         reverse=True
#     )

#     # =====================================================
#     # RETURN RESULT
#     # =====================================================
#     return {

#         "primary_jobs": primary_jobs,

#         "related_jobs": related_jobs
#     }


# # =====================================================
# # HOME ROUTE
# # =====================================================
# @app.route("/")
# def home():

#     return """
#     <h1>AI JOB PORTAL API</h1>

#     <h3>Available Route:</h3>

#     <p>/recommend</p>

#     <h3>Method:</h3>

#     <p>GET or POST</p>
#     """


# # =====================================================
# # RECOMMEND ROUTE
# # =====================================================
# @app.route("/recommend", methods=["GET", "POST"])
# def recommend_jobs():

#     # =====================================================
#     # GET METHOD
#     # =====================================================
#     if request.method == "GET":

#         sample_result = job_portal(

#             "data scientist",

#             ["python", "machine learning", "pandas"]

#         )

#         return jsonify(sample_result)

#     # =====================================================
#     # POST METHOD
#     # =====================================================
#     data = request.get_json()

#     # VALIDATION
#     if not data:

#         return jsonify({
#             "error": "No input data provided"
#         }), 400

#     user_role = data.get("role", "")

#     user_skills = data.get("skills", [])

#     if user_role == "":

#         return jsonify({
#             "error": "Role is required"
#         }), 400

#     if not isinstance(user_skills, list):

#         return jsonify({
#             "error": "Skills must be a list"
#         }), 400

#     # FUNCTION CALL
#     result = job_portal(user_role, user_skills)

#     # NO RESULT
#     if not result["primary_jobs"] and not result["related_jobs"]:

#         return jsonify({
#             "message": "No jobs found"
#         })

#     return jsonify(result)


# # =====================================================
# # MAIN
# # =====================================================
# if __name__ == "__main__":

#     app.run(debug=True)
# #=========================================================================

# ==================================================================
# ==============================html and css ==========================================
# =================================================================
from flask import Flask, render_template, request

app = Flask(__name__)


# =====================================================
# JOB PORTAL FUNCTION
# =====================================================
def job_portal(user_role, user_skills):

    # NORMALIZE INPUT
    user_role = user_role.lower().strip()

    user_skills = set([s.lower().strip() for s in user_skills])

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
    # JOB DATABASE
    # =====================================================
    jobs = [

        # =========================================
        # VALID JOB DATA
        # =========================================

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

        # =========================================
        # WRONG / NOISY DATA
        # =========================================

        {
            "company": "XYZ Corp",
            "role": "java developer",
            "skills": {"python", "django"}
        },   # WRONG DATA

        {
            "company": "FakeData Inc",
            "role": "data scientist",
            "skills": {"excel", "power bi"}
        }   # WRONG DATA
    ]

    # =====================================================
    # STORE RESULTS
    # =====================================================
    primary_jobs = []

    related_jobs = []

    # =====================================================
    # PROCESS JOBS
    # =====================================================
    for job in jobs:

        job_role = job["role"]

        job_skills = set(job["skills"])

        # =====================================================
        # STEP 1 : VALIDATION
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
        # STEP 2 : USER MATCHING
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
        # STORE JOB DATA
        # =====================================================
        job_data = {

            "company": job["company"],

            "role": job_role,

            "matched_skills": list(matched),

            "score": round(score, 2),

            "level": level
        }

        # =====================================================
        # ROLE-FIRST LOGIC
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
# HOME ROUTE
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
# MAIN
# =====================================================
if __name__ == "__main__":

    app.run(debug=True)

# # PERFECT MATCH
# # Role: data scientist
# # Skills: python, machine learning, pandas

# # PARTIAL MATCH
# # Role: data scientist
# # Skills: python, pandas

# # WRONG COMPANY DATA (AUTO REMOVED)
# # Role: java developer
# # Skills: python, django

# # NO PRIMARY MATCH (ONLY RELATED)
# # Role: data scientist
# # Skills: sql

# # JAVA USER (GOOD MATCH)
# # Role: java developer
# # Skills: java, sql

# # WEAK JAVA PROFILE
# # Role: java developer
# # Skills: java

# # MIXED SKILLS (CROSS DOMAIN)
# # Role: java developer
# # Skills: java, python, django

# # NO MATCH AT ALL
# # Role: data scientist
# # Skills: html, css

# # Primary jobs first
# # Related jobs next
# # Skill-based ranking
# # Wrong company data removed
# # Partial matching allowed