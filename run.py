"""
Entry point for the BusFlow Flask application.

This script initializes and runs the Flask development server.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

