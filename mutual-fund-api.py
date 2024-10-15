from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

# Assuming we have instances of our previously created classes
fund_manager = FundManager()
order_management_system = OrderManagementSystem(fund_manager)

# Helper function to parse dates from strings
def parse_date(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d").date()

# Fund Management APIs
@app.route('/funds', methods=['GET'])
def get_all_funds():
    funds = fund_manager.funds
    return jsonify([{
        'scheme_code': f.scheme_code,
        'scheme_name': f.scheme_name,
        'fund_house': f.fund_house,
        'category': f.scheme_category,
        'nav': f.get_current_nav()
    } for f in funds.values()])

@app.route('/funds/<scheme_code>', methods=['GET'])
def get_fund(scheme_code):
    fund = fund_manager.get_fund(scheme_code)
    if fund:
        return jsonify({
            'scheme_code': fund.scheme_code,
            'scheme_name': fund.scheme_name,
            'fund_house': fund.fund_house,
            'category': fund.scheme_category,
            'nav': fund.get_current_nav(),
            'aum': fund.get_current_aum(),
            'expense_ratio': fund.expense_ratio,
            'risk_grade': fund.risk_grade,
            'fund_manager': fund.fund_manager,
            'inception_date': fund.inception_date.isoformat() if fund.inception_date else None,
        })
    return jsonify({'error': 'Fund not found'}), 404

# Order Management APIs
@app.route('/orders/lumpsum', methods=['POST'])
def place_lumpsum_order():
    data = request.json
    order_id, razorpay_order_id = order_management_system.place_lump_sum_order(
        data['user_id'],
        data['fund_code'],
        data['amount'],
        data['order_type']
    )
    return jsonify({
        'order_id': order_id,
        'razorpay_order_id': razorpay_order_id
    }), 201

@app.route('/orders/sip', methods=['POST'])
def place_sip_order():
    data = request.json
    sip_id = order_management_system.place_sip_order(
        data['user_id'],
        data['fund_code'],
        data['amount'],
        data['frequency'],
        parse_date(data['start_date']),
        parse_date(data['end_date']) if 'end_date' in data else None
    )
    return jsonify({'sip_id': sip_id}), 201

@app.route('/orders/<order_id>/confirm-payment', methods=['POST'])
def confirm_payment(order_id):
    data = request.json
    success = order_management_system.confirm_payment(
        order_id,
        data['payment_id'],
        data['signature']
    )
    if success:
        return jsonify({'message': 'Payment confirmed successfully'}), 200
    return jsonify({'error': 'Payment confirmation failed'}), 400

@app.route('/orders/<order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    success = order_management_system.cancel_order(order_id)
    if success:
        return jsonify({'message': 'Order cancelled successfully'}), 200
    return jsonify({'error': 'Order cancellation failed'}), 400

@app.route('/orders/sip/<sip_id>/stop', methods=['POST'])
def stop_sip(sip_id):
    success = order_management_system.stop_sip(sip_id)
    if success:
        return jsonify({'message': 'SIP stopped successfully'}), 200
    return jsonify({'error': 'SIP stop failed'}), 400

@app.route('/orders/<order_id>', methods=['GET'])
def get_order_status(order_id):
    status = order_management_system.get_order_status(order_id)
    return jsonify({'order_id': order_id, 'status': status})

@app.route('/orders/sip/<sip_id>', methods=['GET'])
def get_sip_status(sip_id):
    status = order_management_system.get_sip_status(sip_id)
    return jsonify({'sip_id': sip_id, 'status': status})

@app.route('/users/<user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    orders = order_management_system.get_user_orders(user_id)
    return jsonify(orders)

@app.route('/users/<user_id>/sips', methods=['GET'])
def get_user_sips(user_id):
    sips = order_management_system.get_user_sips(user_id)
    return jsonify(sips)

# User Management APIs (assuming we have a User class)
@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    # This is a placeholder. You would typically fetch this from a database.
    user = {
        'user_id': user_id,
        'name': 'John Doe',
        'email': 'johndoe@example.com',
        'kyc_status': 'Verified'
    }
    return jsonify(user)

@app.route('/users/<user_id>/kyc', methods=['POST'])
def update_kyc(user_id):
    data = request.json
    # This is a placeholder. You would typically update this in a database.
    # Assume we have a update_kyc method in our User class
    # user.update_kyc(data)
    return jsonify({'message': 'KYC updated successfully'}), 200

# Admin APIs
@app.route('/admin/process-orders', methods=['POST'])
def process_orders():
    current_date = parse_date(request.json.get('date', datetime.now().strftime("%Y-%m-%d")))
    order_management_system.process_orders(current_date)
    return jsonify({'message': 'Orders processed successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
