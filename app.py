import streamlit as st
import pandas as pd
from data.google_sheet import read_sheet
# TODO: turn this into a class that contains the dataframe
from data.processing import (
    process_data,
    current_month_total,
    monthly_category_spending,
    prev_and_current_spending_trend,
    delta_between_prev_and_current_month,
    avg_daily_spending_excluding_rent_prev_and_curr_month,
    todays_total,
    unique_years_and_months
)
from visualizations.plot import (
    plot_prev_and_current_month_spending_trend,
    plot_spending_category,
)
# Constants
MONTHLY_EXPENSE_LIMIT = 2200

# Application State
streamlit_session_state = st.session_state

st.title("Expenses 🇨🇦 💵", anchor="home")

df = read_sheet()
if df.empty:
    st.error("No data found.")
    raise ValueError

df = process_data(df)
prev, curr = prev_and_current_spending_trend(df)
delta, _ = delta_between_prev_and_current_month(prev, curr)

current_month_name = pd.Timestamp.now().strftime("%B")
last_month_name = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime("%B")
total = current_month_total(df)


c1, c2, c3 = st.columns(3)
with c1:
    st.metric(
        label=f"Spent in {current_month_name}",
        value=f"{total:.0f} CAD",
        delta=f"{delta:.0f} from {last_month_name}",
        delta_color="inverse",
    )

remaining_days_in_month = pd.Timestamp.now().days_in_month - int(
    pd.Timestamp.now().strftime("%d")
)
remaining_budget = MONTHLY_EXPENSE_LIMIT - total
p_avg, c_avg = avg_daily_spending_excluding_rent_prev_and_curr_month(df)

# TODO: if selected month == current month then show these metrics
with c2:
    td_total = todays_total(df)
    st.metric(
        label=f"Today's Spending",
        value=f"{td_total:.0f} CAD",
        delta=f"""{(
            td_total - remaining_budget / remaining_days_in_month
            ):.0f} from target
            """,
        delta_color="inverse",
    )

with c3:
    remaining_budget_msg = (
        f"ℹ️ Remaining budget for {current_month_name} "
        f"is :red[**${remaining_budget:.0f}**] / "
        f"\${MONTHLY_EXPENSE_LIMIT}. "  # type: ignore
        f"Daily spending target is **${remaining_budget / remaining_days_in_month:.0f}**"
    )
    st.info(remaining_budget_msg)

with st.container():
    st.subheader("Spending Trend")
    selected_year_month = st.date_input(
        key="spending_trend_month_year",
        label="Select year and month",
        value="today",
        format="YYYY-MM-DD",
        help="Navigate to the desired month and pick any date.",
    )
    fig1 = plot_prev_and_current_month_spending_trend(prev, curr)
    st.plotly_chart(
        fig1,
        theme="streamlit",
        use_container_width=True,
        config={"displayModeBar": False},
    )

st.subheader("Monthly Spending by Category")
date_for_spending_category = st.date_input(
    key="spending_category_month_year",
    label="Select year and month",
    value="today",
    format="YYYY-MM-DD",
    help="Navigate to the desired month and pick any date.",
)
category_spending = monthly_category_spending(df, date_for_spending_category)

with st.container():
    spending_category_month_year = (
        pd.Timestamp(date_for_spending_category).strftime("%Y %B")  # type: ignore
    )
    st.write(f"Showing results for **{spending_category_month_year}**")
    fig2 = plot_spending_category(category_spending)
    st.plotly_chart(
        fig2,
        theme="streamlit",
        use_container_width=True,
        config={"displayModeBar": False},
    )
