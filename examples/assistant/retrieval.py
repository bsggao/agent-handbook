"""Deterministic lexical retrieval, not embeddings or a vector database."""
import json
import re
from pathlib import Path


def tokens(text: str) -> set[str]:
    parts = re.findall(r'[a-z0-9]+|[\u3400-\u9fff]+', text.lower())
    result = set()
    for part in parts:
        if re.search(r'[\u3400-\u9fff]', part):
            result.update(part[i:i + 2] for i in range(max(1, len(part) - 1)))
        else:
            result.add(part)
    return result


def search(query: str, limit: int = 3) -> list[dict]:
    docs = json.loads(Path(__file__).with_name('documents.json').read_text(encoding='utf-8'))
    query_tokens = tokens(query)
    ranked = []
    for doc in docs:
        overlap = len(query_tokens & tokens(doc['text'] + doc['title']))
        keywords = sum(word in query for word in doc['keywords'])
        score = overlap + 3 * keywords
        if score:
            ranked.append({**doc, 'score': score})
    ranked.sort(key=lambda d: (-d['score'], d['id']))
    return ranked[:limit]


def select_context(documents: list[dict], budget: int) -> list[dict]:
    """Preserve whole chunks and source IDs. Budget is characters, explicitly not tokens."""
    selected, used = [], 0
    for document in documents:
        size = len(document['text']) + len(document['id']) + 4
        if used + size <= budget:
            selected.append(document)
            used += size
    return selected
