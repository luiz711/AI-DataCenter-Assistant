from pathlib import Path


def load_knowledge_base():
    """
    Reads every Markdown (.md) file inside the knowledge_base folder
    and combines them into one string.
    """

    kb_path = Path("knowledge_base")

    documents = []

    for file in kb_path.glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            documents.append(f.read())

    return "\n\n".join(documents)


def search_knowledge_base(query):
    """
    Searches the knowledge base and returns
    the three most relevant Markdown files.
    """

    kb_path = Path("knowledge_base")

    stop_words = {
        "a",
        "an",
        "and",
        "are",
        "do",
        "for",
        "how",
        "i",
        "in",
        "is",
        "it",
        "of",
        "on",
        "the",
        "to",
        "what",
        "when",
        "where",
        "why",
    }

    keywords = [
        word
        for word in query.lower().split()
        if word not in stop_words
    ]

    results = []

    for file in kb_path.glob("*.md"):

        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        score = 0

        for word in keywords:
            if word in content.lower():
                score += 1

        if score > 0:
            results.append((score, file.name, content))

    results.sort(reverse=True)

    return results[:3]