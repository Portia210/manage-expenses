from flask import Flask, render_template, request, jsonify
import json
import csv

EXPENSE_CATEGORIES = [
    "Shopping", "Groceries", "Utilities", "Transportation", "Travel",
    "Dining Out", "Online Services", "Healthcare", "Education", "Entertainment",
    "Home Maintenance", "Personal Care", "Gifts & Donations", "Insurance",
    "Taxes", "Debt Payments", "Savings & Investments", "Business Expenses",
    "Pet Care", "Other"
]

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', categories=EXPENSE_CATEGORIES)

@app.route('/categorize', methods=['GET', 'POST'])
def categorize():
    if request.method == 'GET':
        with open('../transaction_kind.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Only return items where "confirm" is False
        return jsonify({k: v for k, v in data.items() if not v.get('confirm', False)})
    elif request.method == 'POST':
        data = request.get_json()
        for key, value in data.items():
            if value['confirm']:
                data[key]['confidence'] = '100%'
        with open('../transaction_kind.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return jsonify({'status': 'success'})

@app.route('/get_details', methods=['POST'])
def get_details():
    business_name = request.get_json().get('business_name')
    details = []
    with open('../cal_cleaned.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['שם בית עסק'] == business_name:
                details.append(row)
    return jsonify(details)

if __name__ == '__main__':
    app.run(debug=True)