from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import plotly.express as px
import os
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 
month_arr = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

@app.route('/')
def upload_page():
    return render_template('index.html')

@app.route('/FAQ')
def FAQ_page():
    return render_template('FAQ.html')

@app.route('/process', methods = ['POST'])
def process_file():

    action = request.form.get('action')
    success, result = verify_file(action, request)

    if not success: 
        return result
    
    df = result

    # 1. cleaning
    df_clean = clean_data(df, month_arr)

    # 2. summary table
    total_summary = generate_summary_table(df_clean)
    total_summary_html = total_summary.to_html(classes='stats-table', index = False)

    # 3. by year table
    yearly_summary = generate_yearly_summary(df_clean)
    yearly_summary_html = yearly_summary.to_html(classes='stats-table', index = False)

    # 4. distance histogram
    dist_hist = generate_distance_histogram(df_clean)
    dist_hist_html = dist_hist.to_html(full_html=False)

    # 5. pace histogram
    pace_hist = generate_pace_histogram(df_clean)
    pace_hist_html = pace_hist.to_html(full_html=False)

    # 6. monthly run distribution
    month_hist = generate_monthly_distrib(df_clean, month_arr)
    month_hist_html = month_hist.to_html(full_html=False)

    # 7. distance pie chart
    dist_pie = generate_pie(df_clean)
    dist_pie_html = dist_pie.to_html(full_html = False)

    # send data to jinja2/flask
    return render_template('results.html', 
                           total_summary = total_summary_html, 
                           annual_summary = yearly_summary_html,
                           distance_hist = dist_hist_html,
                           pace_distrib = pace_hist_html,
                           month_distrib = month_hist_html,
                           pie = dist_pie_html)

def verify_file(action, request):
    if action == 'default':
        filepath = 'static/example.csv'
        df = pd.read_csv('static/example.csv')
        return True, df

    elif action == 'upload': 
        if 'file' not in request.files:
            return False, render_template('index.html', error = 'No file part in request')

        file = request.files['file']
        if file.filename == '':
            return False, render_template('index.html', error = 'No selected file')
        
        if not file.filename.endswith('csv'):
            return False, render_template('index.html', error = 'Only .csv files allowed')
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
                file.save(tmp.name)
                tmp_path = tmp.name

            df = pd.read_csv(tmp_path)

        except Exception as e:
            return False, render_template('index.html', error = 'Error processing file')  

        finally:
            os.remove(tmp_path)  

        REQUIRED_COLS = {'Activity Date','Activity Name','Activity Type','Activity Description',
                  'Elapsed Time','Moving Time','Distance','Elevation Gain','Elevation Loss'}
        if not REQUIRED_COLS.issubset(df.columns):
            print('i was here')
            return False, render_template('index.html', error = 'Not a file from Strava - try again')
        
        print(' was here 2')
        return True, df
        
    else:
        return False, render_template('index.html', error = 'Something went wrong - try again')

def clean_data(df, month_arr):
    df_runs = df[['Activity Date','Activity Name','Activity Type','Activity Description',
                  'Elapsed Time','Moving Time','Distance','Elevation Gain','Elevation Loss']]
    df_runs = df_runs.rename(columns = {'Activity Date':'Date', 'Activity Name':'Name',
                                    'Activity Type':'Type','Activity Description':'Description'})
    df_runs['Distance'] = df_runs['Distance'] * 0.621 # km -> mi
    df_runs['Elapsed Time'] = df_runs['Elapsed Time'] / 60 # s -> min
    df_runs['Moving Time'] = df_runs['Moving Time'] / 60 # s -> min
    df_runs['Pace'] = df_runs['Moving Time'] / df_runs['Distance'] # min/mi
    df_runs['Elevation Gain'] = df_runs['Elevation Gain'] * 3.28 # m -> ft
    df_dates = df_runs.copy()

    # NOTE: change starting/ending value depending on earliest/latest activity
    df_dates['Year'] = df_dates['Date'].apply(
        lambda x: 2021 if '2021' in x else
            2022 if '2022' in x else
            2023 if '2023' in x else
            2024 if '2024' in x else 
            2025 if '2025' in x else None
    )

    def find_month(x):
        for month in month_arr:
            if month in x:
                return month
        return None

    df_dates['Month'] = df_dates['Date'].apply(find_month)

    cols = ['Date', 'Year', 'Month'] + [col for col in df_dates.columns if col not in ['Date', 'Year', 'Month']]
    df_dates = df_dates[cols]

    return df_dates

