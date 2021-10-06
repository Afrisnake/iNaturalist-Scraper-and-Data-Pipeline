'''
    User specification of values for key variables used in the 'inaturalist_scraper.py' module.

    This is the 'control panel' of the application, allowing users to set the values of key variables
    These variables are imported into the 'inaturalist_scraper.py' script to control the scrape job

    place_id : int
        Numerical code representing the geographic region for the scrape job
        Examples: 6986 for South Africa, 7146 for Zimbabwe
        Find the correct code by executing a normal search on the iNaturalist 'Explore' page
        The code is contained in the url of the search (click on the url in the address bar)
        This scraper only supports a single place_id value per search

    taxon_id : int
        Numerical code representing the taxon for the scrape job
        Examples: 26036 for Class Reptilia (reptiles), 85553 for Suborder Serpentes (snakes)
        Find the correct code by executing a normal search on the iNaturalist 'Explore' page
        The code is contained in the url of the search (click on the url in the address bar)
        This scraper only supports a single taxon_id value per search

    start_page : int
        Specifies which page of the returned search results the scrape job will begin at
        A value of 1 is recommended (begin scraping at the first page of results)
        The application will not allow start_page values such that start_page*per_page > 10000

    per_page : int
        Specifies the number of observation records to be returned per page of search results
        A value of 100 is recommended

    db_name : str
        Specifies the name of the database into which records will be accessioned

    table_name : str 
        Specifies the name of the destination data table (within the db_name database) for storage of scraped records

'''

# Access numeric code by setting up a search on the iNaturalist 'Explore' page
# Scraper will only take single place_id values
place_id = 0000 # e.g. 6986 for South Africa, 7146 for Zimbabwe, 7143 for Swaziland

# Access numeric code by setting up a search on the iNaturalist 'Explore' page
# Scraper will only take single taxon_id values
taxon_id = 00000 # e.g. 26036 for Class Reptilia, 85553 for Suborder Serpentes

# Specify which starting page of search results to begin scraping at
start_page = 1

# Specify how many records to be returned per page of search results
per_page = 100

# Input name of the database to which scraped records will be piped
db_name = 'your_db_name_here'

# Specify name of the table within the db, in which records will be stored
table_name = 'your_table_name_here'
