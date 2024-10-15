from datetime import datetime

class User:
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.watchlist = Watchlist(user_id)
        self.portfolio = Portfolio(user_id)
        self.orders = Orders(user_id)
        self.kyc_status = "Not Verified"
        self.kyc_details = {}
        self.bank_details = []

    def __str__(self):
        return f"User(id={self.user_id}, name={self.name}, email={self.email}, kyc_status={self.kyc_status})"

    def update_kyc(self, kyc_info):
        self.kyc_details = {
            "pan_number": kyc_info.get("pan_number"),
            "aadhar_number": kyc_info.get("aadhar_number"),
            "dob": kyc_info.get("dob"),
            "address": kyc_info.get("address"),
            "occupation": kyc_info.get("occupation"),
            "income_range": kyc_info.get("income_range"),
            "politically_exposed": kyc_info.get("politically_exposed", False)
        }
        self.kyc_status = "Pending Verification"

    def verify_kyc(self):
        # In a real system, this would involve a thorough verification process
        if all(self.kyc_details.values()):
            self.kyc_status = "Verified"
            return True
        return False

    def add_bank_account(self, account_info):
        new_account = {
            "account_number": account_info["account_number"],
            "ifsc_code": account_info["ifsc_code"],
            "account_holder_name": account_info["account_holder_name"],
            "bank_name": account_info["bank_name"],
            "is_primary": account_info.get("is_primary", False)
        }
        
        if new_account["is_primary"]:
            for account in self.bank_details:
                account["is_primary"] = False
        
        self.bank_details.append(new_account)

    def get_primary_bank_account(self):
        for account in self.bank_details:
            if account["is_primary"]:
                return account
        return None if not self.bank_details else self.bank_details[0]

    def set_primary_bank_account(self, account_number):
        for account in self.bank_details:
            if account["account_number"] == account_number:
                account["is_primary"] = True
            else:
                account["is_primary"] = False

class Watchlist:
    # ... (unchanged)

class Portfolio:
    # ... (unchanged)

class Orders:
    # ... (unchanged)
