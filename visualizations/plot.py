import pandas as pd
import plotly.graph_objects as go
# import plotly.express as px

def plot_prev_and_current_month_spending_trend(previous: pd.DataFrame, current: pd.DataFrame):
    """
    Generates 2 trend lines comparing the cumulative monthly expenses 
    of the previous month and the current month.
    """

    current_month_name = pd.Timestamp.now().strftime("%B")
    prev_month_name = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime("%B")

    prev_line = go.scatter.Line(color='thistle', shape='spline', width=1.5)
    prev_month_plot = go.Scatter(x=previous.index, y=previous["Cumulative Monthly Amount"], line=prev_line, name=f"{prev_month_name}", mode='lines')

    curr_line = go.scatter.Line(color='mediumpurple', shape='spline', width=5)
    curr_month_plot = go.Scatter(x=current.index, y=current['Cumulative Monthly Amount'], line=curr_line, name=f"{current_month_name}", mode='lines')

    # Create the figure
    fig = go.Figure()

    # Add traces to the figure
    fig.add_trace(prev_month_plot)
    fig.add_trace(curr_month_plot)

    hline = go.layout.shape.Line(color='rgba(216,191,216, 0.5)', width=1, dash='dash')

    fig.add_hline(2000, line=hline)

    # remove grid lines
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)

    # add labels and adjust margins
    fig.update_layout(
        # title='Spending Trend',
        xaxis_title='Day',
        yaxis_tickformat = '0.3s',
        yaxis_tickprefix = '$ ',
        margin=dict(l=10, r=10, t=10, b=30)
    )

    return fig


def plot_spending_category(category_spending: pd.DataFrame):
    """
    Generate a bar graph for spending category
    """

    fig = go.Figure()

    pie_chart = go.Pie(
        labels=category_spending['Category1'].str.replace('_', ' '),
        values=category_spending['Amount'],
        hole=.3
    )
    fig.add_trace(pie_chart)
    fig.update_traces(
        hoverinfo='label+percent+value',
        textinfo='label+value',
        textposition='inside'
        # marker=dict(line=dict(color='#000000', width=0.5))
    )

    # fig = px.pie(category_spending, values='Amount', names='Category1', hole=.3, color_discrete_sequence=px.colors.sequential.RdBu)
    
    # fig.add_trace(go.Bar(
    #     x=category_spending['Category1'].str.replace('_', ' '),
    #     y=category_spending['Amount'],
    #     name='CAD',
    #     marker=dict(cornerradius=10, color='indianred')
    # ))

    # # remove grid lines
    # fig.update_xaxes(showgrid=False, zeroline=False)
    # fig.update_yaxes(showgrid=False, zeroline=False)

    # Customize the layout
    fig.update_layout(
        # title='Current Month Spending by Category',
        # yaxis_tickprefix='$ ',
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig
