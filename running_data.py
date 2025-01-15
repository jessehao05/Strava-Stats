import pandas as pd

df_raw = pd.read_csv('activities_12_28_2024.csv')

# select relevant columns and rename for convenience
df_runs = df_raw[['Activity Date','Activity Name','Activity Type','Activity Description',
                  'Elapsed Time','Moving Time','Distance','Elevation Gain','Elevation Loss']]
df_runs = df_runs.rename(columns = {'Activity Date':'Date', 'Activity Name':'Name',
                                    'Activity Type':'Type','Activity Description':'Description'})

# convert km to miles and time into minutes
df_runs['Distance'] = df_runs['Distance'] * 0.621
df_runs['Elapsed Time'] = df_runs['Elapsed Time'] / 60
df_runs['Moving Time'] = df_runs['Moving Time'] / 60
df_runs['Pace'] = df_runs['Moving Time'] / df_runs['Distance']

print(df_runs.sort_values('Distance', ascending=False).head(20))