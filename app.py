from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Function to load data from Excel
def load_excel_data():
    excel_path = 'static/Book1 exam.xlsx'  # Make sure the file is uploaded to this path
    df = pd.read_excel(excel_path)
    data = df.to_dict(orient='records')
    return data

# Route to display the room query form
@app.route('/')
def room_query():
    return render_template('index.html')

# Route to display data for a specific room
@app.route('/room', methods=['GET'])
def room_data():
    room_no = request.args.get('room_no')  # Get the room number from the query string
    tenants = load_excel_data()  # Load the tenant data

    # Find the tenant with the given room number
    tenant = next((tenant for tenant in tenants if str(tenant['Room No.']) == room_no), None)

    return render_template('room_data.html', tenant=tenant, room_no=room_no)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)

