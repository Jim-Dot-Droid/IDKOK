
import streamlit as st
import pandas as pd
import numpy as np
import os

RESULTS_FILE = "results.csv"
INITIAL_BALANCE = 0.1
BET_AMOUNT = 0.01

def load_results():
    if os.path.exists(RESULTS_FILE):
        return pd.read_csv(RESULTS_FILE)
    return pd.DataFrame(columns=["prediction", "actual", "correct"])

def save_result(prediction, actual, correct):
    df = load_results()
    df.loc[len(df)] = [prediction, actual, correct]
    df.to_csv(RESULTS_FILE, index=False)

def normalize_input(value):
    return value / 100 if value > 10 else value

def get_flat_balance_series(df):
    balance = INITIAL_BALANCE
    series = []
    for _, row in df.iterrows():
        if row["prediction"] == "Above":
            balance += BET_AMOUNT if row["correct"] else -BET_AMOUNT
        series.append(balance)
    return series

def get_martingale_balance_series(df):
    balance = INITIAL_BALANCE
    series = []
    streak = 0
    for _, row in df.iterrows():
        if row["prediction"] == "Above":
            bet = BET_AMOUNT * (2 ** streak)
            if row["correct"]:
                balance += bet
                streak = 0
            else:
                balance -= bet
                streak += 1
        series.append(balance)
    return series

def main():
    st.title("Crash Predictor — Flat & Martingale Balance Tracker")

    df = load_results()

    st.subheader("Add a Multiplier")
    new_val = st.text_input("Enter multiplier (e.g. 1.87 or 187 for %):")
    if st.button("Add"):
        try:
            val = normalize_input(float(new_val))
            prediction = "Above" if np.random.rand() > 0.5 else "Under"
            correct = (prediction == "Above" and val > 2.0) or (prediction == "Under" and val <= 2.0)
            save_result(prediction, val, correct)
            st.success(f"Prediction: {prediction} | Actual: {val:.2f} → {'Correct' if correct else 'Wrong'}")
            df = load_results()
        except:
            st.error("Invalid input.")

    st.subheader("SOL Balances")
    if not df.empty:
        df["Flat Balance"] = get_flat_balance_series(df)
        df["Martingale Balance"] = get_martingale_balance_series(df)
        st.line_chart(df[["Flat Balance", "Martingale Balance"]])

        st.metric("Flat Balance", f"{df['Flat Balance'].iloc[-1]:.4f} SOL")
        st.metric("Martingale Balance", f"{df['Martingale Balance'].iloc[-1]:.4f} SOL")

        st.subheader("Accuracy")
        total = len(df)
        correct = df["correct"].sum()
        st.metric("Total Predictions", total)
        st.metric("Correct Predictions", int(correct))
        st.metric("Accuracy", f"{correct / total:.1%}")
    else:
        st.write("Add at least one multiplier to start tracking.")

    if st.button("Reset Data"):
        if os.path.exists(RESULTS_FILE):
            os.remove(RESULTS_FILE)
        st.success("Data reset.")

if __name__ == "__main__":
    main()
