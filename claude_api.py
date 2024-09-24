# In a file named expense_categorizer.py

import requests
import json
import configparser

# Read configuration from INI file
config = configparser.ConfigParser()
config.read('config_claude.ini')

API_URL = "https://api.anthropic.com/v1/messages"
API_KEY = config['DEFAULT']['ApiKey']

EXPENSE_CATEGORIES = [
    "Shopping", "Groceries", "Utilities", "Transportation", "Travel",
    "Dining Out", "Online Services", "Healthcare", "Education", "Entertainment",
    "Home Maintenance", "Personal Care", "Gifts & Donations", "Insurance",
    "Taxes", "Debt Payments", "Savings & Investments", "Business Expenses",
    "Pet Care", "Other"
]

TRANSACTION_KIND_FILE = 'transaction_kind.json'


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
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01"
    }

    prompt = f"""
    Categorize the following businesses into these categories: {', '.join(EXPENSE_CATEGORIES)}

    Businesses: {', '.join(businesses)}

    For each business, provide:
    1. The most fitting category
    2. A confidence level (0-100%)
    3. A brief explanation for your choice

    If a business type is unclear, indicate a lower confidence and explain why.

    Respond in this format for each business:
    Business: [business name]
    Category: [category]
    Confidence: [0-100]%
    Explanation: [brief explanation]

    Separate each business with a blank line.
    """

    data = {
        "model": "claude-3-5-sonnet-20240620",
        "system": "You are an experienced accountant.",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000
    }

    response = requests.post(API_URL, headers=headers, json=data, timeout=10000)

    if response.status_code == 200:
        ai_response = response.json()['content'][0]['text']
        return parse_ai_response(ai_response, businesses)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return {}


def parse_ai_response(ai_response, businesses):
    results = {}
    current_business = None
    current_data = {}

    for line in ai_response.strip().split('\n'):
        line = line.strip()
        if line.startswith('Business:'):
            if current_business:
                results[current_business] = dict(current_data)
            current_business = line.split(':', 1)[1].strip()
            current_data = {}
        elif line.startswith('Category:'):
            current_data['category'] = line.split(':', 1)[1].strip()
        elif line.startswith('Confidence:'):
            current_data['confidence'] = line.split(':', 1)[1].strip()
        elif line.startswith('Explanation:'):
            current_data['explanation'] = line.split(':', 1)[1].strip()

    if current_business:
        results[current_business] = dict(current_data)

    return results


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