from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import plotly.express as px
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
    df_runs['Distance'] = df_runs['Distance'] * 0.621
    df_runs['Elapsed Time'] = df_runs['Elapsed Time'] / 60
    df_runs['Moving Time'] = df_runs['Moving Time'] / 60
    df_runs['Pace'] = df_runs['Moving Time'] / df_runs['Distance']
    df_dates = df_runs.copy()

    month_arr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    df_dates['Year'] = df_dates['Date'].apply(
        lambda x: 2021 if '2021' in x else
            2022 if '2022' in x else
            2023 if '2023' in x else
            2024 if '2024' in x else None
    )

    def find_month(x):
        for month in month_arr:
            if month in x:
                return month
        return None

    df_dates['Month'] = df_dates['Date'].apply(find_month)

    cols = ['Date', 'Year', 'Month'] + [col for col in df_dates.columns if col not in ['Date', 'Year', 'Month']]
    df_dates = df_dates[cols]

    cleaned_table_html = df_dates.to_html(classes='stats-table', index=False)

    # 2. summary table
    total_summary = df_runs[['Distance','Moving Time','Elevation Gain']].agg(['sum']) # summing columns, TO-DO: ignore N/A values in elevation
    total_summary['Activities'] = len(df_runs) # adding activities column as the total number of rows
    total_summary = total_summary[['Activities','Distance','Moving Time','Elevation Gain']] # rearrange columns
    total_summary['Moving Time'] = total_summary['Moving Time'] / 60
    total_summary = total_summary.round(2)

    total_summary_html = total_summary.to_html(classes='stats-table', index = False)

    # 3. by year table
    yearly_summary = df_dates.groupby('Year').agg({
        'Distance': 'sum',
        'Moving Time': 'sum',
        'Elevation Gain': 'sum'
    })
    yearly_summary['Activities'] = df_dates.groupby('Year').size()
    yearly_summary = yearly_summary[['Activities', 'Distance', 'Moving Time', 'Elevation Gain']]
    yearly_summary['Moving Time'] = yearly_summary['Moving Time'] / 60
    yearly_summary = yearly_summary.reset_index()
    yearly_summary = yearly_summary.round(2)
    
    yearly_summary_html = yearly_summary.to_html(classes='stats-table', index = False)

    
    # 4. distance histogram
    dist_hist = px.histogram(df_dates, x="Distance", title="Number of Runs at Each Distance")
    dist_hist_html = dist_hist.to_html(full_html=False)

    # 5. pace histogram
    pace_hist = px.histogram(df_dates, x="Pace", title="Number of Runs at Each Pace")
    pace_hist_html = pace_hist.to_html(full_html=False)

    # 6. monthly run distribution
    month_hist = px.histogram(
        df_dates,
        x='Month',
        nbins=12,
        labels={'Month': 'Month', 'count': 'Number of runs'},
        title='Number of runs each month across all years'
    )
    # month_hist.update_traces(marker_color='lightblue', marker_line_color='black', marker_line_width=1)
    month_hist_html = month_hist.to_html(full_html=False)

    # 7. distance pie chart
    df_dates['Distance Bracket'] = df_dates['Distance'].apply(
        lambda x: '<2' if x < 2 else
                '2-4' if x <= 4 else 
                '4-6' if x <= 6 else
                '6-8' if x <= 8 else
                '>8'
    )   
    bracket_counts = df_dates['Distance Bracket'].value_counts().sort_index()

    dist_pie = px.pie(
        names = bracket_counts.index,
        values = bracket_counts.values,
        title = 'Run Counts by Distance Bracket (miles)'
    )

    dist_pie_html = dist_pie.to_html(full_html = False)

    # end: delete file from local
    os.remove(filepath)

    # send data to jinja2/flask
    return render_template('results.html', 
                           total_summary = total_summary_html, 
                           annual_summary = yearly_summary_html,
                           distance_hist = dist_hist_html,
                           pace_distrib = pace_hist_html,
                           month_distrib = month_hist_html,
                           pie = dist_pie_html)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok = True)
    app.run(debug = True)