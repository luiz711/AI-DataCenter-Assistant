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