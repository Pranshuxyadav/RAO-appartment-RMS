from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Load OTPs and room data from Excel file
def load_data():
    try:
        # Ensure the Excel file path is correct
        df = pd.read_excel('room_data.xlsx.xlsx')  # Correct the file path if necessary
        return df
    except FileNotFoundError:
        return None

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/otp', methods=['GET'])
def otp_login():
    otp = request.args.get('otp')
    
    # Debug print to check if OTP is received
    print(f"Received OTP: {otp}")
    
    if otp:
        df = load_data()
        
        if df is None:
            return "Error: Data file not found.", 500
        
        # Convert the OTP column and input OTP to lowercase and strip any extra spaces
        df['OTP'] = df['OTP'].astype(str).str.lower().str.strip()
        otp = otp.lower().strip()
        
        # Debug print to check the OTP column from the DataFrame
        print(f"OTP column from DataFrame: {df['OTP'].tolist()}")  # Print OTP column for debugging
        
        # Check if the entered OTP exists in the file
        tenant_data = df[df['OTP'] == otp]
        
        if not tenant_data.empty:
            tenant = tenant_data.iloc[0].to_dict()
            return render_template('room_data.html', tenant=tenant, room_no=tenant['Room No.'])
        else:
            return "Invalid OTP. Please try again.", 400
    return "OTP is required", 400


if __name__ == '__main__':
    app.run(debug=True)
