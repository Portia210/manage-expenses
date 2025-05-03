import requests
import json
import configparser

# Read configuration from INI file
config = configparser.ConfigParser()
config.read('config_gemini.ini')

PROJECT_ID = config['DEFAULT']['ProjectId']  # Your GCP Project ID
REGION = config['DEFAULT']['Region']  # Region where your Vertex AI endpoint is deployed
ENDPOINT_NAME = config['DEFAULT']['EndpointName']  # Name of your deployed Vertex AI Endpoint

EXPENSE_CATEGORIES = [
    "Shopping", "Groceries", "Utilities", "Transportation", "Travel",
    "Dining Out", "Online Services", "Healthcare", "Education", "Entertainment",
    "Home Maintenance", "Personal Care", "Gifts & Donations", "Insurance",
    "Taxes", "Debt Payments", "Savings & Investments", "Business Expenses",
    "Pet Care", "Other"
]

TRANSACTION_KIND_FILE = 'transaction_kind_g.json'


def load_known_transactions():
    try:
        with open(TRANSACTION_KIND_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_known_transactions(known_transactions):
    with open(TRANSACTION_KIND_FILE, 'w', encoding='utf-8') as f:
        json.dump(known_transactions, f, ensure_ascii=False, indent=2)


def categorize_expenses(businesses_names):
    known_transactions = load_known_transactions()
    new_categorizations = {}
    batch_size = 20

    for i in range(0, len(businesses_names), batch_size):
        print("start new loop")
        batch = businesses_names[i:i + batch_size]
        uncategorized = [b for b in batch if b not in known_transactions]

        if uncategorized:
            batch_results = get_category_from_ai(uncategorized)
            new_categorizations.update(batch_results)
            known_transactions.update(batch_results)
            save_known_transactions(known_transactions)

        # Add known transactions for this batch
        new_categorizations.update({b: known_transactions[b] for b in batch if b in known_transactions})

    return new_categorizations


def get_category_from_ai(businesses):
    url = f"https://vertexai.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/endpoints/{ENDPOINT_NAME}"
    headers = {
        "Authorization": f"Bearer {get_access_token()}",  # Replace with function to get access token
        "Content-Type": "application/json",
    }

    prompt = f"""
    Categorize the following businesses into these categories: {', '.join(EXPENSE_CATEGORIES)}

    Businesses: {', '.join(businesses)}

    For each business, provide:
    1. The most fitting category
    2. A confidence level (0-100%)
    3. A brief explanation for your choice

    If a business type is unclear, indicate a lower confidence and explain why.
    """

    data = json.dumps({"inputs": [prompt]})

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        predictions = response.json()["predictions"]
        return parse_predictions(predictions, businesses)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return {}


def parse_predictions(predictions, businesses):
    results = {}
    for i, prediction in enumerate(predictions):
        business_name = businesses[i]
        category = prediction["display_name"]
        confidence = prediction["scores"][0] * 100  # Convert to percentage
        explanation = prediction["metadata"].get("explanation", "")
        results[business_name] = {
            "category": category,
            "confidence": confidence,
            "explanation": explanation
        }
    return results


# Function to get access token (implementation omitted for brevity)
def get_access_token():
    # Replace with your implementation to get an access token for Vertex AI
    pass


# Example usage (can be commented out when using as a module)
if __name__ == "__main__":
    all_businesses = [
        "SUPER-PHARM",
        "GETT",
        "NETFLIX",
        "AMAZON",
        "LOCAL RESTAURANT"
    ]

    categorizations = categorize_expenses(all_businesses)
    for business, details in categorizations.items():
        print(f"\n{business}:")
        print(f"Category: {details['category']}")
        print(f"Confidence: {details['confidence']}")
        print(f"Explanation: {details['explanation']}")