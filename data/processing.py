import pandas as pd
# from app import streamlit_session_state as st_session

def process_data(df):
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")
    df["Amount"] = pd.to_numeric(df["Amount"])
    df["Share"] = pd.to_numeric(df["Share"]) / 100
    df["Amount"] = df["Amount"] * df["Share"]
    df["Month"] = df["Date"].dt.to_period("M")
    return df


def current_month_total(df):
    current_month = pd.Timestamp.now().to_period("M")
    current_month_df = df[df["Month"] == current_month]
    return current_month_df["Amount"].sum()


def last_month_total(df):
    last_month = (pd.Timestamp.now() - pd.DateOffset(months=1)).to_period("M")
    last_month_data = df[df["Month"] == last_month]
    return last_month_data["Amount"].sum()


def todays_total(df):
    today = pd.Timestamp.now().normalize()  # Get today's date
    today_data = df[df["Date"] == today]
    return today_data["Amount"].sum()


def monthly_category_spending(df, date):
    selected_month = pd.Timestamp(date).to_period("M")
    # current_month = pd.Timestamp.now().to_period("M")
    selected_month_month_df = df[df["Month"] == selected_month]
    return selected_month_month_df.groupby("Category1")["Amount"].sum().reset_index()


def prev_and_current_spending_trend(df):
    """
    Create dataset that represents cumulative spending 
    over the last month and the current month.
    """
    daily_spending = df.groupby(df["Date"])["Amount"].sum().reset_index()
    daily_spending["Cumulative Monthly Amount"] = daily_spending.groupby(daily_spending["Date"].dt.to_period("M"))["Amount"].cumsum()

    now = pd.Timestamp.now()
    start_of_prev_month = (now - pd.DateOffset(months=1)).replace(day=1)

    # TODO: considier the case where no entry for 1st of month is present. How will ffill work then?
    # Spoiler alert: It doesn't work. Need to set value current month to zero in that case.
    date_range = pd.date_range(start=start_of_prev_month.date(), end=now.date())
    date_spine = pd.DataFrame(date_range, columns=['Date'])

    date_spine = date_spine.merge(
        daily_spending[['Cumulative Monthly Amount']],
        left_on='Date',
        right_on=daily_spending['Date'],
        how='left',
    ).ffill()

    prev = date_spine[date_spine['Date'].dt.to_period("M") == start_of_prev_month.to_period("M")]
    prev.set_index(prev['Date'].dt.day, inplace=True)
    curr = date_spine[date_spine['Date'].dt.to_period("M") == now.to_period("M")]
    curr.set_index(curr['Date'].dt.day, inplace=True)

    return prev, curr


def delta_between_prev_and_current_month(prev: pd.DataFrame, curr: pd.DataFrame):
    today = int(pd.Timestamp.now().strftime("%d"))
    prev_amt = float(prev.loc[today, 'Cumulative Monthly Amount']) # type: ignore
    curr_amt = float(curr.loc[today, 'Cumulative Monthly Amount']) # type: ignore
    delta = curr_amt - prev_amt  # negative delta is good
    pct = delta * 100 / prev_amt
    return delta, pct



def avg_daily_spending_excluding_rent_prev_and_curr_month(df: pd.DataFrame):
    now = pd.Timestamp.now()
    last_month = (now - pd.DateOffset(months=1))

    prev = df[df["Month"] == last_month.to_period("M")]
    curr = df[df["Month"] == now.to_period("M")]
    
    # filter out rent
    prev = prev[prev['Category1'] != 'Rent']
    curr = curr[curr['Category1'] != 'Rent']
    
    p_avg = prev['Amount'].sum() /  last_month.days_in_month
    c_avg = curr['Amount'].sum() / int(now.strftime('%d'))
    return p_avg, c_avg


def unique_years_and_months(df: pd.DataFrame):
    df["MonthName"] = df["Month"].strftime("%B")
    df["Year"] = df["Year"].strftime("%Y")

    return sorted(df["Year"].unique()), sorted(df["MonthName"].unique())
