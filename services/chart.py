from sqlalchemy import func, case, cast, Integer, extract, desc
from models.transaction import Transaction
from models.category import Category
from utils.chart_data_manager import transform_chart_data
from utils.constants import CHART_TYPES, MONTHS
from datetime import datetime 


class ChartService():
    def __init__(self, db):
        self.db = db
        self.now = datetime.now()

    def get_income_expense_chart(self):
        query = (
            self.db.query(
                cast(func.strftime('%m', Transaction.transaction_date), Integer).label('month'),
                func.sum(case((Transaction.type == 'INCOME', Transaction.amount), else_=0)).label('total_income'),
                func.sum(case((Transaction.type == 'EXPENSE', Transaction.amount), else_=0)).label('total_expense'),
            )
            .group_by('month')
            .order_by('month')
        )
        results = query.all()
        row_data = [
            {"category": MONTHS[str(month)], "Income": income, "Expense": expense}
            for month, income, expense in results
        ]
        result = transform_chart_data(CHART_TYPES["bar"], row_data)
        return result

    def get_expense_by_category_chart(self):
        query = (
            self.db.query(
                case(
                    (Transaction.category_id == None, "Uncategorized"),
                    else_=Category.name
                ).label("label"),
                func.sum(Transaction.amount).label("value")
            )
            .outerjoin(Category, Category.id == Transaction.category_id)
            .filter(Transaction.type == "EXPENSE")
            .filter(extract('month', Transaction.transaction_date) == self.now.month)
            .filter(extract('year', Transaction.transaction_date) == self.now.year)
            .group_by(Transaction.category_id)
            .order_by(desc('value'))
            .limit(5)
        )
        results = query.all()
        row_data = [
            {"label": category, "value": amount}
            for category, amount in results
        ]
        result = transform_chart_data(CHART_TYPES["pie"], row_data)
        print("result", result)
        return result