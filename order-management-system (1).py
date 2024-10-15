from datetime import datetime, timedelta
import uuid

# Mock Razorpay client for demonstration purposes
class MockRazorpayClient:
    def create_order(self, amount, currency="INR"):
        return {
            "id": f"order_{uuid.uuid4().hex}",
            "entity": "order",
            "amount": amount,
            "currency": currency,
            "status": "created",
            "created_at": int(datetime.now().timestamp())
        }

    def verify_payment_signature(self, params_dict):
        # In a real scenario, this would verify the signature
        return True

class OrderManagementSystem:
    def __init__(self, fund_manager):
        self.fund_manager = fund_manager
        self.orders = {}
        self.sip_orders = {}
        self.razorpay_client = MockRazorpayClient()

    def place_lump_sum_order(self, user_id, fund_code, amount, order_type):
        order_id = str(uuid.uuid4())
        razorpay_order = self.razorpay_client.create_order(amount * 100)  # Razorpay expects amount in paise
        order = {
            'order_id': order_id,
            'user_id': user_id,
            'fund_code': fund_code,
            'amount': amount,
            'order_type': order_type,
            'status': 'Pending Payment',
            'created_at': datetime.now(),
            'executed_at': None,
            'units_allotted': None,
            'razorpay_order_id': razorpay_order['id']
        }
        self.orders[order_id] = order
        return order_id, razorpay_order['id']

    def place_sip_order(self, user_id, fund_code, amount, frequency, start_date, end_date=None):
        sip_id = str(uuid.uuid4())
        sip_order = {
            'sip_id': sip_id,
            'user_id': user_id,
            'fund_code': fund_code,
            'amount': amount,
            'frequency': frequency,
            'start_date': start_date,
            'end_date': end_date,
            'status': 'Active',
            'created_at': datetime.now(),
            'last_executed': None,
            'next_execution': start_date
        }
        self.sip_orders[sip_id] = sip_order
        return sip_id

    def confirm_payment(self, order_id, payment_id, signature):
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]
        params_dict = {
            'razorpay_order_id': order['razorpay_order_id'],
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        if self.razorpay_client.verify_payment_signature(params_dict):
            order['status'] = 'Pending'
            return True
        else:
            order['status'] = 'Payment Failed'
            return False

    def cancel_order(self, order_id):
        if order_id in self.orders:
            if self.orders[order_id]['status'] in ['Pending Payment', 'Pending']:
                self.orders[order_id]['status'] = 'Cancelled'
                return True
        return False

    def stop_sip(self, sip_id):
        if sip_id in self.sip_orders:
            if self.sip_orders[sip_id]['status'] == 'Active':
                self.sip_orders[sip_id]['status'] = 'Stopped'
                return True
        return False

    def process_orders(self, current_date=None):
        if current_date is None:
            current_date = datetime.now().date()

        for order_id, order in self.orders.items():
            if order['status'] == 'Pending':
                self._execute_order(order_id, current_date)

        for sip_id, sip_order in self.sip_orders.items():
            if sip_order['status'] == 'Active' and sip_order['next_execution'].date() <= current_date:
                self._execute_sip_installment(sip_id, current_date)

    def _execute_order(self, order_id, execution_date):
        order = self.orders[order_id]
        fund = self.fund_manager.get_fund(order['fund_code'])
        
        if fund:
            current_nav = fund.get_current_nav()
            if current_nav:
                units_allotted = order['amount'] / current_nav
                order['status'] = 'Executed'
                order['executed_at'] = execution_date
                order['units_allotted'] = units_allotted

                # Here you would update the user's portfolio
                # portfolio.add_units(order['fund_code'], units_allotted)

                return True
        
        order['status'] = 'Failed'
        return False

    def _execute_sip_installment(self, sip_id, execution_date):
        sip_order = self.sip_orders[sip_id]
        
        # Create a lump sum order for this SIP installment
        lump_sum_order_id, razorpay_order_id = self.place_lump_sum_order(
            sip_order['user_id'],
            sip_order['fund_code'],
            sip_order['amount'],
            'Buy'
        )

        # In a real scenario, you would initiate automatic payment here
        # For demonstration, we'll assume payment is successful
        payment_id = f"pay_{uuid.uuid4().hex}"
        signature = "mocked_signature"
        if self.confirm_payment(lump_sum_order_id, payment_id, signature):
            # Execute the lump sum order
            if self._execute_order(lump_sum_order_id, execution_date):
                sip_order['last_executed'] = execution_date
                sip_order['next_execution'] = self._calculate_next_execution(sip_order)

                if sip_order['end_date'] and execution_date >= sip_order['end_date']:
                    sip_order['status'] = 'Completed'
        else:
            # Handle failed payment
            self.sip_orders[sip_id]['status'] = 'Payment Failed'

    def _calculate_next_execution(self, sip_order):
        last_execution = sip_order['last_executed']
        frequency = sip_order['frequency']

        if frequency == 'Monthly':
            next_execution = last_execution + timedelta(days=30)
        elif frequency == 'Quarterly':
            next_execution = last_execution + timedelta(days=91)
        elif frequency == 'Semi-Annually':
            next_execution = last_execution + timedelta(days=182)
        elif frequency == 'Annually':
            next_execution = last_execution + timedelta(days=365)
        else:
            raise ValueError(f"Unsupported frequency: {frequency}")

        return next_execution

    def get_order_status(self, order_id):
        return self.orders.get(order_id, {}).get('status', 'Order not found')

    def get_sip_status(self, sip_id):
        return self.sip_orders.get(sip_id, {}).get('status', 'SIP not found')

    def get_user_orders(self, user_id):
        return [order for order in self.orders.values() if order['user_id'] == user_id]

    def get_user_sips(self, user_id):
        return [sip for sip in self.sip_orders.values() if sip['user_id'] == user_id]

# Example usage:
if __name__ == "__main__":
    from datetime import date

    # Assuming we have a FundManager instance
    fund_manager = FundManager()
    # ... (initialize fund_manager with some funds)

    oms = OrderManagementSystem(fund_manager)

    # Place a lump sum order
    lump_sum_order_id, razorpay_order_id = oms.place_lump_sum_order('USER001', 'HDFC001', 5000, 'Buy')
    print(f"Lump sum order placed: {lump_sum_order_id}, Razorpay Order ID: {razorpay_order_id}")

    # Simulate payment confirmation
    payment_id = f"pay_{uuid.uuid4().hex}"
    signature = "mocked_signature"
    payment_confirmed = oms.confirm_payment(lump_sum_order_id, payment_id, signature)
    print(f"Payment confirmed: {payment_confirmed}")

    # Place a SIP order
    sip_order_id = oms.place_sip_order('USER001', 'HDFC001', 1000, 'Monthly', date(2023, 11, 1), date(2024, 10, 31))
    print(f"SIP order placed: {sip_order_id}")

    # Process orders
    oms.process_orders(date(2023, 11, 1))

    # Check order statuses
    print(f"Lump sum order status: {oms.get_order_status(lump_sum_order_id)}")
    print(f"SIP order status: {oms.get_sip_status(sip_order_id)}")

    # Get user orders and SIPs
    print(f"User orders: {oms.get_user_orders('USER001')}")
    print(f"User SIPs: {oms.get_user_sips('USER001')}")
