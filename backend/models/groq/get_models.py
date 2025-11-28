import logging
import requests
import os
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_groq_models():
    """Fetch and print the list of available GROQ models in a list format"""

    try:
        logging.info("Fetching GROQ models...")
        api_key = os.environ["GROQ_API_KEY"]
        url = "https://api.groq.com/openai/v1/models"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        # Disable SSL verification for corporate network
        response = requests.get(url, headers=headers, verify=False)
        list_models = response.json()['data']
        list_model_ids = [dct['id'] for dct in list_models]

    except KeyError:
        logging.error("GROQ_API_KEY not found in environment variables.")
        list_model_ids = []

    except Exception as e:
        logging.error(f"Error fetching GROQ models: {e}")
        list_model_ids = []

    return list_model_ids
