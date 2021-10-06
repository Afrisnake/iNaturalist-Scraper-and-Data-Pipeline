# iNaturalist-Scraper-and-Data-Pipeline
A Python application for Windows that scrapes biodiversity observation records from the iNaturalist website and pipes scraped data to a destination table in an sqlite3 database

## Introduction
This modular web-scraping application scrapes behind an iNaturalist login, extracting key variables from each observation record (see below) and transferring these data via a data pipeline to a destination table in an sqlite3 database. The following variables are extracted (blank if data missing):
<pre>
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
</pre>

## Implementation
This web-scraper utilizes the hidden APIs by which iNaturalist mediates queries to its records database. It comprises 5 modules (see below) as well as a mandatory **__ init __.py** file. All important information about the classes, methods, functions and variables defined in these modules is included in docstrings.

- **inat_creds.py**<br/>
This file must be edited by the user to include a valid iNaturalist *username* and *password*.

- **inat_search_params.py**<br/>
This editable file is the 'control panel' of the application. User sets the values of key variables, which are imported into the main script to control the scrape job. The following variables can be manipulated:
<pre>
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
</pre>

- **inat_create_db.py**<br/>
This module builds the database into which data will be accessioned, and the pipeline which mediates data transfer. Main actions are as follows:<br/>
<pre>
      Creates an 'iNaturalist_data' folder in the working directory, in which the database will be located
      Creates and connects to the database 
      Creates a named data storage table in the database, as a destination for scraped data
      Inserts scraped data into the storage table
      Detects and ignores duplicate data when piping to the table
</pre>

- **inat_scrape_longstrings.py**<br/>
Contains long 'print' and 'logging' messages for the main script. These messages reduce readability of the code, so are imported to the main script from this module.

- **inaturalist_scraper.py**<br/>
This is the main script, which implements a full scrape job based on parameters in the 'inat_search_params.py' module. See docstrings for a detailed description of the classes, methods and functions defined in this module. Note the following:
<pre>
      iNaturalist has a limit of start_page*per_page = 10000 for data retrieval via the API. The code loops through pages of
      observations up to this limit, after which the date of the last observation extracted prior to the limit being reached is
      set as the new upper bound (oldest date) for the next round of querying filtered by date. This allows scraping to continue
      into the next set of records.
      
      If the scrape job terminates unexpectedly, it can be restarted at the last page that was processed prior to termination.
      The user edits the 'inat_search_params.py' file, setting the 'start_page' value to the page number at which the scrape ended.
      If this results in start_page*per_page > 10000, the date of the last observation prior to termination is retrieved from the
      'current_oldest_date.txt' file and set as the upper bound (oldest date) for a new round of querying filtered by date.
      Scraping then begins where it left off, at page 1 of this new filtered search.
      
      In a fresh scrape, the user may enter a value for the 'start_page' variable such that start_page*per_page > 10000.
      This application does not have functionality to support such a search, and the user is instructed to enter a lower value
      for 'start_page'. 
</pre>

### Scraping Procedure
- Ensure that Python and the prerequisite libraries are installed on your machine (see 'Dependencies').
- All five module files and the **__ init __.py** file must be placed in the same folder (working directory).
- Edit the 'inat_creds.py' and 'inat_search_params.py' files appropriately.
- Ensure that the 'current_oldest_date.txt' file is **deleted** if present, **unless** the search is being restarted part way through after unexpected termination of the application.
- To run the scraper, execute the main script 'inaturalist_scraper.py' (from within VSCode or other code editor, or from Command Prompt, Python Command Prompt, Anaconda Prompt etc.).

### Outputs
- Folder called 'iNaturalist_data' created in the working directory.
- Sqlite3 database (user-specified name) created in this folder.
- Scraped data inserted into the destination table (user-specified name) of the database (explore database with DB Browser for SQLite (DB4S) or other appropriate application).
- Comprehensive log file generated (iNat_scraper.log). Logging info for subsequent scrape jobs is appended to this file
- A 'current_oldest_date.txt' file is generated to track progress of the scrape job through records ordered in ascending order by observation date. This file is automatically deleted upon normal termination of a scrape job.

## Dependencies
Python 3.8<br/>
Requests library (pip install requests)<br/>
Beautiful Soup 4 libray (pip install bs4)

## Contact
Please feel free to contact me (Chris Kelly) at the following email:<br/>
<img src="https://github.com/Afrisnake/AFRISNAKE.github.io/blob/master/images/cmrkelly_gmail_address.jpg" alt="email" width="180" height="36" />
