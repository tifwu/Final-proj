import Final_proj as proj
from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/language-gross')
def language_gross():
    div = proj.plot_language_gross()
    return '<h2><a href="/">< Back to homepage</a></h2>' + div

@app.route('/gross')
def gross():
    div = proj.plot_gross()
    return '<h2><a href="/">< Back to homepage</a></h2>' + div

if __name__ == '__main__':
    print('starting flask...', app.name)
    app.run(debug=True)