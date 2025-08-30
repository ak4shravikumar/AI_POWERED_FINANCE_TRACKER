import streamlit as st
import pandas as pd
import plotly.express as px

st.title("AI Finance Tracker")

# Load CSV data once and convert 'Date' properly
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.read_csv('transactions.csv')
    st.session_state.transactions['Date'] = pd.to_datetime(
        st.session_state.transactions['Date'],
        format='%Y-%m-%d',
        errors='coerce'
    )
    # Drop rows with missing dates to avoid errors
    st.session_state.transactions = st.session_state.transactions.dropna(subset=['Date'])

df = st.session_state.transactions

# Create 'Month' column dynamically from Date column
df['Month'] = df['Date'].dt.to_period('M')

# Overall category summary table to give broad spending overview
category_summary = df.groupby('Category')['Amount'].sum().reset_index()
category_summary['% of Total'] = (category_summary['Amount'] / category_summary['Amount'].sum() * 100).round(2)
st.subheader("Category Summary")
st.table(category_summary)

# Pie and bar charts show overall spending distribution, unfiltered
spending_summary = df.groupby('Category')['Amount'].sum().reset_index()

pie_fig = px.pie(
    spending_summary,
    names='Category',
    values='Amount',
    title='Overall Spending by Category',
    color_discrete_sequence=px.colors.qualitative.Pastel,
)
st.plotly_chart(pie_fig)

top_cats = spending_summary.sort_values(by='Amount', ascending=False).head(5)
bar_fig = px.bar(
    top_cats,
    x='Category',
    y='Amount',
    title='Top Spending Categories',
    color='Category',
    text='Amount',
    color_discrete_sequence=px.colors.qualitative.Vivid,
)
st.plotly_chart(bar_fig)

# Monthly spending trend line chart (overall)
monthly_totals = df.groupby('Month')['Amount'].sum().reset_index()
monthly_totals['Month'] = monthly_totals['Month'].astype(str)
line_fig = px.line(
    monthly_totals,
    x='Month',
    y='Amount',
    title='Monthly Spending Trend',
    markers=True,
)
st.plotly_chart(line_fig)

# Category filter dropdown placed before transactions for clarity
categories = df['Category'].unique().tolist()
categories.insert(0, 'All')
selected_category = st.selectbox("Filter by Category", categories)

# Filter data to show only transactions for the selected category (or all)
filtered_df = df if selected_category == 'All' else df[df['Category'] == selected_category]

# Show filtered transactions table
st.subheader(f"Transactions: {selected_category}")
st.dataframe(filtered_df)

# Show total spending based on filtered transactions
total_spent = filtered_df['Amount'].sum()
st.write(f"**Total Spending: ₹{total_spent}**")

# Auto-categorization function for new transactions
def auto_categorize(description):
    desc = description.lower()
    if any(k in desc for k in ["swiggy", "zomato", "pizza"]):
        return "Food"
    elif any(k in desc for k in ["uber", "ola", "taxi"]):
        return "Transport"
    elif any(k in desc for k in ["amazon", "flipkart"]):
        return "Shopping"
    else:
        return "Other"

# Spending insights - month-over-month for selected category
def spending_insight(df, category):
    cat_df = df[df['Category'] == category]
    latest = df['Date'].max()
    cur_month, cur_year = latest.month, latest.year
    prev_month = 12 if cur_month == 1 else cur_month - 1
    prev_year = cur_year - 1 if cur_month == 1 else cur_year

    current_sum = cat_df[(cat_df['Date'].dt.month == cur_month) & (cat_df['Date'].dt.year == cur_year)]['Amount'].sum()
    prev_sum = cat_df[(cat_df['Date'].dt.month == prev_month) & (cat_df['Date'].dt.year == prev_year)]['Amount'].sum()

    if prev_sum == 0:
        if current_sum == 0:
            return f"No spending in {category} for the past two months."
        else:
            return f"New spending in {category}: ₹{current_sum} this month."

    change = ((current_sum - prev_sum) / prev_sum) * 100
    if change > 0:
        return f"You increased your {category} spending by {change:.1f}% compared to last month."
    elif change < 0:
        return f"You decreased your {category} spending by {abs(change):.1f}% compared to last month."
    else:
        return f"Your {category} spending is unchanged from last month."

if selected_category != 'All':
    message = spending_insight(df, selected_category)
    st.info(message)

# Form to add new transactions
st.subheader("Add New Transaction")
with st.form("transaction_form"):
    date = st.date_input("Date")
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0)
    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        category = auto_categorize(description)
        new_entry = {
            "Date": date.strftime("%Y-%m-%d"),
            "Description": description,
            "Amount": amount,
            "Category": category,
        }
        st.session_state.transactions = pd.concat(
            [st.session_state.transactions, pd.DataFrame([new_entry])], ignore_index=True
        )
        st.session_state.transactions['Date'] = pd.to_datetime(
            st.session_state.transactions['Date'],
            format='%Y-%m-%d',
            errors='coerce',
        )
        st.session_state.transactions.to_csv('transactions.csv', index=False)
        st.success("Transaction added and saved!")
        st.rerun()
