from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)

# Assuming we have instances of our previously created classes
fund_manager = FundManager()
order_management_system = OrderManagementSystem(fund_manager)

# Helper function to parse dates from strings
def parse_date(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d").date()

# Fund Data API
@app.route('/api/funds', methods=['GET'])
def get_funds():
    category = request.args.get('category')
    fund_house = request.args.get('fund_house')
    min_nav = request.args.get('min_nav')
    max_nav = request.args.get('max_nav')

    funds = fund_manager.funds.values()

    if category:
        funds = [f for f in funds if f.scheme_category == category]
    if fund_house:
        funds = [f for f in funds if f.fund_house == fund_house]
    if min_nav:
        funds = [f for f in funds if f.get_current_nav() >= float(min_nav)]
    if max_nav:
        funds = [f for f in funds if f.get_current_nav() <= float(max_nav)]

    return jsonify([{
        'scheme_code': f.scheme_code,
        'scheme_name': f.scheme_name,
        'fund_house': f.fund_house,
        'category': f.scheme_category,
        'nav': f.get_current_nav(),
        'aum': f.get_current_aum(),
        'expense_ratio': f.expense_ratio,
        'risk_grade': f.risk_grade,
        'ytd_return': calculate_ytd_return(f),
        '1y_return': calculate_1y_return(f),
        '3y_return': calculate_3y_return(f),
        '5y_return': calculate_5y_return(f)
    } for f in funds])

@app.route('/api/funds/<scheme_code>', methods=['GET'])
def get_fund_details(scheme_code):
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
            'investment_objective': fund.investment_objective,
            'min_investment': fund.min_investment,
            'exit_load': fund.exit_load,
            'benchmark': fund.benchmark,
            'nav_history': get_nav_history(fund),
            'performance': {
                'ytd_return': calculate_ytd_return(fund),
                '1y_return': calculate_1y_return(fund),
                '3y_return': calculate_3y_return(fund),
                '5y_return': calculate_5y_return(fund)
            }
        })
    return jsonify({'error': 'Fund not found'}), 404

# User Data API
@app.route('/api/users/<user_id>', methods=['GET'])
def get_user_data(user_id):
    # This is a placeholder. In a real application, you would fetch this data from a database.
    user = {
        'user_id': user_id,
        'name': 'John Doe',
        'email': 'johndoe@example.com',
        'phone': '+1234567890',
        'kyc_status': 'Verified',
        'account_opening_date': '2022-01-01',
        'total_investment': 100000,
        'current_value': 110000
    }
    
    # Fetch user's portfolio
    portfolio = get_user_portfolio(user_id)
    
    # Fetch user's orders
    orders = order_management_system.get_user_orders(user_id)
    
    # Fetch user's SIPs
    sips = order_management_system.get_user_sips(user_id)

    return jsonify({
        'user_info': user,
        'portfolio': portfolio,
        'orders': orders,
        'sips': sips
    })

@app.route('/api/users/<user_id>/portfolio', methods=['GET'])
def get_user_portfolio(user_id):
    # This is a placeholder. In a real application, you would fetch this data from a database.
    portfolio = [
        {
            'scheme_code': 'HDFC001',
            'scheme_name': 'HDFC Top 100 Fund',
            'units': 100,
            'average_cost': 350,
            'current_nav': 400,
            'current_value': 40000,
            'profit_loss': 5000,
            'returns': 14.28
        },
        {
            'scheme_code': 'ICICI001',
            'scheme_name': 'ICICI Prudential Bluechip Fund',
            'units': 200,
            'average_cost': 40,
            'current_nav': 45,
            'current_value': 9000,
            'profit_loss': 1000,
            'returns': 12.5
        }
    ]
    return jsonify(portfolio)

# Helper functions for calculating returns
def calculate_ytd_return(fund):
    # Placeholder implementation
    return 10.5

def calculate_1y_return(fund):
    # Placeholder implementation
    return 15.2

def calculate_3y_return(fund):
    # Placeholder implementation
    return 12.8

def calculate_5y_return(fund):
    # Placeholder implementation
    return 14.3

def get_nav_history(fund):
    # Placeholder implementation
    today = datetime.now().date()
    history = []
    for i in range(30):  # Last 30 days
        date = today - timedelta(days=i)
        history.append({
            'date': date.isoformat(),
            'nav': round(fund.get_current_nav() * (1 + (random.random() - 0.5) * 0.02), 2)
        })
    return history

if __name__ == '__main__':
    app.run(debug=True)
