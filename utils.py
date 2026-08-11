import re
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
        "with",
        "should",
        "can",
        "could",
        "would",
        "my",
        "this",
        "that",
    }

    # Remove punctuation and normalize the query
    cleaned_query = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        query.lower(),
    )

    # Remove common words
    keywords = [
        word
        for word in cleaned_query.split()
        if word not in stop_words and len(word) > 2
    ]

    results = []

    for file in kb_path.glob("*.md"):

        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        searchable_text = (
            file.stem.lower()
            + " "
            + content.lower()
        )

        score = 0

        for word in keywords:

            # Exact keyword match
            if word in searchable_text:
                score += 2

            # Simple plural/singular matching
            if word.endswith("s"):

                singular = word[:-1]

                if singular in searchable_text:
                    score += 1

            else:

                plural = word + "s"

                if plural in searchable_text:
                    score += 1

        # Extra weight for filename matches
        for word in keywords:

            if word in file.stem.lower():
                score += 3

        if score > 0:
            results.append(
                (
                    score,
                    file.name,
                    content,
                )
            )

    results.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return results[:3]