# main.py
from flask import Flask, render_template, request
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# main.py
from config import APP_ID, API_KEY, SHEET_ENDPOINT, TOKEN


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    exercise_text = request.form['exercise_text']
    result = process_exercise(exercise_text)
    return render_template('result.html', result=result)

def process_exercise(exercise_text):
    GENDER = "male"
    WEIGHT_KG = 63
    HEIGHT_CM = 170
    AGE = 21

    APP_ID = os.environ.get('APP_ID')
    API_KEY = os.environ.get('API_KEY')
    SHEET_ENDPOINT = os.environ.get('SHEET_ENDPOINT')
    TOKEN = os.environ.get('TOKEN')

    exercise_endpoint = "https://trackapi.nutritionix.com/v2/natural/exercise"

    headers = {
        "x-app-id": APP_ID,
        "x-app-key": API_KEY,
    }

    parameters = {
        "query": exercise_text,
        "gender": GENDER,
        "weight_kg": WEIGHT_KG,
        "height_cm": HEIGHT_CM,
        "age": AGE
    }

    response = requests.post(exercise_endpoint, json=parameters, headers=headers)
    result = response.json()

    ####################### Connecting to sheety #################################

    bearer_headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    today_date = datetime.now().strftime("%d/%m/%Y")
    now_time = datetime.now().strftime("%X")

    for exercise in result["exercises"]:
        sheet_input = {
            "workout": {
                "date": today_date,
                "time": now_time,
                "exercise": exercise["name"].title(),
                "duration": exercise["duration_min"],
                "calories": exercise["nf_calories"]
            }
        }

        sheet_response = requests.post(
            SHEET_ENDPOINT,
            json=sheet_input,
            headers=bearer_headers
        )

        print(sheet_response.json())

    return result

if __name__ == '__main__':
    app.run(debug=True)
