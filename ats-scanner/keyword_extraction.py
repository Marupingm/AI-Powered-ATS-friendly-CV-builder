import spacy

nlp = spacy.load("en_core_web_sm")

def extract_keywords(job_description):
    doc = nlp(job_description.lower())
    return set([token.lemma_ for token in doc if token.is_alpha and not token.is_stop])
