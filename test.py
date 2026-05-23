from recommendation import recommendation

# Quick test prompt
recs = recommendation("I want a technical club where I can write software code, build mobile apps, work on Python or JavaScript projects, and participate in hackathons", top=10, debug=True)
for r in recs:
    print(f"{r['score']:.4f}  {r['name']}")