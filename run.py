from app import create_app

app = create_app()

if __name__ == '__main__':
    # Start the Flask development server on port 5000 (debug=True for local checks)
    app.run(debug=True, host='0.0.0.0', port=5000)
