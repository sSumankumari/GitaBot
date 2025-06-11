import os
import json
from flask import Flask, render_template, request, jsonify
from helper import generate_response
from sentiment_helper import analyze_sentiment_vader, generate_learning_message
from google.cloud import translate_v2 as translate

app = Flask(__name__)

# Path to Google Cloud credentials
# credentials_file = 'advance-stratum-409704-8f6e8f9201b9.json'  # For contributor 1
credentials_file = 'gitabot-434209-8f7a7daa37c1.json'  # For contributor 2


credentials_path = os.path.join(os.path.dirname(__file__), credentials_file)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

# Initialize Google Cloud Translation client
translate_client = translate.Client()


# Load supported languages from JSON file
def load_supported_languages():
    try:
        with open('languages.json', 'r') as file:
            languages = json.load(file)
        return languages
    except Exception as e:
        print("Error loading languages from JSON file:", e)
        return []


supported_languages = load_supported_languages()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/gitabot')
def gitabot():
    return render_template('gitabot.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/documentation')
def documentation():
    return render_template('documentation.html')


@app.route('/get_languages')
def get_languages():
    try:
        return jsonify(supported_languages)
    except Exception as e:
        print("Error fetching supported languages:", e)
        return jsonify([])


@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    query = data.get('query', '')
    input_language = data.get('input_language', 'en')
    output_language = data.get('output_language', 'en')

    if query:
        try:
            # Translate query to English if it's not already in English
            if input_language != 'en':
                query = translate_client.translate(
                    query,
                    source_language=input_language,
                    target_language='en'
                )['translatedText']

            # Perform sentiment analysis
            sentiment_scores, compound, neg, neu, pos, sentiment_message, short_message = analyze_sentiment_vader(query)
            learning_message = generate_learning_message(sentiment_message)

            # Generate chatbot response
            response_data = generate_response(query)

            if response_data:
                chatbot_response = response_data.get("general_response", "Sorry, I can't answer this query.")

                # Translate response to the desired output language if it's not English
                if output_language != 'en':
                    chatbot_response = translate_client.translate(
                        chatbot_response,
                        source_language='en',
                        target_language=output_language
                    )['translatedText']

                # Translate the final response back to the input language
                if input_language != 'en' and output_language != input_language:
                    chatbot_response = translate_client.translate(
                        chatbot_response,
                        source_language=output_language,
                        target_language=input_language
                    )['translatedText']

                response = {
                    "status": "success",
                    "general_response": chatbot_response,
                    "dataset_response": response_data.get("dataset_response", ""),
                    "id": response_data.get("id", ""),
                    "shloka": response_data.get("shloka", ""),
                    "hin_meaning": response_data.get("hin_meaning", ""),
                    "eng_meaning": response_data.get("eng_meaning", ""),
                    "sentiment": {
                        'compound': compound,
                        'neg': neg,
                        'neu': neu,
                        'pos': pos,
                        'message': sentiment_message,
                        'short_message': short_message,
                        'learning_message': learning_message
                    }
                }
            else:
                response = {
                    "status": "failure",
                    "message": "Sorry, I can't answer this query."
                }
        except Exception as e:
            print(f"Error processing request: {e}")
            response = {
                "status": "error",
                "message": "An error occurred while processing your request."
            }
    else:
        response = {
            "status": "failure",
            "message": "Query cannot be empty."
        }

    return jsonify(response)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
