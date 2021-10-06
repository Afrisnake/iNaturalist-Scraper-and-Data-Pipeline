page_observations = [
    (509046, '1988-01-02', 'Dendroaspis', 'polylepis', '', '[-16.533578, 28.795252]', -16.533578, 28.795252, 'Kariba', False, 'research'),
    (509039, '1989-01-05', 'Telescopus', 'semiannulatus', '', '[-15.831677, 29.142909]', -15.831677, 29.142909, 'Mana Pools National Park', False, 'research'),
    (509030, '1986-07-17', 'Psammophis', 'subtaeniatus', '', '[-18.161659, 28.211067]', -18.161659, 28.211067, 'Sengwa Wildlife Research Area', False, 'research'),
    (509028, '1980-09-01', 'Python', 'natalensis', '', '[-17.75755, 27.86028]', -17.75755, 27.86028, 'Chizarira National Park', False, 'research'),
    (505270, '1986-07-25', 'Bitis', 'arietans', '', '[-18.160797, 28.209972]', -18.160797, 28.209972, 'Sengwa Wildlife Research Area', False, 'research'),
    (505236, '1979-04-22', 'Dispholidus', 'typus', '', '[-16.81724, 28.449483]', -16.81724, 28.449483, 'Matusadona National Park', False, 'research'),
    (421787, '1979-12-19', 'Elapsoidea', 'boulengeri', '', '[-16.815695, 28.446586]', -16.815695, 28.446586, 'Matusadona National Park', False, 'needs_id'),
    (414645, '1988-07-13', 'Lycophidion', 'capense', '', '[-15.836848, 29.146428]', -15.836848, 29.146428, 'Mana Pools National Park', False, 'research'),
    (413589, '1988-05-27', 'Dendroaspis', 'polylepis', '', '[-15.832151, 29.143027]', -15.832151, 29.143027, 'Mana Pools National Park', False, 'research'),
    (412962, '1986-07-06', 'Elapsoidea', 'boulengeri', '', '[-18.142498, 28.208942]', -18.142498, 28.208942, 'Sengwa Wildlife Research Area', False, 'research'),
    (295298, '2012-12-11', 'Naja', 'annulifera', '', '[-16.180798, 30.142407]', -16.180798, 30.142407, 'Masoka', False, 'research'),
    (295296, '2012-12-12', 'Hemirhagerrhis', 'nototaenia', '', '[-16.243868, 30.234772]', -16.243868, 30.234772, 'Murara', False, 'research'),
    (205852, '2007-02-17', 'Philothamnus', 'angolensis', '', '[-18.1858941505, 32.8923583031]', -18.1858941505, 32.8923583031, 'Gairezi River, Zimbabwe', False, 'research'),
    (169863, '2012-12-25', 'Dispholidus', 'typus', '', '[-19.802221, 32.870743]', -19.802221, 32.870743, 'Chimanimani, Manicaland, Zimbabwe', False, 'research'),
    (169856, '2012-12-30', 'Duberria', '', '', '[-19.8, 32.8666667]', -19.8, 32.8666667, 'Chimanimani, Zimbabwe', False, 'needs_id')
]

test = [
    (000000, '2021-01-01', 'Genus', 'species', '', '[-16, 28]', -16, 28, 'Somewhere', False, 'research')
]


import sqlite3
import os
import sys
import logging
db_name = 'test_database'
table_name = 'test_table'

# Logging initialisation and configuration
logging.basicConfig(filename = 'iNat_scraper.log', level=logging.INFO, format='%(asctime)s - %(message)s')


