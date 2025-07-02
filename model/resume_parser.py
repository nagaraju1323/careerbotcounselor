import spacy
nlp = spacy.load('en_core_web_sm')

# Set of known skills
KNOWN_SKILLS = {
    "python", "java", "c++", "machine learning", "deep learning", "sql",
    "nlp", "flask", "django", "html", "css", "javascript", "react", "data analysis",
    "pandas", "numpy", "tensorflow", "pytorch", "git", "docker", "kubernetes",
    "linux", "excel"
}

def extract_skills(text):
    text = text.lower()
    doc = nlp(text)

    tokens = set(token.text for token in doc if not token.is_stop)
    single_skills = KNOWN_SKILLS.intersection(tokens)

    # Use phrases (noun chunks) for multi-word matches
    phrases = set(chunk.text.strip() for chunk in doc.noun_chunks)
    multi_word_skills = KNOWN_SKILLS.intersection(phrases)

    extracted = single_skills.union(multi_word_skills)
    return list(extracted)
