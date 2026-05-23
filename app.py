from flask import Flask, render_template, request
from recommendation import *
app = Flask(__name__)
@app.route("/", methods=['GET', 'POST'])
def main():
    try:
        with open("scraper/club_list.json", "r") as file:
            club_data = json.load(file)
    except FileNotFoundError:
        club_data = []

    user_query = None
    result = None

    if request.method=='POST':
        user_query = request.form.get('prompt')
        if user_query and user_query.strip() != "":
            result = recommendation(user_query)

    return render_template('index.html', clubs=club_data, recommendations=result, query=user_query)

app.run(debug=True)
