import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

'''This is a very genius idea I found. Basically a sentence transformer will take all of the descriptions from each of the club and 
give them traits. For example, if there are three traits 'technical', 'entertainment', and 'artistic' and we have an AI club, it's gonna get 
more technical points and entertainment points then artistic. Each trait is scored from -1.0 to 1.0. But the actual transformer deals with
384 traits. This does the same for the user prompt as well. Once we have these vector scores, we have to calculate how close they are in 
a 384 dimensional space, and it's an algorithm called cosine similarity. Using this algorithm, we can get the most close scores between 
clubs and the prompt and provide recommendations to the user based on the score.'''

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def recommendation(user_prompt, top=15, include_name=True, debug=False):
    with open("scraper/club_list.json", "r") as file:
        clubs = json.load(file)

    texts = []
    for club in clubs:
        parts = []
        name = club.get("name", "").strip()
        info = club.get("info", "").strip()

        #Well only UW theatre club had "no description" in there description but still don't want to pollute the calculation
        if "no description" in info:
            info = ""

        #Sometimes the model too dumb and forgets stuff, so we have to anchor the name of the club twice cuz often times the keyword from club name is better than the description
        if include_name and name:
            parts.append(f"{name} {name}")

        if info:
            parts.append(info)

        texts.append(" - ".join(parts) if parts else "")

    #The embeddings
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
    '''This sorts by score descending'''
    scored_clubs.sort(key=lambda x: x['score'], reverse=True)

    return scored_clubs[:top]


