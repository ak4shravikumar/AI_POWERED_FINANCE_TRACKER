import streamlit as st
import pandas as pd
import plotly.express as px

st.title("AI Finance Tracker")

# Load CSV data once and keep in session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.read_csv('transactions.csv')

df = st.session_state.transactions

# Category filter as before
categories = df['Category'].unique().tolist()
categories.insert(0, 'All')
selected_category = st.selectbox("Filter by Category", categories)

if selected_category != 'All':
    filtered_df = df[df['Category'] == selected_category]
else:
    filtered_df = df

# Pie chart of spending by category (use filtered data)
spending_summary = filtered_df.groupby('Category')['Amount'].sum().reset_index()
fig = px.pie(spending_summary, names='Category', values='Amount', title='Spending by Category')
st.plotly_chart(fig)

st.subheader(f"Transactions: {selected_category}")
st.dataframe(filtered_df)

total_spent = filtered_df['Amount'].sum()
st.write(f"Total Spending: ₹{total_spent}")

# Transaction entry form
st.subheader("Add New Transaction")

with st.form("transaction_form"):
    date = st.date_input("Date")
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0)
    category = st.selectbox("Category", df['Category'].unique().tolist())
    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        new_entry = {
            "Date": date.strftime("%Y-%m-%d"),
            "Description": description,
            "Amount": amount,
            "Category": category
        }

        # Append new entry to session state DataFrame
        st.session_state.transactions = pd.concat([
            st.session_state.transactions,
            pd.DataFrame([new_entry])
        ], ignore_index=True)

        # Save updated transactions to CSV file
        st.session_state.transactions.to_csv('transactions.csv', index=False)

        st.success("Transaction added and saved!")

        # Refresh to show updated table and chart
        st.rerun()


