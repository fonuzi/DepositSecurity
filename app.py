from flask import Flask, render_template_string
import plotly.graph_objects as go
import json
from data_models import DEFAULT_CREDITORS, DEFAULT_BANKS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Banking Sector Loss Distribution Model</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        #chart {
            width: 100%;
            height: 600px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Banking Sector Loss Distribution Model</h1>
        <div id="chart"></div>
    </div>
    <script>
        var graphs = {{plotly_json | safe}};
        Plotly.newPlot('chart', graphs.data, graphs.layout);
    </script>
</body>
</html>
'''

def create_visualization():
    try:
        logger.info("Creating visualization...")
        bank_data = DEFAULT_BANKS["Bank A"]
        total_assets = bank_data["total_assets"]

        # Create figure
        fig = go.Figure()

        # Add bars for each creditor
        for creditor, value in bank_data.items():
            if creditor != "total_assets":
                fig.add_trace(go.Bar(
                    name=creditor,
                    x=['Bank A'],
                    y=[value],
                    marker_color=DEFAULT_CREDITORS[creditor]['color'] if creditor in DEFAULT_CREDITORS else '#333',
                    text=f'€{value:,.0f}',
                    textposition='inside',
                ))

        # Update layout
        fig.update_layout(
            barmode='stack',
            height=600,
            title="Bank Value Distribution",
            yaxis_title="Amount (EUR)",
            showlegend=True,
            legend_title="Creditor Type",
        )

        logger.info("Visualization created successfully")
        return json.loads(fig.to_json())
    except Exception as e:
        logger.error(f"Error creating visualization: {str(e)}")
        raise

@app.route('/')
def home():
    try:
        logger.info("Handling home route request")
        plotly_json = create_visualization()
        return render_template_string(HTML_TEMPLATE, plotly_json=plotly_json)
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application...")
        app.run(host='0.0.0.0', port=8080, debug=False)
    except Exception as e:
        logger.error(f"Failed to start Flask application: {str(e)}")