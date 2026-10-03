# Usernames allowed as authors for problem suggestions.
PROBLEM_SUGGESTION_AUTHOR_NAMES = [
    "QCM du sujet de préselection française - Sciences à l'Ecole",
    "Problème du sujet de préselection française - Sciences à l'Ecole",
    "Problème du sujet officiel des IPhO"
]
PROBLEM_SUGGESTION_AUTHOR_YEARS = list(range(2015, 2027))
PROBLEM_SUGGESTION_AUTHOR_USERNAMES = [
    f"{name} - {year}"
    for name in PROBLEM_SUGGESTION_AUTHOR_NAMES
    for year in PROBLEM_SUGGESTION_AUTHOR_YEARS
]
