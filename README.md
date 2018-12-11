# SI507 Final Project: IMDb Top 250 Explorer

## Data Source
### IMDb Charts of Top 250 movies
- Source: https://www.imdb.com/chart/top
- This project scraped the charts and the information page of all 250 movies listed in this chart. No credentials are needed for the scraping

### Plotly
- This project uses Plotly for data presentation
- An API key is required to successfully render the plot. Please follow the steps below to acquire and provide the program the key.
###### Getting an API key for Plotly
1. Sign up on Plotly: https://plot.ly/
2. Pip install plotly if it is not already on your machine
3. Create a **secrets.py** file and include the following information
'''
plotly_username = <your username>
plotly_key = <your api key>
'''
