import sqlite3
import requests
from bs4 import BeautifulSoup
import json
from secrets import plotly_username, plotly_key
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from math import log

CACHE_FNAME = 'imdb_cache.json'
global DBNAME
DBNAME = 'imdb_top250.sqlite'

def create_unique_ident(url):
    return url

def request_from_cached_data(request_url):
    unique_ident = create_unique_ident(request_url)

    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_data = cache_file.read()
        CACHE_DICT = json.loads(cache_data)
        cache_file.close()
    except:
        CACHE_DICT = {}

    if unique_ident in CACHE_DICT:
        print('Getting cached data....')
        return CACHE_DICT[unique_ident]
    else:
        print('Requesting new data....')
        resp = requests.get(request_url)
        CACHE_DICT[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICT)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICT[unique_ident]

def create_database():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    # Drop tables for development
    statement = '''
            DROP TABLE IF EXISTS 'Movies';
    '''
    cur.execute(statement)
    statement = '''
            DROP TABLE IF EXISTS 'Genre';
    '''
    cur.execute(statement)
    statement = '''
               DROP TABLE IF EXISTS 'Country';
       '''
    cur.execute(statement)
    statement = '''
               DROP TABLE IF EXISTS 'Language';
       '''
    cur.execute(statement)
    conn.commit()

    ## Create tables
    statement = '''
        CREATE TABLE 'Movies'(
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Titles' TEXT NOT NULL,
        'Ratings' FLOAT NOT NULL,
        'Director' TEXT NOT NULL,
        'Genre' INTEGER NOT NULL,
        'Country' INTEGER NOT NULL,
        'Language' INTEGER NOT NULL,
        'GrossUSA' INTEGER,
        'WorldwideGross' INTEGER
        )
    '''
    cur.execute(statement)

    statement = '''
        CREATE TABLE 'Genre'(
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'Name' TEXT NOT NULL
        )
    '''
    cur.execute(statement)

    statement = '''
            CREATE TABLE 'Country'(
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL
            )
    '''
    cur.execute(statement)

    statement = '''
            CREATE TABLE 'Language'(
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL
            )
    '''
    cur.execute(statement)

    conn.commit()
    conn.close()

def populate_ref_tables(table, lst):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    for i in lst:
        statement = '''
            INSERT INTO {}
            VALUES (?,?)
        '''
        statement = statement.format(table)
        cur.execute(statement, (None, i))

    conn.commit()
    conn.close()


def clean_gross_no(str):
    split_string = str.split()
    for s in split_string:
        if "$" in s:
            return_num = s
    return_num = ''.join(return_num[1:].split(','))
    return int(return_num)


