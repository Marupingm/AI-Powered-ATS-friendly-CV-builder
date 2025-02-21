from keyword_extraction import extract_keywords

def match_keywords(resume_text, job_description):
    resume_words = extract_keywords(resume_text)
    job_words = extract_keywords(job_description)

    print("🔹 Extracted Resume Keywords:", resume_words)  # Debugging line
    print("🔹 Extracted Job Description Keywords:", job_words)  # Debugging line

    matches = resume_words.intersection(job_words)
    match_score = (len(matches) / len(job_words) * 100) if job_words else 0

    print("✅ Matched Keywords:", matches)  # Debugging line
    print("✅ ATS Score:", match_score)  # Debugging line

    return match_score, matches