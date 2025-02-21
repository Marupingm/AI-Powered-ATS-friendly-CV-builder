from flask import Flask, request, render_template, jsonify, send_file, session
import os
from fpdf import FPDF
from extract_text import extract_text
from match_keywords import match_keywords
import groq  # type: ignore

import spacy
nlp = spacy.load("en_core_web_sm")  # This is the small model


app = Flask(__name__)
app.secret_key = "super_secret_key"

# Groq API Configuration
GROQ_API_KEY = "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"
LLAMA_MODEL = "llama3-70b-8192"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

client = groq.Client(api_key=GROQ_API_KEY)

@app.route("/", methods=["GET", "POST"])
def index():
    """Handles resume scanning and displays results."""
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

        try:
            resume_text = extract_text(file_path)
            print("✅ Extracted Resume Text:", resume_text[:500])  # Debugging
        except Exception as e:
            print(f"❌ Error extracting text: {e}")
            return "Failed to extract text from resume", 500

        # Calculate ATS score
        score, matches = match_keywords(resume_text, job_description)
        print("✅ ATS Score:", score)  # Debugging

        # Store values in session
        session["resume_text"] = resume_text
        session["job_description"] = job_description
        session["score"] = score
        session["ai_suggestions"] = None  # Reset AI suggestions

        print("🔹 Session Data After Scan:", session)  # Debugging

    return render_template(
        "index.html",
        score=session.get("score"),
        resume_text=session.get("resume_text"),
        job_description=session.get("job_description"),
        ai_suggestions=session.get("ai_suggestions"),
    )


@app.route("/generate-ai", methods=["POST"])
def generate_ai():
    """Uses AI to analyze or optimize the resume."""
    data = request.get_json()
    field = data.get("field")
    job_description = data.get("job_description")
    resume_text = data.get("resume_text")

    print("🔹 Job Description:", job_description)  # Debugging
    print("🔹 Resume Text:", resume_text)  # Debugging

    if not job_description or not resume_text:
        return jsonify({"error": "Job description or resume text is missing."}), 400

    prompts = {
        "analyze": f"Analyze this resume's compatibility with the following job description:\n\n{resume_text}\n\nJob Description:\n{job_description}",
        "optimize": f"Optimize this resume for the given job description:\n\n{resume_text}\n\nJob Description:\n{job_description}",
    }

    if field not in prompts:
        return jsonify({"error": "Invalid field"}), 400

    try:
        completion = client.chat.completions.create(
            model=LLAMA_MODEL,
            messages=[{"role": "user", "content": prompts[field]}],
            temperature=1,
            max_tokens=1024,
            top_p=1,
        )

        suggestion = completion.choices[0].message.content.strip()
        session["ai_suggestions"] = suggestion  # Store AI output in session

        return jsonify({"suggestion": suggestion})
    except Exception as e:
        print(f"❌ Error generating AI suggestions: {e}")  # Debugging
        return jsonify({"error": "AI service is currently unavailable. Try again later."}), 500


@app.route("/download-optimized-cv", methods=["POST"])
def download_optimized_cv():
    """Converts optimized CV text into a downloadable PDF."""
    data = request.get_json()
    content = data.get("content", "")

    if not content.strip():
        return "No content to generate PDF", 400

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, content)

    pdf_path = os.path.join(UPLOAD_FOLDER, "Optimized_CV.pdf")
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True)


@app.route("/clear-session", methods=["GET"])
def clear_session():
    """Clears all session data and resets the app."""
    session.clear()
    return jsonify({"message": "Session cleared"}), 200

import os

if __name__ == "__main__":
    app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)