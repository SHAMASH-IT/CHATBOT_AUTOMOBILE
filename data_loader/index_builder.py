# index_builder.py
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

df = pd.read_csv("data/cars.csv", low_memory=False)
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

def base_brand(car_type):
    return ''.join([c for c in car_type if not c.isdigit()])

def row_to_text(row):
    brand = base_brand(row['CarType']).upper()
    return (
        f"La voiture de marque {brand} ({row['CarType']}) modèle {row['CarModel']} coûte {row['Price']}. "
        f"Elle a parcouru {row['Kilometrage']}. "
        f"Année de fabrication : {row['Year']}. "
        f"Nombre de plaintes : {row['Plaintes']}. "
        f"Problèmes signalés : {row['Problem']}."
    )

df['CarType'] = df['CarType'].str.strip()

try:
    df['text'] = df.apply(row_to_text, axis=1)
    embeddings = model.encode(df['text'].tolist(), show_progress_bar=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))

    faiss.write_index(index, 'model/car_index.faiss')
    df.to_csv("model/cars_with_text.csv", index=False)

except Exception as e:
    print(e)
