import pandas as pd

# Load the transactions CSV file
df = pd.read_csv('transactions.csv')

# 1. Total spending (sum of all amounts)
total_spent = df['Amount'].sum()
print(f"Total Spending: ₹{total_spent}")

# 2. Filter transactions by category (e.g., Food)
food_expenses = df[df['Category'] == 'Food']
print("\nFood Expenses:")
print(food_expenses)

# 3. Summarize spending by category
spending_by_category = df.groupby('Category')['Amount'].sum()
print("\nSpending by Category:")
print(spending_by_category)
