from distutils.log import debug
from flask import Flask, render_template, request
from constructor import Index
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

i = Index(data_dir='test', output_dir='output')
i.parse()

@app.route('/first_query')
def first_query():
    return render_template('page1.html')


@app.route('/data', methods=['POST'])
def handle_data():
    if request.method == 'POST':

        query = request.form.get("query")
        results = i.ranker(str(query))
        df = results[['file_name', 'score']]
        return render_template('data2.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)

app.run(debug = True)