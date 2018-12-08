from Final_proj import *
import unittest

class TestDatabase(unittest.TestCase):
    
    def test_movies_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        
        sql = 'SELECT Titles FROM Movies'
        cur.execute(sql)
        results = cur.fetchall()
        self.assertEqual(len(results), 250)
        self.assertIn(('The Shawshank Redemption', ), results)
        
        sql = 'SELECT Genre.Name FROM Movies JOIN Genre ON Genre.Id=Movies.Genre'
        cur.execute(sql)
        results = cur.fetchall()
        self.assertIn(('Drama',), results)
        
        
        
        conn.close()
        
    def test_country_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        
        sql = 'SELECT Name FROM Country'
        cur.execute(sql)
        results = cur.fetchall()
        self.assertGreater(len(results), 0)
        self.assertIn(('USA', ), results)
        
        conn.close()
    
    def test_language_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        
        sql = 'SELECT Name FROM Language'
        cur.execute(sql)
        results = cur.fetchall()
        self.assertGreater(len(results), 0)
        self.assertIn(('English', ), results)
        
        conn.close()
        
    def test_genre_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        
        sql = 'SELECT Name FROM Genre'
        cur.execute(sql)
        results = cur.fetchall()
        self.assertGreater(len(results), 0)
        self.assertIn(('Drama', ), results)
        
        conn.close()
        
    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        
        sql = '''
            SELECT Genre.Name
            FROM Movies
                JOIN Genre ON Genre.Id = Movies.Genre
            WHERE Movies.Titles = 'Inception'
        '''
        cur.execute(sql)
        result = cur.fetchone()
        self.assertEqual(result[0], 'Action')
        
        sql = '''
            SELECT Language.Name
            FROM Movies
                JOIN Language ON Language.Id = Movies.Language
            WHERE Movies.Titles = 'The Godfather'
        '''
        cur.execute(sql)
        result = cur.fetchone()
        self.assertEqual(result[0], 'English')
        
        sql = '''
            SELECT Country.Name
            FROM Movies
                JOIN Country ON Country.Id = Movies.Country
            WHERE Movies.Titles = "Schindler's List"
        '''
        cur.execute(sql)
        result = cur.fetchone()
        self.assertEqual(result[0], 'USA')
        
        conn.close()

        
class TestCleanMethods(unittest.TestCase):
    def test_clean_gross_no(self):
        num = clean_gross_no('$123,456,789')
        self.assertEqual(num, 123456789)

        
class TestMapping(unittest.TestCase):
    def test_language_gross(self):
        try:
            plot_language_gross()
            plot_gross()
        except:
            self.fail()
            
    def test_display_table(self):
        movies = display_in_table()
        self.assertEqual(len(movies), 250)
        
        
    def test_heat_map(self):
        pass

        
if __name__ == '__main__':
    unittest.main()