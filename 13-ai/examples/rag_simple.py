"""Мінімальний RAG без залежностей: TF-IDF-пошук по локальному корпусу.

Демонструє retrieval-частину RAG на стандартній бібліотеці: токенізація,
IDF, TF-IDF-вектори й косинусна близькість. Ембедінги та векторні БД —
у `detailed-guide.md` і `resources.md`; цей приклад працює офлайн.

Запуск:

    python rag_simple.py
    python rag_simple.py --query "failsafe battery link" --top-k 2
"""

from __future__ import annotations

import argparse
import math
import re
from collections import Counter

DOCUMENTS = {
    'failsafe': 'Failsafe triggers RTL when the RC link is lost for more than two seconds.',
    'battery': 'Battery failsafe switches to Land when remaining capacity drops below ten percent.',
    'geofence': 'Geofence violation stops the mission and holds the vehicle inside the allowed area.',
    'mavlink': 'MAVLink telemetry streams heartbeat and position messages over the radio link.',
}


def tokenize(text: str) -> list[str]:
    return re.findall(r'[a-z0-9]+', text.lower())


def build_index(documents: dict[str, str]) -> tuple[dict[str, float], list[dict[str, float]]]:
    tokenized = [tokenize(text) for text in documents.values()]
    document_frequency: Counter[str] = Counter()
    for tokens in tokenized:
        document_frequency.update(set(tokens))
    total = len(tokenized)
    idf = {
        term: math.log((1 + total) / (1 + frequency)) + 1
        for term, frequency in document_frequency.items()
    }
    vectors = []
    for tokens in tokenized:
        counts = Counter(tokens)
        length = len(tokens) or 1
        vectors.append({term: (count / length) * idf[term] for term, count in counts.items()})
    return idf, vectors


def cosine(left: dict[str, float], right: dict[str, float]) -> float:
    common = set(left) & set(right)
    dot = sum(left[term] * right[term] for term in common)
    norm_left = math.sqrt(sum(value * value for value in left.values()))
    norm_right = math.sqrt(sum(value * value for value in right.values()))
    if norm_left == 0 or norm_right == 0:
        return 0.0
    return dot / (norm_left * norm_right)


def retrieve(query: str, documents: dict[str, str], top_k: int = 2) -> list[tuple[str, float]]:
    idf, vectors = build_index(documents)
    counts = Counter(tokenize(query))
    length = sum(counts.values()) or 1
    query_vector = {
        term: (count / length) * idf.get(term, 0.0) for term, count in counts.items()
    }
    scored = [
        (name, round(cosine(query_vector, vector), 4))
        for name, vector in zip(documents, vectors)
    ]
    scored = [item for item in scored if item[1] > 0]
    scored.sort(key=lambda item: (-item[1], item[0]))
    return scored[:top_k]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query', default='failsafe battery link')
    parser.add_argument('--top-k', type=int, default=2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(f'query: {args.query}')
    for name, score in retrieve(args.query, DOCUMENTS, args.top_k):
        print(f'{score:.4f}  {name}: {DOCUMENTS[name]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
