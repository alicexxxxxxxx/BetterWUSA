import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def recommendation(user_prompt, top=15, include_name=True, debug=False):
    with open("scraper/club_list.json", "r") as file:
        clubs = json.load(file)

    texts = []
    for club in clubs:
        parts = []
        name = club.get("name", "").strip()
        info = club.get("info", "").strip()

        if "no description" in info:
            info = ""

        if include_name and name:
            parts.append(f"{name} {name}")

        if info:
            parts.append(info)

        texts.append(" - ".join(parts) if parts else "")


    club_info_embeddings = model.encode(texts, show_progress_bar=False)
    user_prompt_embeddings = model.encode([user_prompt])

    similarity_score = cosine_similarity(user_prompt_embeddings, club_info_embeddings)[0]

    scored_clubs = []
    for index, current_score in enumerate(similarity_score):
        scored_clubs.append({
            "name": clubs[index].get("name"),
            "term": clubs[index].get("term"),
            "info": clubs[index].get("info"),
            "link": clubs[index].get("link"),
            "score": float(current_score)
        })

    scored_clubs.sort(key=lambda x: x['score'], reverse=True)

    if debug:
        print(f"Query: {user_prompt}")
        for i, c in enumerate(scored_clubs[:min(10, len(scored_clubs))]):
            print(f"{i+1:02d}. {c['name'][:60]:60}  score={c['score']:.4f}")

    return scored_clubs[:top]


