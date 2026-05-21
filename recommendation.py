import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def recommendation(user_prompt, top_n=5):
    club_dic = {}
    with open("scraper/club_list.json", "r") as file:
        club_info = json.load(file)
        for i in range(len(club_info)):
            name_data = club_info[i]['name']
            info_data = club_info[i]['info']
            club_dic[name_data] = info_data
    club_info_embeddings = model.encode(list(club_dic.values()))
    user_prompt_embeddings = model.encode([user_prompt])
    cosine_similarity(user_prompt_embeddings, club_info_embeddings)


