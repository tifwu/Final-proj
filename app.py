import Final_proj as proj
from flask import Flask, render_template, url_for, request
from flask import send_from_directory

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        sortby = request.form['sortby']
        sortorder = request.form['sortorder']
        searchBy = request.form['searchBy']
        searchTitle = request.form['searchTitle']
        data = proj.display_in_table(sortby,sortorder, searchBy, searchTitle)
    else:
        data = proj.display_in_table()
    return render_template('index.html', movies=data)

@app.route('/language-gross')
def language_gross():
    return render_template('plot.html', div=lang_div)

@app.route('/gross')
def gross():
    return render_template('plot.html', div=gross_div)

@app.route('/heatmap')
def heatmap():
    return render_template('plot.html', div=heat_div)
    

if __name__ == '__main__':
    lang_div = proj.plot_language_gross()
    gross_div = proj.plot_gross()
    heat_div = proj.plot_heatmap()
    app.run(debug=True)