def scrape_and_populate():
    ## Scrape top 250 page
    baseurl = "https://www.imdb.com"
    chart_url = "/chart/top"
    resp = request_from_cached_data(baseurl + chart_url)
    soup = BeautifulSoup(resp, 'html.parser')

    #print(soup.prettify())

    movie_list = soup.find(class_="lister-list")
    movie_items = movie_list.find_all('tr')

    data_dict = {}
    country_list = []
    genre_list = []
    language_list = []
    for i in movie_items:
        title_col = i.find(class_="titleColumn")
        title_link = title_col.find('a')
        title = title_link.text
        movie_url = title_link['href']
        rating = i.find(class_='ratingColumn').text.strip()
        rating = float(rating)

        ## Scrape individual movie page
        resp = request_from_cached_data(baseurl + movie_url)
        soup = BeautifulSoup(resp, 'html.parser')
        direct_div = soup.find(class_='credit_summary_item')
        director = direct_div.find('a').text

        genre_div = soup.find('h4', text='Genres:').parent
        genre = genre_div.find('a').text.strip()
        if genre not in genre_list:
            genre_list.append(genre)

        country_div = soup.find('h4', text='Country:').parent
        country = country_div.find('a').text.strip()
        if country not in country_list:
            country_list.append(country)

        language_div = soup.find('h4', text='Language:').parent
        language = language_div.find('a').text.strip()
        if language not in language_list:
            language_list.append(language)

        try:
            gross_usa_div = soup.find('h4', text='Gross USA:').parent
            gross_usa = gross_usa_div.text
            gross_usa = clean_gross_no(gross_usa)
            #print(gross_usa)
        except:
            gross_usa = None

        try:
            gross_world_div = soup.find('h4', text='Cumulative Worldwide Gross:').parent
            gross_world = gross_world_div.text
            gross_world = clean_gross_no(gross_world)
            #print(gross_world)
        except:
            gross_world = None

        data_dict[title] = {'rating': rating, 'director': director, 'genre': genre, 'language': language, 'country': country, 'gross_usa': gross_usa, 'gross_world': gross_world}
    # print(data_dict)
    
    
    ## Populate referenced tables
    populate_ref_tables('Country', country_list)
    populate_ref_tables('Language', language_list)
    populate_ref_tables('Genre', genre_list)

    ## Populate main data table
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    for movie in data_dict.items():
        statement = "SELECT Id FROM Genre WHERE Name='{}'".format(movie[1]['genre'])
        cur.execute(statement)
        genre_id = cur.fetchone()[0]

        statement = "SELECT Id FROM [Language] WHERE Name='{}'".format(movie[1]['language'])
        cur.execute(statement)
        language_id = cur.fetchone()[0]

        statement = "SELECT Id FROM Country WHERE Name='{}'".format(movie[1]['country'])
        cur.execute(statement)
        country_id = cur.fetchone()[0]

        statement = '''
            INSERT INTO Movies(Titles, Ratings, Director, Genre, Country, [Language], GrossUSA, WorldwideGross)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''

        insertion = (movie[0], movie[1]['rating'], movie[1]['director'], genre_id, language_id, country_id, movie[1]['gross_usa'], movie[1]['gross_world'])
        cur.execute(statement, insertion)

    conn.commit()
    conn.close()

    
def plot_language_gross():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    
    statement = '''
        SELECT Language.Name, AVG(Movies.GrossUSA), AVG(Movies.WorldwideGross)
        FROM Movies JOIN Language ON Movies.Language=Language.Id
        GROUP BY Language.Name
    '''
    cur.execute(statement)
    language_data = cur.fetchall()
    # print(language_data)
    
    gross_usa = []
    gross_world = []
    languages = []
    for lang in language_data:
        languages.append(lang[0])
        gross_usa.append(lang[1])
        gross_world.append(lang[2])
    
    trace1 = go.Bar(
        x=languages,
        y=gross_usa,
        text=gross_usa,
        textposition='auto',
        name='USA average gross'
    )
    trace2 = go.Bar(
        x=languages,
        y=gross_world,
        text=gross_world,
        textposition='auto',
        name='Worldwide average gross'
    )
    layout = go.Layout(
        title='Average gross by language in USA market / worldwide',
        barmode='group',
        xaxis=dict(title='Language'),
        yaxis=dict(title='Gross')
    )
    
    data = [trace1, trace2]
    fig = go.Figure(data=data, layout=layout)
    #py.plot(fig, validate=False, filename='imdb-language')
    div = plotly.offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=True)
    
    conn.close()
    return div

    
def plot_gross():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    
    statement = '''
        SELECT Titles, GrossUSA, WorldwideGross FROM Movies
    '''
    cur.execute(statement)
    gross_data = cur.fetchall()
    # print(language_data)
    
    gross_usa = []
    gross_world = []
    titles = []
    for gross in gross_data:
        if None not in gross:
            titles.append(gross[0])
            gross_usa.append(gross[1])
            gross_world.append(gross[2])
    
    trace = go.Scatter(
    x = gross_usa,
    y = gross_world,
    text = titles,
    mode = 'markers',
    marker = dict(
        size = 14,
        opacity = 0.5
    )
    )

    layout = dict(
        title='Gross by USA market and worldwide',
        xaxis=dict(title='Gross in USA', gridwidth= 2),
        yaxis=dict(title='Gross worldwide', gridwidth= 2)
    )
    
    data = [trace]
    fig = dict(data=data, layout=layout)
    div = plotly.offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=True)
    #py.plot(data, filename='imdb-gross')
    
    conn.close()
    return div


def plot_heatmap():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    
    statement = '''
        SELECT  m.GrossUSA, m.WorldwideGross, g.Name, c.Name
        FROM Movies AS m
            JOIN Genre AS g ON g.Id = m.Genre
                JOIN Country AS c ON c.Id = m.Country
        GROUP BY g.Name, c.Name
    '''
    cur.execute(statement)
    results = cur.fetchall()
    
    avg_gross=[]
    country=[]
    genre=[]
    for movie in results:
        if (movie.count(None) != 2):
            genre.append(movie[2])
            country.append(movie[3])
            if movie[0] == None:
                avg_gross.append(log(movie[1], 2))
            elif movie[1] == None:
                avg_gross.append(log(movie[0], 2))
            else:
                avg_gross.append(log(movie[0]+movie[1]/2, 2))
    
    trace = go.Scatter(
        x = country,
        y = genre,
        text=[country, genre],
        mode = 'markers',
        marker = dict(
            size=avg_gross,
            color='rgb(152,103,69)',
        )
    )
    
    layout = dict(
        title='Average gross in USA and World market by Country and Genre',
        xaxis=dict(title='Country', gridwidth= 2),
        yaxis=dict(title='Genre', gridwidth= 2)
    )
    
    data = [trace]
    
    fig = dict(data=data, layout=layout)
#    py.plot(fig, filename = 'test')
    div = plotly.offline.plot(fig, show_link=False, output_type="div", include_plotlyjs=True)
    
    conn.close()
    return div
    

def display_in_table(sortby='ratings', sortorder='DESC'):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    sort_param = 'm.Ratings'
    order_param = 'DESC'
    
    statement = '''
        SELECT m.Titles, m.Ratings, m.Director, g.Name, c.Name, l.Name, m.GrossUSA, m.WorldwideGross FROM Movies AS m
        LEFT JOIN Country AS c ON m.Country=c.Id
            LEFT JOIN Genre AS g ON m.Genre=g.Id
                LEFT JOIN [Language] AS l ON m.[Language]=l.Id
        ORDER BY {} {}
    '''
    if sortby == 'gross_usa':
        sort_param = 'm.GrossUSA'
    elif sortby == 'gross_world':
        sort_param = 'm.WorldwideGross'
    
    if sortorder == 'asc':
        order_param = 'ASC'
        
    cur.execute(statement.format(sort_param, order_param))
    movies = cur.fetchall()
    # print(movies)
    conn.close()
    return movies



# if __name__ == '__main__':
#    # create_database()
#    # scrape_and_populate()
#    # plotly.tools.set_credentials_file(username=plotly_username, api_key=plotly_key)
    