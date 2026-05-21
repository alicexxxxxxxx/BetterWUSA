import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def recommendation(user_prompt, top=15):
    with open("scraper/club_list.json", "r") as file:
        clubs = json.load(file)
    info = [club.get("info", "") for club in clubs]
    club_info_embeddings = model.encode(info, show_progress_bar=False)
    user_prompt_embeddings = model.encode([user_prompt])

    score = cosine_similarity(user_prompt_embeddings, club_info_embeddings)[0]

    scored_clubs = []
    for index, score in enumerate(score):
        scored_clubs.append({
            "name": clubs[index].get("name"),
            "info": clubs[index].get("info")
        })

    scored_clubs.sort(key=lambda x: x['score'], reverse=True)
    return scored_clubs[:top]


