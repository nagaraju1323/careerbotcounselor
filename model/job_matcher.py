def match_jobs(skills):
    job_map = {
        'python': ['Software Developer', 'AI Engineer'],
        'java': ['Backend Developer'],
        'sql': ['Database Engineer', 'Data Analyst'],
        'machine learning': ['ML Engineer', 'AI Researcher'],
        'deep learning': ['Deep Learning Engineer'],
        'html': ['Frontend Developer'],
        'css': ['Frontend Developer'],
        'javascript': ['Web Developer', 'Full Stack Developer'],
        'react': ['Frontend Developer'],
        'flask': ['Python Web Developer'],
        'django': ['Backend Developer'],
        'pandas': ['Data Analyst'],
        'numpy': ['Data Scientist'],
        'tensorflow': ['ML Engineer'],
        'pytorch': ['Deep Learning Engineer'],
        'git': ['DevOps Engineer'],
        'docker': ['DevOps Engineer'],
        'kubernetes': ['Cloud Engineer'],
        'linux': ['System Administrator'],
        'excel': ['Data Analyst'],
        'nlp': ['NLP Engineer', 'AI Engineer'],
        'c++': ['Software Developer']
    }

    matched_jobs = set()

    for skill in skills:
        skill = skill.lower().strip()  # Normalize skill
        if skill in job_map:
            matched_jobs.update(job_map[skill])

    return list(matched_jobs)
