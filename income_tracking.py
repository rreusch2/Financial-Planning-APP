# income_tracking.py

# Import necessary libraries
from datetime import datetime
import streamlit as st

# Class to represent an income record
class Income:
    def __init__(self, user_id, source, amount, date, notes=''):
        self.user_id = user_id
        self.source = source
        self.amount = amount
        self.date = date
        self.notes = notes

# In-memory store for income records (to be replaced with a database in production)
income_store = []

# Function to add an income record
def add_income(user_id, source, amount, date, notes=''):
    new_income = Income(user_id, source, amount, date, notes)
    income_store.append(new_income)
    return new_income

# Function to get income records for a specific user and timeframe
def get_income_by_user(user_id, start_date=None, end_date=None):
    user_incomes = [income for income in income_store if income.user_id == user_id]
    if start_date and end_date:
        user_incomes = [income for income in user_incomes if start_date <= income.date <= end_date]
    return user_incomes
