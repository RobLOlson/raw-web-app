import os
from flask import Flask

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

@app.route('/')
def hello():
    return f"Hello World!<br>{os.environ['APP_SETTINGS']}"


@app.route('/<name>')
def hello_name(name):
    return f"hello {name}"


if __name__ == '__main__':
    print(os.environ['APP_SETTINGS'])
    app.run()
