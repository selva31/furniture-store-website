from app import create_app


# Create the app instance using the factory function
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)  # Runs in debug mode for easier development
