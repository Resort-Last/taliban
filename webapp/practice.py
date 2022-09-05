from flask import Flask, render_template, request
import pickle
import os
import pandas as pd
from DBHandler import DBHandler

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # getting input with name = fname in HTML form
        first_name = request.form.get("fname")
        # getting input with name = lname in HTML form
        last_name = request.form.get("lname")
        print(first_name, last_name)
        return render_template('home.html', names=[first_name, last_name])
    else:
        return render_template('home.html')


@app.route("/dingdong")
def asd():
    for pkl in os.listdir():
        if pkl[-4:] == '.pkl':
            with open(f'{pkl}', 'rb') as f:
                result = pickle.load(f)
                df = result['bbands,bbands_ichimoku,ichimoku']
    return render_template('dingdong.html', df=df)


if __name__ == "__main__":
    app.run(debug=True)
