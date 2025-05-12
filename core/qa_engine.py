# qa_engine.py
import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import re

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
df = pd.read_csv("model/cars_with_text.csv")
index = faiss.read_index("model/car_index.faiss")

def clean_car_type(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r'[^a-z]', '', text.strip().lower())

def clean_string(text):
    return text.strip().lower().replace(" ", "")

def search_car_info(car_type, car_model, suggestion_id):
    cleaned_car_type = clean_car_type(car_type)
    cleaned_car_model = clean_string(car_model)

    df_copy = df.copy()
    df_copy['CarType_cleaned'] = df_copy['CarType'].apply(clean_car_type)
    df_copy['CarModel_cleaned'] = df_copy['CarModel'].apply(clean_string)

    filtered_results = df_copy[
        (df_copy['CarType_cleaned'] == cleaned_car_type) & 
        (df_copy['CarModel_cleaned'] == cleaned_car_model)
    ]
    
    if suggestion_id == "known_issues_user_car":
        problems = []

        for _, row in filtered_results.iterrows():
            problems.append(row['Problem'])
            if len(problems) == 3:
                break

        if problems:
            suggestions = [{"id": "known_issues_user_car_followup", "text": 'Je veux savoir plus de détails sur les problèmes'},
                           {"id": "known_issues_user_car_closeup", "text": 'Merci pour votre réponse'}]
            problem_list = "\n".join(problems)
            return {
                "message": f"Les 3 premiers problèmes connus pour la voiture {car_type} modèle {car_model} sont :\n{problem_list}, est-ce que vous voulez savoir le prix de réglage de chaque problème ?",
                "details": {
                    "kilometrage": filtered_results['Kilometrage'].tolist(),
                    "price": filtered_results['Price'].tolist()
                },
                "suggestions": suggestions
            }
        else:
            return {
                "message": f"Aucun problème connu trouvé pour la voiture {car_type} modèle {car_model}.",
                "details": {},
                "suggestions": []
            }

    elif suggestion_id == "known_issues_user_car_followup":
        details = []
        for _, row in filtered_results.iterrows():
            details.append({
                "problem": row['Problem'],
                "kilometrage": row['Kilometrage'],
                "price": row['Price']
            })
            if len(details) == 3:
                break

        return {
            "message": f"Voici plus de détails sur les problèmes connus pour la voiture {car_type} modèle {car_model}:",
            "details": details
        }

    else:
        return {
            "message": "Désolé, je n'ai pas compris cette demande.",
            "details": {},
            "suggestions": []
        }


def search_car_info_semantic(suggestion_id, question, car_type, car_model, top_k=5, car_type_session=None, car_model_session=None):

    if top_k is None:
        top_k = 5  
    
    global model, index, df

    query_embedding = model.encode([question])
    D, I = index.search(np.array(query_embedding), top_k)
    results = df.iloc[I[0]]

    question_clean = clean_string(question).lower()
    known_brands = ["bmw", "fiat", "kia", "suzuki", "toyota", "volkswagen", "volvo", "peugeot", "mercedes", "mazda", "renault", "ford", "mitsubishi", "hundai", "honda", "nissan", "subaru"]
    brand_in_question = next((b for b in known_brands if b in question_clean), None)

    if car_model_session is None:
        car_type_match = None
        for m in df['CarType'].astype(str).unique():
            m_clean = clean_string(str(m))  
            brand_part = re.sub(r'\d+$', '', m_clean)  
            
            if brand_part in question_clean:
                car_type_match = brand_part
                print("Matched generic brand:", car_type_match)
                break
    else :
        car_type_match = car_type_session

    if car_model_session is None:            
        car_model_match = None
        if car_type_match:
            filtered_df = df[df['CarType'].str.lower().str.startswith(car_type_match.lower())]
            
            for m in filtered_df['CarModel'].astype(str).unique():
                if str(m).lower() in question_clean:
                    car_model_match = clean_string(str(m))
                    print("Car model match (filtered)", car_model_match)
                    break
    else :
        car_model_match = car_model_session               

    for _, row in results.iterrows():
        car_type = car_type_match
        car_model = car_model_match

        print(car_type, car_model)

        if car_model is None:
            return f"Merci de specifier le modèle de la marque {car_type} que vous cherchez.", car_type, car_model

        if "prix" in question_clean or "coûte" in question_clean:
            matching_rows = df[
                df['CarType'].str.lower().str.startswith(car_type.lower()) &
                (df['CarModel'].astype(str).str.lower() == car_model.lower())
            ]

            if not matching_rows.empty:
                prices = matching_rows['Price'].str.replace(' ', '').str.replace('$', '').str.replace(' ', '').str.replace(',', '').astype(str)
                prices = prices.str.extract(r'(\d+)')[0].astype(float)

                price_min = int(prices.min())
                price_max = int(prices.max())

                if price_min == price_max:
                    return f"Le prix de la {car_type.upper()} {car_model.upper()} est {price_min} $.", car_type, car_model
                else:
                    return (
                        f"Le prix des voitures {car_type.upper()} {car_model.upper()} varie entre {price_min} $ et {price_max} $. "
                        f"Avez-vous une année précise en tête ?", car_type, car_model
                    )
            else:
                return "Je n'ai trouvé aucune correspondance exacte pour cette combinaison de marque et de modèle."
        if "prix" in question_clean and "année" in question_clean:
            return f"Le prix de la {car_type.upper()} {car_model.upper()} pour le {row['Year']} est {row['Price']}.", car_type, car_model

        if "information" in question_clean or "détail" in question_clean:
            return row['text'], car_type, car_model

        return row['text'], car_type, car_model

    return "Je n'ai pas trouvé de correspondance précise pour cette voiture.", car_type, car_model
