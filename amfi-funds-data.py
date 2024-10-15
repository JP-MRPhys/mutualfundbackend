from datetime import datetime

class Fund:
    def __init__(self, scheme_code, scheme_name, fund_house, scheme_type, scheme_category, scheme_sub_category):
        self.scheme_code = scheme_code
        self.scheme_name = scheme_name
        self.fund_house = fund_house
        self.scheme_type = scheme_type
        self.scheme_category = scheme_category
        self.scheme_sub_category = scheme_sub_category
        self.nav_history = []
        self.aum_history = []
        self.expense_ratio = None
        self.risk_grade = None
        self.benchmark = None
        self.fund_manager = None
        self.inception_date = None
        self.exit_load = None
        self.min_investment = None
        self.investment_objective = None

    def update_nav(self, date, nav):
        self.nav_history.append({"date": date, "nav": nav})

    def update_aum(self, date, aum):
        self.aum_history.append({"date": date, "aum": aum})

    def get_current_nav(self):
        return self.nav_history[-1]["nav"] if self.nav_history else None

    def get_current_aum(self):
        return self.aum_history[-1]["aum"] if self.aum_history else None

    def set_fund_details(self, expense_ratio, risk_grade, benchmark, fund_manager, inception_date, exit_load, min_investment, investment_objective):
        self.expense_ratio = expense_ratio
        self.risk_grade = risk_grade
        self.benchmark = benchmark
        self.fund_manager = fund_manager
        self.inception_date = inception_date
        self.exit_load = exit_load
        self.min_investment = min_investment
        self.investment_objective = investment_objective

    def __str__(self):
        return f"{self.scheme_name} (Code: {self.scheme_code}) - {self.fund_house}"

class FundManager:
    def __init__(self):
        self.funds = {}

    def add_fund(self, fund):
        self.funds[fund.scheme_code] = fund

    def get_fund(self, scheme_code):
        return self.funds.get(scheme_code)

    def get_funds_by_category(self, category):
        return [fund for fund in self.funds.values() if fund.scheme_category == category]

    def get_funds_by_fund_house(self, fund_house):
        return [fund for fund in self.funds.values() if fund.fund_house == fund_house]

    def update_nav(self, scheme_code, date, nav):
        if scheme_code in self.funds:
            self.funds[scheme_code].update_nav(date, nav)

    def update_aum(self, scheme_code, date, aum):
        if scheme_code in self.funds:
            self.funds[scheme_code].update_aum(date, aum)

# Example usage:
if __name__ == "__main__":
    fund_manager = FundManager()

    # Creating a sample fund
    hdfc_equity = Fund(
        scheme_code="HDFC001",
        scheme_name="HDFC Equity Fund",
        fund_house="HDFC Mutual Fund",
        scheme_type="Open Ended",
        scheme_category="Equity",
        scheme_sub_category="Large Cap"
    )

    hdfc_equity.set_fund_details(
        expense_ratio=1.5,
        risk_grade="High",
        benchmark="Nifty 50 TRI",
        fund_manager="Prashant Jain",
        inception_date=datetime(1995, 1, 1),
        exit_load="1% if redeemed within 1 year",
        min_investment=5000,
        investment_objective="Long-term capital appreciation through investment in equity and equity-related instruments."
    )

    fund_manager.add_fund(hdfc_equity)

    # Updating NAV and AUM
    fund_manager.update_nav("HDFC001", datetime(2023, 10, 15), 825.67)
    fund_manager.update_aum("HDFC001", datetime(2023, 9, 30), 26500000000)

    # Retrieving fund information
    print(fund_manager.get_fund("HDFC001"))
    print(f"Current NAV: {fund_manager.get_fund('HDFC001').get_current_nav()}")
    print(f"Current AUM: {fund_manager.get_fund('HDFC001').get_current_aum()}")