def generate_summary_table(df):
    total_summary = df[['Distance','Moving Time','Elevation Gain']].agg(['sum']) # summing columns, TO-DO: ignore N/A values in elevation
    total_summary['Activities'] = len(df) # adding activities column as the total number of rows
    total_summary = total_summary[['Activities','Distance','Moving Time','Elevation Gain']] # rearrange columns
    total_summary['Moving Time'] = total_summary['Moving Time'] / 60
    total_summary = total_summary.round(2)
    total_summary = total_summary.rename(columns = {'Distance': 'Distance (mi)', 'Moving Time': 'Moving Time (hr)', 'Elevation Gain': 'Elevation Gain (ft)'})

    return total_summary

def generate_yearly_summary(df):
    yearly_summary = df.groupby('Year').agg({
        'Distance': 'sum',
        'Moving Time': 'sum',
        'Elevation Gain': 'sum'
    })
    yearly_summary['Activities'] = df.groupby('Year').size()
    yearly_summary = yearly_summary[['Activities', 'Distance', 'Moving Time', 'Elevation Gain']]
    yearly_summary['Moving Time'] = yearly_summary['Moving Time'] / 60
    yearly_summary = yearly_summary.reset_index()
    yearly_summary = yearly_summary.round(2)
    yearly_summary = yearly_summary.rename(columns = {'Distance': 'Distance (mi)', 'Moving Time': 'Moving Time (hr)', 'Elevation Gain': 'Elevation Gain (ft)'})
    
    return yearly_summary

def generate_distance_histogram(df):
    dist_hist = px.histogram(df, 
        x = "Distance", 
        title = "Number of Runs at Each Distance", 
        nbins = 12, 
        template = 'seaborn',
        labels = {'Distance': 'Distance (miles)', 'count' : 'Number of runs'})
    dist_hist.update_traces(marker_line_width = 1, marker_line_color = 'white')

    return dist_hist

def generate_pace_histogram(df):
    pace_hist = px.histogram(df, 
        x = "Pace", 
        title = "Number of Runs at Each Pace", 
        template = "seaborn",
        labels = {'Pace': 'Pace (min/mile)'})
    pace_hist.update_traces(marker_line_width = 1, marker_line_color = 'white')
        
    return pace_hist

def generate_monthly_distrib(df, month_arr):

    df['Month'] = pd.Categorical(df['Month'], categories = month_arr, ordered = True)

    month_hist = px.histogram(df,
        x = 'Month',
        nbins = 12,
        labels = {'Month': 'Month', 'count': 'Number of runs'},
        title = 'Number of Runs by Month',
        template = 'seaborn')
    
    month_hist.update_traces(marker_line_width = 1, marker_line_color = 'white')
    month_hist.update_xaxes(categoryorder = 'array', categoryarray = month_arr)

    return month_hist

def generate_pie(df):
    df['Distance Bracket'] = df['Distance'].apply(
        lambda x: '<2' if x < 2 else
                '2-4' if x <= 4 else 
                '4-6' if x <= 6 else
                '6-8' if x <= 8 else
                '>8'
    )   
    bracket_counts = df['Distance Bracket'].value_counts().sort_index()

    dist_pie = px.pie(
        names = bracket_counts.index,
        values = bracket_counts.values,
        title = 'Mileage Distribution',
        template = 'seaborn'
    )
    dist_pie.update_traces(legendgrouptitle_text = 'Distance Bracket (miles)')

    return dist_pie

if __name__ == '__main__':
    app.run(debug = True)