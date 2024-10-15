from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Placeholder for Aadhaar/PAN verification API integration
def verify_aadhaar_pan(aadhaar, pan):
    # Integrate with a third-party API here
    # ...
    return True  # Replace with actual verification result

@app.route('/api/apply', methods=['POST'])
def apply_loan():
    data = request.get_json()
    aadhaar = data.get('aadhaar')
    pan = data.get('pan')
    loan_amount = int(data.get('loanAmount'))
    loan_term = int(data.get('loanTerm'))

    if not verify_aadhaar_pan(aadhaar, pan):
        return jsonify({"error": "Aadhaar/PAN verification failed"}), 400

    # Loan amount and term validation based on CIBIL (placeholder - assuming good CIBIL for now)
    if not (10000 <= loan_amount <= 200000):  # Example good CIBIL range
        return jsonify({"error": "Loan amount must be between 10000 and 200000"}), 400


    # Calculate EMI (Example)
    interest_rate = 0.027  # 2.7% monthly interest
    num_payments = loan_term
    emi = (loan_amount * interest_rate * (1 + interest_rate)**num_payments) / ((1 + interest_rate)**num_payments - 1)

    # ... (Database interaction to store application details)

    return jsonify({"emi": emi, "loan_term": loan_term}) #Simplified return

@app.route('/<path:path>')
def file(path):
    return send_file('public/'+path)
@app.route('/')
def root():
    return send_file('public/index.html')
if __name__ == '__main__':
    app.run(debug=True)