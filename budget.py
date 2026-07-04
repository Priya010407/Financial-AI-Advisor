# -------------------------------
# CATEGORY-BASED BUDGET SYSTEM
# -------------------------------

def get_budget(category):

    budgets = {
        "Food & Dining": 5000,
        "Shopping": 4000,
        "Groceries": 6000,
        "Transportation": 3000,
        "Medical": 5000,
        "Entertainment": 2500,
        "Utilities": 4000,
        "Other": 2000
    }

    return budgets.get(category, 3000)


# -------------------------------
# MONTHLY SMART LIMIT (OPTIONAL)
# -------------------------------

def get_monthly_budget(income):

    try:

        income = float(income)

        return {
            "essential": income * 0.50,
            "savings": income * 0.30,
            "lifestyle": income * 0.20
        }

    except:

        return {
            "essential": 0,
            "savings": 0,
            "lifestyle": 0
        }