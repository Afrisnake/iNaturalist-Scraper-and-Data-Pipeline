# iNaturalist-Scraper-and-Data-Pipeline
A Python application for Windows that scrapes biodiversity observation records from the iNaturalist website and pipes scraped data to a destination table in an sqlite3 database

## Introduction
This modular web-scraping application scrapes behind an iNaturalist login, extracting key variables from each observation record (see below) and transferring these data via a data pipeline to a destination table in a sqlite3 database. The following variables are extracted (blank if data missing):

            id (int):           unique iNaturalist primary key
            date (str):         date on which observation was made (yyyy-mm-dd)
            genus (str):        genus name for organism
            species (str):      species name for organism
            subspecies (str):   subspecies name for organism
            coords (list):      locality coordinates in decimal degrees [lat, long]
            lat (float):        locality latitude in decimal degrees
            long (float):       locality longitude in decimal degrees
            locality (str):     iNaturalist 'best guess' of locality based on coords
            introduced (bool):  indigenous to locality (False, 0) or introduced to locality (True, 1)
            qual_grade (str):   identification verified ('research') or yet to be verified ('needs_id')  

## Implementation

This web-scraper utilizes the hidden API's by which iNaturalist mediates queries to its records database. It comprises 5 modules (see below) as well as a mandatory **__ init __.py** file. All important information about the classes, methods, functions and variables defined in these modules is included in docstrings.


- **inat_creds.py**<br/>
This file must be edited by the user to include a valid iNaturalist *username* and *password*
- **inat_search_params.py**<br/>
This editable file is the 'control panel' of the application. Users set the values of key variables, which are imported into the main script to control the scrape job. The following variables can be manipulated:

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

- **inat_create_db.py**<br/>
This module builds the database into which data will be accessioned, and the pipeline which mediates data transfer.<br/><br/>
<pre>       - Creates an 'iNaturalist_data' folder in the working directory, in which the database will be located<br/></pre>
            - Creates and connects to the database<br/>
            - Creates a named data storage table in the database, as a destination for scraped data<br/>
            - Inserts scraped data into the storage table<br/>
            - Detects and ignores duplicate data when piping to the table
- **inat_scrape_longstrings.py**<br/>
Contains long 'print' and 'logging' messages for the main script. These messages reduce readability of the code, so are imported to the main script from this module.






### Scraping Procedure
- Ensure that Python and the prerequisite libraies are installed on your machine (see 'Dependencies')
- All five module files and the **__ init __.py** file must be placed in the same folder
- Edit the 'inat_creds.py'and 'inat_search_params.py' files appropriately
- To run the scraper, execute the main script




Logging
Inherent limit of 10000, and how it's overcome
 


## Dependencies
Python 3.8<br/>
Requests library (pip install requests)<br/>
Beautiful Soup 4 libray (pip install bs4)

## Contact
Please feel free to contact me (Chris Kelly) at the following email:<br/>
<img src="https://github.com/Afrisnake/AFRISNAKE.github.io/blob/master/images/cmrkelly_gmail_address.jpg" alt="email" width="180" height="36" />