# Create a pipeline class to control database accession of scraped records
class iNatPipeline():

    '''
        Class representing sqlite3 data pipeline.

        Creates a directory in which the database will be located
        Creates and connects to the db
        Creates a cursor for manipulation of the db

        ...
            
        Attributes
        ----------
        db_name : str
            Specifies the name of the database (default is the outside variable 'db_name')
        destination : str, automatic
            Specifies the full path to the db
        con : connection, automatic
            Establishes a pipeline to the db
        cur : cursor, automatic
            Creates a cursor for manipulation of the db

        Methods
        ----------
        create_table(table_name)
            Creates a named data storage table in the db, with correct columns
            Default table name is the outside variable 'table_name'
            Terminates the application if table cannot be created correctly
        pipe_to_db(table_name, page_observations)
            Inserts scraped data into a database table
            Default table is the outside variable 'table_name'
            Default data is the outside variable 'page_observations'
            Detects and ignores duplicate data when piping to the db table

    '''

    logging.info('\n\n--------------------\n\nA new instance of the iNatPipeline class has been created\n')


    # Create a directory 'iNaturalist_data' in which database will be created
    db_dir = 'iNaturalist_data'

    if not os.path.exists(db_dir):
        os.mkdir(db_dir)


    def __init__(self, db_name=db_name):

        '''
            Constructs all the necessary attributes for the iNatPipeline object.

            Parameters
            ----------
            db_name : str
                Specifies the name of the database (default is the outside variable 'db_name')
            destination : str, automatic
                Specifies the full path to the db
            con : connection, automatic
                Establishes a pipeline to the db
            cur : cursor, automatic
                Creates a cursor for manipulation of the db

        '''

        self.db_name = db_name
        self.destination = f"{os.path.join((os.path.realpath(os.getcwd())), 'iNaturalist_data', self.db_name)}.db"
        self.con = sqlite3.connect(self.destination)
        self.cur = self.con.cursor()


    # Create a named db table into which data can be inserted
    def create_table(self, table_name=table_name):

        '''
            Creates a named data storage table in the db, with correct columns.
            
            Terminates the application if table cannot be created correctly
            
            Parameters
            ----------
            table_name : str
                Name of the table (default is the outside variable 'table_name')
        
        '''

        try:
            self.cur.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}(
                id INTEGER PRIMARY KEY,
                date TEXT,
                genus TEXT,
                species TEXT,
                subspecies TEXT,
                coords TEXT,
                lat REAL,
                long REAL,
                locality TEXT,
                introduced BOOLEAN,
                qual_grade TEXT)'''
            )
            print(f"Table '{table_name}' successfully created in sqlite3 '{self.db_name}' database")
            logging.info(f"Table '{table_name}' successfully created in sqlite3 '{self.db_name}' database")
        except:
            print('Error encountered while creating table')
            logging.critical('Error encountered while creating table. The application has been terminated', exc_info=True)
            sys.exit('Database table cannot be created. The application has been terminated')


    # Sends scraped records from each page to a data table in the db
    def pipe_to_db(self, table_name=table_name, page_observations=page_observations):

        '''
            Inserts scraped data into a db table.
            
            Detects and ignores duplicate data when piping to the db table
            
            Parameters
            ----------
            table_name : str
                Name of the destination table (default is the outside variable 'table_name')
            page_observations : list
                List of tuples, each containing data from a single iNaturalist record
                Data must correspond exactly with columns of the destination table
                Default name for data variable is the outside variable 'page_observations' 
        
        '''

        try:
            self.cur.executemany(f'''INSERT OR IGNORE INTO {table_name} VALUES (?,?,?,?,?,?,?,?,?,?,?)''', page_observations)
            self.con.commit()
            print(f"{len(page_observations)} records successfully written to table '{table_name}' in sqlite3 '{self.db_name}' database")
            logging.info(f"{len(page_observations)} records successfully written to table '{table_name}' in sqlite3 '{self.db_name}' database")
        except:
            print('Error encountered during pipeline operations')
            logging.error('Error encountered during pipeline operations', exc_info=True)


# For testing purposes
if __name__ == "__main__":

    db = iNatPipeline()
    db.create_table()
    db.create_table('new')
    db.pipe_to_db()
    db.pipe_to_db('new',test)

    db = iNatPipeline('snakes')
    db.create_table()
    db.create_table('new')
    db.pipe_to_db()
    db.pipe_to_db('new',test)