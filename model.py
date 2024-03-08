from flask import Flask, request, render_template, redirect, url_for
import urllib.request
import json
import os
import ssl
import matplotlib.pyplot as plt
import pandas as pd
from flask import session


app = Flask(__name__)
users = {
    'user1': {'username': 'user1', 'password': 'password1'},
    'user2': {'username': 'user2', 'password': 'password2'}
}

df = pd.read_csv('heart.csv')


@app.route('/predict', methods=['POST', 'GET'])
def predict():
    age = request.form.get('age')
    sex = request.form.get('sex')
    restingBP = request.form.get('restingBP')
    chestPainType = request.form.get('chestPainType')
    chestPainType = request.form.get('cholesterol')
    fastingBS = request.form.get('fastingBS')
    restingECG = request.form.get('restingECG')
    maxHR = request.form.get('maxHR')
    exerciseAngina = request.form.get('exerciseAngina')
    oldpeak = request.form.get('oldpeak')
    st_Slope = request.form.get('stSlope')

    data = {
        "Inputs": {
            "input1": [
                {
                    "Age": int(age),
                    "Sex": sex,
                    "RestingBP": int(restingBP),
                    "ChestPainType": chestPainType,
                    "Cholesterol": int(chestPainType),
                    "FastingBS": int(fastingBS),
                    "RestingECG": "Normal",
                    "MaxHR": int(maxHR),
                    "ExerciseAngina": exerciseAngina,
                    "Oldpeak": float(oldpeak),
                    "ST_Slope": st_Slope
                }
            ]
        },
        "GlobalParameters": {}
    }

    body = str.encode(json.dumps(data))

    url = 'http://9a5da49f-e77f-4aa9-a123-effc49910fc2.westeurope.azurecontainer.io/score'
    api_key = 'jHrVboewgsKDe6flrI1WKg5MeDh51tH1'
    headers = {'Content-Type': 'application/json',
               'Authorization': ('Bearer ' + api_key)}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        prediction = json.loads(result)
        heart_disease_prediction = prediction['Results']['WebServiceOutput0'][0]['HeartDiseasePrediction']

        if heart_disease_prediction == 1:
            prediction_text = "Unfortunately, there is a high likelihood that you will develop heart failure."
        else:
            prediction_text = "The likelihood of not developing heart failure is high!"

        return render_template('page1.html', prediction=prediction_text)

    except urllib.error.HTTPError as error:
        return f"Error: {error}", 500


@app.route("/plot", methods=['POST', 'GET'])
def graph():
    user_age = request.form.get('age')

    srčane_bolesti = df[df['HeartDisease'] == 1]['Age']

    plt.figure(figsize=(10, 6))
    plt.hist(srčane_bolesti, bins=20, color='#B8B7D8',
             edgecolor='black', alpha=0.7)
    plt.title('Distribution of heart diseases by age')
    plt.xlabel('Age')
    plt.ylabel('Number of people with heart disease')
    plt.grid(True)

    if user_age:
        plt.axvline(x=int(user_age), color='red', linestyle='--', linewidth=2,
                    label="User's age")
        plt.legend()

    graph_file = 'static/graph.png'
    plt.savefig(graph_file)

    return render_template("plot.html", graph=graph_file)


@app.route("/plot2", methods=['POST', 'GET'])
def graph2():
    user_sex = request.form.get('sex')

    srčane_bolesti = df[df['HeartDisease'] == 1]['Sex']

    plt.figure(figsize=(10, 6))
    plt.hist(srčane_bolesti, bins=20, color='#B8B7D8',
             edgecolor='black', alpha=0.7)
    plt.title('Distribution of heart diseases by sex')
    plt.xlabel('Gender')
    plt.ylabel('Number of people with heart disease')
    plt.grid(True)

    if user_sex:
        plt.axvline(x=str(user_sex), color='red', linestyle='--', linewidth=2,
                    label="User's gender")  # Označavanje korisničke dobi na dijagramu
        plt.legend()

    graph2_file = 'static/graph2.png'
    plt.savefig(graph2_file)

    return render_template("plot2.html", graph2=graph2_file)


@app.route("/plot3", methods=['POST', 'GET'])
def graph3():
    user_chol = request.form.get('cholesterol')
    srčane_bolesti = df[df['HeartDisease'] == 1]['Cholesterol']

    plt.figure(figsize=(10, 6))
    plt.hist(srčane_bolesti, bins=20, color='#B8B7D8',
             edgecolor='black', alpha=0.7)
    plt.title('Distribution of heart diseases by sholesterol')
    plt.xlabel('Cholesterol')
    plt.ylabel('Number of people with heart disease')
    plt.grid(True)
    if user_chol:
        plt.axvline(x=int(user_chol), color='red', linestyle='--', linewidth=2,
                    label="User's cholesterol")
        plt.legend()
    graph3_file = 'static/graph3.png'
    plt.savefig(graph3_file)

    return render_template("plot3.html", graph3=graph3_file)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            return redirect(url_for('page1', username=username))
        elif username in users and users[username]['password'] == password:
            session['logged_in'] = True
            session['username'] = username
        else:
            return render_template('login.html', message='Invalid username or password.')
    return render_template('login.html', message='')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return render_template('signup.html', message='Username already exists.')
        else:
            users[username] = {'username': username, 'password': password}
            return redirect(url_for('login'))
    return render_template('signup.html', message='')


@app.route('/page1/<username>')
def page1(username):
    return render_template('page1.html', username=username)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for(''))


def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context


allowSelfSignedHttps(True)


df = pd.read_csv('heart.csv')


if __name__ == '__main__':
    app.run(debug=True)
