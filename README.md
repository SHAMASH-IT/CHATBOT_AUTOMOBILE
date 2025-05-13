# Chatbot Project

## Description

This chatbot was developed using two primary techniques:

1.  **Predefined Automatic Questions:** This approach uses suggestions to guide the conversation with a predefined structure of questions and responses.
2.  **Semantic Search with FAISS:** This more advanced technique employs semantic search and a FAISS index.  It utilizes sentence transformers to generate embeddings, allowing the model to retrieve the closest matching responses based on the user's question.

The application has been developed and primarily tested, but further tuning is needed to achieve full functionality.

**Important Notes:**

* The frontend of the bot requires you to send the car model and type with your API request to the backend.  For the bot to provide a relevant response, the provided car model and type *must* exist within the `cars.csv` data.
* Currently, the `car_type` and `car_model` are hardcoded in the frontend code (specifically in the `fetch` calls) as 'Toyota' and 'Camry' respectively.  You will need to modify the frontend code to allow users to input these values dynamically.  The relevant code snippets are shown below:

```javascript
  try {
        const response = await fetch('http://localhost:5000/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            question: userText, 
            car_type: 'Toyota', //  <---  Modify this line
            car_model: 'Camry'  //  <---  And this line
          }),
        });

This occurs in two places in the original code (lines 221-230 and 331-340).

RAM Requirement: This project may require a machine with at least 16GB of RAM for optimal performance, especially when dealing with large datasets and the FAISS indexing process.

Setup Instructions
Create a Virtual Environment:

python -m venv venv

Activate the Virtual Environment and Install Libraries:

On Windows:

venv\Scripts\activate
pip install -r requirements.txt # if you have a requirements.txt

On macOS and Linux:

source venv/bin/activate
pip install -r requirements.txt # if you have a requirements.txt

(You might need to create a requirements.txt file with the needed libraries, e.g., Flask, sentence-transformers, etc.)

Create an Environment File:

Create a file named .env in the project's root directory.

Add your secret key to the .env file:

SECRET_KEY="your_secret_key_here"  # Replace "your_secret_key_here" with your actual secret key.

Add Model and Data Folders:

Create two folders in the project's root directory: model and data.

Place the following files in the respective folders:

data/cars.csv

model/car_index.faiss

model/cars_with_text.csv
(The car_index.faiss and cars_with_text.csv files may be provided via a Google Drive link, as mentioned in the original description.)

Running the Application
Navigate to the Project Directory:

Open a command prompt or terminal.

Use the cd command to navigate to the project's root directory.

Activate the Virtual Environment:

Follow the instructions in step 2 above to activate the virtual environment.

Run the Flask Application:

python app.py
