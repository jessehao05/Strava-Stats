from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt

import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def upload_page():
    return render_template('index.html')

@app.route('/example')
def example_page():
    return render_template('example.html')

@app.route('/instructions')
def instructions_page():
    return render_template('instructions.html')

@app.route('/process', methods = ['POST'])
def process_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    df = pd.read_csv(filepath)

    summary = df.describe().to_html(classes='data')

    # pandas/matplot processing
    
    # 1. cleaning
    df_runs = df[['Activity Date','Activity Name','Activity Type','Activity Description',
                  'Elapsed Time','Moving Time','Distance','Elevation Gain','Elevation Loss']]
    df_runs = df_runs.rename(columns = {'Activity Date':'Date', 'Activity Name':'Name',
                                    'Activity Type':'Type','Activity Description':'Description'})
    
    cleaned_table_html = df_runs.to_html(classes='data', index=False)

    # 2. summary table
    total_summary = df_runs[['Distance','Moving Time','Elevation Gain']].agg(['sum']) # summing columns, TO-DO: ignore N/A values in elevation
    total_summary['Activities'] = len(df_runs) # adding activities column as the total number of rows
    total_summary = total_summary[['Activities','Distance','Moving Time','Elevation Gain']] # rearrange columns
    total_summary['Moving Time'] = total_summary['Moving Time'] / 60

    total_summary_html = total_summary.to_html(index = False)

    
    # 3. distance histogram
    dist_hist, dist_hist_ax = plt.subplots()

    dist_hist_ax.hist(df_runs['Distance'], 
            bins = range(int(df_runs['Distance'].min()), int(df_runs['Distance'].max()) + 2), 
            color = 'lightblue', 
            edgecolor = 'black')

    dist_hist_ax.set_xlabel('Distance (miles)')
    dist_hist_ax.set_ylabel('Number of runs')
    dist_hist_ax.set_title('Number of runs at each distance')

    img_path = os.path.join('static', 'dist_hist.png')
    dist_hist.savefig(img_path)

    # send data to jinja2/flask
    # q: can you add classes/ID's to html tables you pass to jinja? (for styling)
    return render_template('results.html', cleaned_table = cleaned_table_html, total_summary = total_summary_html, hist_path = img_path)


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok = True)
    app.run(debug = True)