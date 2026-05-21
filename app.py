from flask import Flask, render_template, request, redirect, session, url_for
from recommendation import *
app = Flask(__name__)

@app.route("/", methods=['GET'])
def main():
    try:
        with open("scraper/club_list.json", "r") as file:
            club_data = json.load(file)
    except FileNotFoundError:
        club_data = []
    return render_template('index.html', clubs=club_data)

app.run(debug=True)
