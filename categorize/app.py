from flask import Flask, render_template, request, jsonify
import json
import csv
import os
import logging

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

@app.route('/all_reports')
def all_reports():
    reports_dir = '../all_reports'
    report_files = os.listdir(reports_dir)
    return render_template('all_reports.html', report_files=report_files)

@app.route('/report/<folder_name>')
# def report(folder_name):
#     reports_dir = '../all_reports'
#     csv_files = [f for f in os.listdir(os.path.join(reports_dir, folder_name)) if f.endswith('.csv')]
#     report_data = {}
#     for csv_file in csv_files:
#         logging.info(f"Processing file: {csv_file}")
#         with open(os.path.join(reports_dir, folder_name, csv_file), 'r', encoding='utf-8') as f:
#             reader = csv.DictReader(f)
#             report_title = os.path.splitext(csv_file)[0]
#             if 'earning' in report_title.lower():
#                 report_title = 'הכנסות בנק'
#             elif 'expenses' in report_title.lower():
#                 report_title = 'הוצאות בנק'
#             elif 'cc' in report_title.lower():
#                 report_title = 'פירוט הוצאות אשראי'
#                 # Add the 'סוג הוצאה' column
#                 with open('transaction_kind.json', 'r', encoding='utf-8') as t:
#                     transaction_data = json.load(t)
#                 rows = list(reader)
#                 for row in rows:
#                     business_name = row['שם בית עסק']
#                     if business_name in transaction_data:
#                         row['סוג הוצאה'] = transaction_data[business_name]['category']
#                     else:
#                         row['סוג הוצאה'] = 'Other'
#                 report_data[report_title] = rows
#             else:
#                 report_data[report_title] = list(reader)
#     logging.info(f"report_data: {report_data}")
#     return render_template('report.html', report_data=report_data)


@app.route('/report/<folder_name>')
def report(folder_name):
    reports_dir = '../all_reports'
    csv_files = [f for f in os.listdir(os.path.join(reports_dir, folder_name)) if f.endswith('.csv')]
    report_data = {}
    for csv_file in csv_files:
        with open(os.path.join(reports_dir, folder_name, csv_file), 'r', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            report_data[os.path.splitext(csv_file)[0]] = list(reader)
    return render_template('report.html', report_data=report_data)

if __name__ == '__main__':
    app.run(debug=True)