from flask import Flask, render_template
from config import DevConfig

app = Flask(__name__)
app.config.from_object(DevConfig)

@app.route('/')
def index():
    # return '<h1>hello world</h1>'
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
