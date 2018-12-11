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
```
plotly_username = <your username>
plotly_key = <your api key>
```

## Program Structure
### create_database()
This function set up the sqlite database, ***imdb_top250_sqlite***, that is used in the program. It will first drop the duplicated tables in the database, and then creates 1 main data table Movies, and 3 referenced tables: Language, Genre and Country

### scrape_and_populate_ref()
This function organize data from IMDb Top 250 charts. It will scrape data from IMDb website or request from cache if available. The program organize the referenced information in lists and populate the referenced tables, then returns a list of Movie instances that will be used in populate_main_table() function to populate the main data table used in this project.

### populate_main_table()
This function populates the main data table of all 250 movies.

### Data presentation functions
There are mainly 4 functions for data presentation:
- plot_language_gross()
- plot_gross()
- plot_heatmap()
- display_in_table()
The former three functions plot the data requested from the database into different charts, and the last function takes input from users to filter the data displayed in the table.

### class Movie():
There is one class defined in this program to stored the information as attributes in each instance.


## User Guide
1. To successfully run the program, please make sure you have successfully installed the modules specified in the requirements.txt file
2. Initialize the database by running **Final_proj.py**
3. Run **app.py** to start the flask app, and open the app with your browser


