from flask import Flask, request, jsonify, session
from core.qa_engine import search_car_info
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "https://servify.shamash-it.com"}})  

app.secret_key = os.getenv("SECRET_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    question = data.get("question", "").strip().lower()
    car_type = data.get("car_type", None)  
    car_model = data.get("car_model", None)

    if car_type:
        session['car_type'] = car_type
    if car_model:
        session['car_model'] = car_model

    #print("Received question:", question)
    #print("Received car type:", car_type)
    #print("Received car model:", car_model)

    car_type = car_type or session.get('car_type')
    car_model = car_model or session.get('car_model')

    if car_type is None or car_model is None:
        print("Car type or model is missing!")
    else:
        print("Car type from session:", car_type)
        print("Car model from session:", car_model)

    response = ""
    suggestions = []
    details = []  

    if "bonjour" in question or "salut" in question or "hi" in question or "hello" in question:
        response = "Bonjour! Comment puis-je vous aider aujourd'hui ?"
        suggestions = [
            {"id": "known_issues_user_car", "text": "Quels sont les problèmes fréquemment rencontrés sur ma voiture ?"},
            {"id": "known_issues_other_car", "text": "Consulter les problèmes courants d’un autre modèle."},
            {"id": "car_description", "text": "Obtenir une fiche descriptive d’un véhicule."}
        ]

    elif "merci" in question or "thank you" in question:
        response = "Merci à vous aussi! Si vous avez d'autres questions, n'hésitez pas à demander."

    elif 'suggestion_id' in data:
        suggestion_id = data['suggestion_id']
        print("Received suggestion_id:", suggestion_id)

        if suggestion_id == "known_issues_user_car" or suggestion_id == "known_issues_user_car_followup":
            result = search_car_info(car_type, car_model, suggestion_id)
            
            response = result['message']
            details = result['details']  
            suggestions = result.get('suggestions', [])  

        elif suggestion_id == "known_issues_other_car_closeup":
            response = "Merci à vous aussi! Si vous avez d'autres questions, n'hésitez pas à demander."

        elif suggestion_id == "known_issues_other_car":
            result = search_car_info(suggestion_id, car_type, car_model)
            response = result['message']
            details = result['details']  

        elif suggestion_id == "car_description":
            result = search_car_info(car_type, car_model)
            response = result['message']
            details = result['details'] 

    else:
        car_type_session = session.get('car_type')
        car_model_session = session.get('car_model')

        response = "Je vais chercher des informations sur votre voiture."

    return jsonify({
        'response': response,
        'suggestions': suggestions,
        'details': details  
    })

if __name__ == "__main__":
    app.run(debug=True)
