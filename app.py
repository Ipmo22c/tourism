"""
Flask Web Application for Multi-Agent Tourism System
"""
from flask import Flask, render_template, request, jsonify
from agents.tourism_agent import TourismAgent
import logging

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Initialize the tourism agent
tourism_agent = TourismAgent()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/query', methods=['POST'])
def process_query():
    """
    API endpoint to process user queries
    
    Expected JSON:
    {
        "query": "user's query string"
    }
    
    Returns:
    {
        "response": "agent's response",
        "success": true/false
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "response": "Please provide a query in the request.",
                "success": False
            }), 400
        
        user_query = data['query'].strip()
        
        if not user_query:
            return jsonify({
                "response": "Query cannot be empty.",
                "success": False
            }), 400
        
        logger.info(f"Processing query: {user_query}")
        
        # Process the query using the tourism agent
        response = tourism_agent.process_query(user_query)
        
        return jsonify({
            "response": response,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return jsonify({
            "response": f"An error occurred while processing your query: {str(e)}",
            "success": False
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Tourism AI Agent"
    }), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

