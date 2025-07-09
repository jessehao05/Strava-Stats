# Strava Info

Shows lifetime and yearly statistics for Strava Activities. I didn't have Strava Wrapped for past years, so I wanted to be able to see all of my stats summarized.

## Instructions using R/RStudio:

1. Request a .csv file of all Strava activities to your email: log onto Strava.com --> Settings --> My Account --> Download or Delete Your Account / Get Started (you don't actually have to delete your account) --> (2) Download Request / Request Your Archive
2. Add .csv file into working directory
3. Copy runs.Rmd and open in RStudio
4. Change file name in the read_csv() function to your file name (line 17)
5. Change years of analysis as needed (lines 81-84)
6. Knit to HTML/PDF

## Stats:

Tables:

- Table with lifetime number of activities, distance, hours, and elevation
- Table with number of activities, distance, hours, and elevation for each year

Graphs:

- Histogram showing total runs at each distance
- Histogram showing total runs at each pace
- Bar chart showing number of runs (lifetime) in each month
- Pie chart showing number of runs in at each distance class (5 classes: <2, 2-4, 4-6, 6-8, and >8 miles)

To-Do:

- README
- Update Instructions (note: my activities start in 2021)
- Metric version
- Formatting (Headers, horizontal lines?)
- Rounding in summary tables
- Possibly look at splitting by year + grouping by month
- (Python)

- instruction line (How to use: upload your Strava data .csv file)
- add FAQ redirect with dropdown menu (includes: Don't have enough data from my own Strava but want to see how the website works?, Unsure how to download your Strava data?, [forgot something here])
- graph styling: labels, pie chart
- rewrite with functions
