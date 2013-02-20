import os

from waitress import serve

from {{ project_name }} import wsgi


PORT = int(os.environ.get("PORT", 5000))


if __name__ == "__main__":
    serve(wsgi.application,
        port = PORT,
    )