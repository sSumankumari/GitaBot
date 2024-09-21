import os
import pandas as pd
from dotenv import load_dotenv
import openai
import re

# Load environment variables
load_dotenv()

# Load dataset
data = pd.read_csv('Bhagwad_Gita.csv')

# Initialize OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define prompt templates
prompt_template_with_id = """
Using the wisdom of the Bhagavad Gita, respond to the following query as if Lord Krishna himself is addressing the person:
Query: {query}
Response:
Please start your response with the ID of the most relevant shloka in the exact format BGX.Y, followed by your response.
For example, "BG2.47: You have the right to perform your prescribed duties, but you are not entitled to the fruits of your actions."
Only provide one shloka ID and a concise response.
"""

prompt_template_general = """
Imagine Lord Krishna personally addressing you, imparting his timeless wisdom from the Bhagavad Gita to help address your concern:

Query: "{query}"

My dear child, I understand your concern about "{query}". The Bhagavad Gita teaches us valuable lessons that can guide us in such situations. Remember, think of me as your guide, offering wisdom to illuminate your way forward.

May you find clarity and peace as you reflect on these teachings and navigate your journey.
"""

def generate_openai_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if you have access
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

def generate_response(query, use_dataset=True):
    # Generate general response
    general_response = generate_openai_response(prompt_template_general.format(query=query))

    if use_dataset:
        # Generate response with Shloka ID
        dataset_response = generate_openai_response(prompt_template_with_id.format(query=query))

        # Extract the first valid ID from response using regular expression
        id_pattern = r'BG\d+\.\d+'
        matches = re.findall(id_pattern, dataset_response)
        if matches:
            id_mentioned = matches[0]
            # Ensure ID exists in the dataset
            if id_mentioned in data['ID'].values:
                # Retrieve corresponding Shloka, HinMeaning, and EngMeaning
                selected_row = data[data['ID'] == id_mentioned].iloc[0]
                shloka = selected_row['Shloka']
                hin_meaning = selected_row['HinMeaning']
                eng_meaning = selected_row['EngMeaning']
                chapter = id_mentioned.split('.')[0][2:]  # Extract chapter
                verse = id_mentioned.split('.')[1]  # Extract verse

                result = {
                    "general_response": general_response.replace("**", ""),  # Remove stars
                    "dataset_response": f"Chapter: {chapter} and Shloka: {verse}",
                    "id": id_mentioned,
                    "shloka": shloka,
                    "hin_meaning": hin_meaning,
                    "eng_meaning": eng_meaning
                }

                return result
            else:
                return {
                    "general_response": general_response.replace("**", ""),
                    "dataset_response": "",
                    "id": "",
                    "shloka": "",
                    "hin_meaning": "",
                    "eng_meaning": ""
                }
        else:
            return {
                "general_response": general_response.replace("**", ""),
                "dataset_response": "",
                "id": "",
                "shloka": "",
                "hin_meaning": "",
                "eng_meaning": ""
            }
    else:
        return {
            "general_response": general_response.replace("**", ""),
            "dataset_response": "",
            "id": "",
            "shloka": "",
            "hin_meaning": "",
            "eng_meaning": ""
        }

if __name__ == "__main__":
    query = "How can I find inner peace?"
    result = generate_response(query)
    print(result)
