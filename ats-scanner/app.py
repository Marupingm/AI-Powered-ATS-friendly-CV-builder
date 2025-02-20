from flask import Flask, request, render_template, jsonify, send_file
import requests
import os
from fpdf import FPDF
from extract_text import extract_text
from match_keywords import match_keywords

app = Flask(__name__)

# Hugging Face API key for Llama 3
HUGGINGFACE_API_KEY = "YOUR_HUGGINGFACE_API_KEY"
LLAMA_MODEL = "meta-llama/Llama-3-8B"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    score, matches, resume_text = None, None, None

    if request.method == "POST":
        if "resume" not in request.files or "job_description" not in request.form:
            return "Missing file or job description", 400

        resume = request.files["resume"]
        job_description = request.form["job_description"].strip()

        if resume.filename == "":
            return "No selected file", 400
        if job_description == "":
            return "Job description cannot be empty", 400

        file_path = os.path.join(UPLOAD_FOLDER, resume.filename)
        resume.save(file_path)

        resume_text = extract_text(file_path)
        score, matched_keywords = match_keywords(resume_text, job_description)

        return render_template("index.html", score=score, matches=matched_keywords, resume_text=resume_text)

    return render_template("index.html", score=score, matches=matches, resume_text=resume_text)

@app.route("/generate-ai", methods=["POST"])
def generate_ai():
    """ Generate AI-based suggestions using Llama 3 """
    data = request.get_json()
    field = data.get("field")

    prompts = {
        "skills": "List the most relevant skills for a software developer CV.",
        "experience": "Improve this work experience section for a software developer CV.",
        "education": "Provide a strong education section for a software developer CV."
    }

    if field not in prompts:
        return jsonify({"error": "Invalid field"}), 400

    try:
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompts[field]
        }

        response = requests.post(
            f"https://api-inference.huggingface.co/models/{LLAMA_MODEL}",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            suggestion = response.json()[0]["generated_text"].strip()
        else:
            suggestion = "AI service is currently unavailable."

        return jsonify({"suggestion": suggestion})

    except Exception as e:
        print("Hugging Face API Error:", str(e))
        return jsonify({"error": "AI service is currently unavailable. Try again later."}), 500

@app.route("/build-cv", methods=["POST"])
def build_cv():
    """ Generate ATS-friendly CVs as PDFs """
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    skills = request.form.get("skills")
    experience = request.form.get("experience")
    education = request.form.get("education")
    template = request.form.get("template", "classic")

    if not all([name, email, phone, skills, experience, education]):
        return "All fields are required!", 400

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"{name}'s CV - {template.title()} Template", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Email: {email}", ln=True)
    pdf.cell(200, 10, f"Phone: {phone}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Skills", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, skills)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Experience", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, experience)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Education", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, education)

    pdf_path = os.path.join(UPLOAD_FOLDER, "generated_cv.pdf")
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
