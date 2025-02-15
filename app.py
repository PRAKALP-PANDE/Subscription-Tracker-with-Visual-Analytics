from flask import Flask, render_template, request, redirect, jsonify, send_file
import sqlite3
from datetime import datetime
import csv
import pandas as pd
import io

app = Flask(__name__)
DB_NAME = "user_management.db"

# Initialize database
def initialize_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        contact TEXT UNIQUE NOT NULL,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        amount DECIMAL NOT NULL,
                        description TEXT
                      )''')
    conn.commit()
    conn.close()

initialize_db()

# Routes
@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template('index.html', users=users)

@app.route('/add', methods=['POST'])
def add_user():
    data = request.form
    name = data.get('name')
    contact = data.get('contact')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    amount = data.get('amount')
    description = data.get('description')

    if not all([name, contact, start_date, end_date, amount]):
        return jsonify({"error": "All fields except description are required"}), 400

    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    if start_date >= end_date:
        return jsonify({"error": "Start date must be before end date"}), 400

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, contact, start_date, end_date, amount, description) VALUES (?, ?, ?, ?, ?, ?)",
                       (name, contact, start_date, end_date, amount, description))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400

    return redirect('/')

@app.route('/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/export_csv')
def export_csv():
    """Exports user data to a CSV file for download."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")

    # Fetch all rows and column headers
    rows = cursor.fetchall()
    headers = [description[0] for description in cursor.description]
    conn.close()

    # Create an in-memory bytes buffer for the CSV data
    csv_file = io.StringIO()
    writer = csv.writer(csv_file)

    # Write the column headers and data rows
    writer.writerow(headers)
    writer.writerows(rows)

    # Move to the beginning of the buffer
    csv_file.seek(0)

    # Send the CSV file as a downloadable attachment
    return send_file(
        io.BytesIO(csv_file.getvalue().encode('utf-8')),  # Encode StringIO as bytes
        mimetype='text/csv',
        download_name='users.csv',
        as_attachment=True
    )

@app.route('/analyze')
def analyze():
    """Performs data analysis and returns results for visualization."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT start_date, end_date, amount FROM users")
    rows = cursor.fetchall()
    conn.close()

    # Convert the data to a DataFrame for analysis
    df = pd.DataFrame(rows, columns=['start_date', 'end_date', 'amount'])
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    # Peak Sales Periods
    sales_by_date = df.groupby(df['start_date'].dt.date)['amount'].sum().sort_values(ascending=False).head(5)

    # User Onboarding Trends
    onboarding_trends = df['start_date'].dt.to_period('M').value_counts().sort_index()

    # Format the response
    analysis_results = {
        "peak_sales_periods": {
            "dates": sales_by_date.index.astype(str).tolist(),
            "amounts": sales_by_date.values.tolist()
        },
        "user_onboarding_trends": {
            "months": onboarding_trends.index.astype(str).tolist(),
            "counts": onboarding_trends.values.tolist()
        }
    }

    return jsonify(analysis_results)

if __name__ == '__main__':
    app.run(debug=True)
