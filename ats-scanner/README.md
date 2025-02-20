ats-scanner/                     # Root project folder
│── app.py                        # Main Flask app (backend)
│── extract_text.py               # Extract text from resumes (PDF, DOCX)
│── keyword_extraction.py         # Extract keywords from job descriptions
│── match_keywords.py             # Match resume with job description
│── requirements.txt              # List of dependencies for easy installation
│
├── templates/                    # Frontend (HTML files)
│   ├── index.html                # Web interface for file upload & results
│
├── static/                       # Frontend static files
│   ├── style.css                 # CSS styles for web UI
│
├── resume_samples/               # Sample resumes for testing
│   ├── sample_resume.pdf
│   ├── sample_resume.docx
│
└── README.md                     # Documentation on how to use the project


// Run the following command to install the necessary packages:
pip install flask pdfplumber python-docx spacy nltk
python -m spacy download en_core_web_sm
