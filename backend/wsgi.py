import serverless_wsgi

from app import create_app

app = create_app()


def lambda_handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)
