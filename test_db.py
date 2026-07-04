from database import *

create_database()

save_expense(
    "Food & Dining",
    500,
    "Good expense. Try cooking more at home."
)

print(get_expenses())