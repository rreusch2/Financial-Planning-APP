from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# Update visuals.py to only generate pie chart:
def generate_expense_charts(transactions, period='monthly'):
    """Generate category distribution pie chart"""
    try:
        categories_data = {}
        
        # Get current date ranges
        today = datetime.now()
        if period == 'yearly':
            start_date = datetime(today.year, 1, 1)
        else:  # monthly
            start_date = datetime(today.year, today.month, 1)
        
        # Process transactions
        for t in transactions:
            if t.amount < 0 and t.date >= start_date:  # Only expenses within period
                category = t.category.split(':')[0] if t.category else 'Uncategorized'
                categories_data[category] = categories_data.get(category, 0) + abs(t.amount)
        
        if not categories_data:
            # Create empty chart with "No Data" message
            fig = go.Figure().add_annotation(
                text="No transaction data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig.to_html()

        # Create category pie chart
        period_text = "Year to Date" if period == 'yearly' else "Month to Date"
        fig = px.pie(
            values=list(categories_data.values()),
            names=list(categories_data.keys()),
            title=f'Expense Distribution by Category ({period_text})'
        )
        fig.update_layout(
            template='plotly_white',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True
        )
        
        return fig.to_html()
        
    except Exception as e:
        print(f"Error generating chart: {str(e)}")
        return None