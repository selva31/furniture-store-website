from core import create_app

# Create Flask app from your factory
app = create_app()

# This is required by Vercel to handle serverless requests
def handler(request):
    return app(request.environ, start_response=lambda status, headers: (None, []))
