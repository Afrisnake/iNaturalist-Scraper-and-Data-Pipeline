import requests
from bs4 import BeautifulSoup as bs
import os
import json
import logging
import sys
import sqlite3
import datetime
from inat_creds import username, password
from inat_search_params import place_id, taxon_id, start_page, per_page, db_name, table_name
from inat_create_db import iNatPipeline


# Logging initialisation and configuration
logging.basicConfig(filename = 'iNat_scraper.log', level=logging.INFO, format='%(asctime)s - %(message)s')


# create a class for the iNaturalist site
class iNaturalist():

    '''
        Class representing all interactions with the iNaturalist website.

        Sets all search parameters for iNaturalist queries
        Opens an iNaturalist session which is maintained for the duration of the scrape job
        Instantiates the iNatPipeline class (via import from the 'inat_create_db.py' module)

        ...
            
        Attributes
        ----------
        place_id : int
            Numerical code representing the geographic region for the scrape job
            Default is the outside variable 'place_id' imported from the 'inat_search_params.py' module
        taxon_id : int
            Numerical code representing the taxon for the scrape job
            Default is the outside variable 'taxon_id' imported from the 'inat_search_params.py' module
        start_page : int
            Specifies which page of the returned search results the scrape job will begin at
            Default is the outside variable 'start_page' imported from the 'inat_search_params.py' module
        per_page : int
            Specifies the number of observation records to be returned per page of search results
            Default is the outside variable 'per_page' imported from the 'inat_search_params.py' module
        session : session object, automatic
            Uses 'requests' library to open an internet session object
            Allows connection with the iNaturalist host to be maintained for the duration of the login
        pipeline : instantiation of iNatPipeline class, automatic
            Instantiates class iNatPipeline (imported from 'inat_create_db.py' module)
            Mediates transfer of scraped data to a table (table_name) in an sqlite3 database (db_name)    

        Methods
        ----------
        login(username, password)
            Specifies data (and obtains csrf token) for login payload
            Submits login request to iNaturalist server
            Verifies login by attempting to access data on the userprofile homepage
        find_oldest_record()
            Submits search request filtered by observation date (ascending order; oldest to most recent)
            Extracts oldest observation date from results of the search
            Returns the oldest date (oldest_str : str)
            Terminates the application if oldest date cannot be accessed
        query_filterbydate(oldest_str, today)
            Submits search request filtered by observation date in ascending order: oldest ('oldest_str') to most recent ('today')
            Scrapes all observation data from specified page of search results
            Returns scraped data in json format (jsondata : dict)
        query_nofilter()
            Submits unfiltered search request
            Scrapes all observation data from specified page of search results
            Returns scraped data in json format (jsondata : dict)
        extract_records(data, cycles)
            Extracts observation data from a page of query results in json format (data)
            Takes parameter 'cycles' to help track which page of query results is being processed
            Returns extracted data as a list of tuples (page_observations : list)
        pipe_to_db(table_name, page_observations)
            Inserts scraped data (page_observations) into the destination db table
            Detects and ignores duplicate data when piping to the table

    '''

    logging.info('\n\n--------------------\n\nA new instance of the iNaturalist class has been created\n')


    def __init__(self, place_id=place_id, taxon_id=taxon_id, start_page=start_page, per_page=per_page):
        
        '''
            Constructs all the necessary attributes for the iNaturalist object.

            Parameters
            ----------
            place_id : int
                Numerical code representing the geographic region for the scrape job
                Default is the outside variable 'place_id' imported from the 'inat_search_params.py' module
            taxon_id : int
                Numerical code representing the taxon for the scrape job
                Default is the outside variable 'taxon_id' imported from the 'inat_search_params.py' module
            start_page : int
                Specifies which page of the returned search results the scrape job will begin at
                Default is the outside variable 'start_page' imported from the 'inat_search_params.py' module
            per_page : int
                Specifies the number of observation records to be returned per page of search results
                Default is the outside variable 'per_page' imported from the 'inat_search_params.py' module
            session : session object, automatic
                Uses 'requests' library to open an internet session object
                Allows connection with the iNaturalist host to be maintained for the duration of the login
            pipeline : instantiation of iNatPipeline class, automatic
                Instantiates class iNatPipeline (imported from 'inat_create_db.py' module)
                Mediates transfer of scraped data to a table (table_name) in an sqlite3 database (db_name)

        '''
        
        self.place_id = place_id
        self.taxon_id = taxon_id
        self.start_page = start_page
        self.per_page = per_page
        self.session = requests.session()
        self.pipeline = iNatPipeline(db_name) # Instantiates iNatPipeline class (from module create_db.py)

        
    # Makes a login request to the iNaturalist login website
    # Verifies login by accessing the userprofile homepage
    def login(self, username=username, password=password):

        '''
            Logs into the iNaturalist website as a specific registered user.
            
            Specifies data (and obtains csrf token) for login payload
            Submits login request to iNaturalist server
            Verifies login by attempting to access data on the userprofile homepage
            
            Parameters
            ----------
            username : str
                Username registered with iNaturalist
                Default is the outside variable 'username' imported from the 'inat_creds.py' module
            password : str
                Password corresponding with the username
                Default is the outside variable 'password' imported from the 'inat_creds.py' module
        
        '''

        # Setting the base url, login url and headers for authentication
        baseurl = 'https://www.inaturalist.org'

        login = '/session'

        login_headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 OPR/78.0.4093.184 (Edition avira-2)',
            'Origin':baseurl,
            'Referer':baseurl + '/login'
        }

        # Make initial request to login site to get authenticity-token (equiv to csrf token)
        # Constructed by DevTools inspection if iNaturalist login page
        loginpage = self.session.get(baseurl + '/login')
        soup = bs(loginpage.text, 'lxml') 
        forminput = soup.select('form input')
        auth_token = forminput[1]['value']
            
        # Login payload, constructed through DevTools inspection of 'Form Data' from login POST request
        login_payload = {
            'authenticity_token':auth_token,
            'user[email]':username,
            'user[password]':password,
            'user[remember_me]':0
        }

        # Post payload to the login route
        login_request = self.session.post(baseurl + login, headers=login_headers, data=login_payload)

        # Save request cookies
        cookies = login_request.cookies

        # In this instance, status code 200 is not sufficient to check for successful login
        # The following check will decisively verify login success
        soup = bs(self.session.get('https://www.inaturalist.org/home').text, 'lxml')
        userprofile = soup.select('h1 a')
            
        try:
            href = userprofile[0]['href']

            if f"/people/{username.lower()}" in href:
                print('Login succesful')
                logging.info(f'Successfully logged into iNaturalist as {username}')
            else:
                pass
        except:
            print('Login failure')
            logging.error(f'Error - failed to log in as {username}', exc_info=True)


    # Search request for records ordered according to date (ascending - oldest first)
    # Return only the oldest record, and extract the observation date
    # Terminates the application if the oldest date cannot be extracted
    def find_oldest_record(self):    

        '''           
            Extracts the date of the oldest record in the iNaruralist search.

            Submits search request filtered by observation date (ascending order; oldest to most recent)
            Extracts oldest observation date from results of the search
            
            Returns
            ----------
            oldest_str : str
                The date of the oldest record in the search (ISO 8601 format: yyyy-mm-dd)

            Raises
            ----------
            KeyError
                When scrape fails and jsondata['results'] therefore cannot be found
                Causes termination of the application via implementation of sys.error 
                
        '''

        # Set up the search query. Hidden API detected via DevTools, through inspection of 'Network'
        # Processed by Insomnia (Generate Code; Python, Requests) and adjusted appropriately    
        url = "https://api.inaturalist.org/v1/observations"

        querystring = {
            "verifiable":"true",
            "order_by":"observed_on",
            "order":"asc",
            "page":"1",
            "spam":"false",
            "place_id":f"{self.place_id}",
            "taxon_id":f"{self.taxon_id}",
            "locale":"en",
            "per_page":"1",
            "return_bounds":"true"
            }

        headers = {"sec-ch-ua": "^\^"}

        # Make search request to access relevant observations in iNaturalist
        try:
            r = self.session.request("GET", url, headers=headers, params=querystring)

            if r.status_code == 200:
                print(f"'Find oldest record' request successful; status_code = {r.status_code}")
                logging.info(f"'Find oldest record' request successful; status_code = {r.status_code}")
            else:
                print(f"An error occurred during the 'Find oldest record' request; status_code = {r.status_code}")
                logging.error(f"An error occurred during the 'Find oldest record' request; status_code = {r.status_code}", exc_info=True)
    
        except:
            print(f"'Find oldest record' request failed; status_code = {r.status_code}")
            logging.error(f"Error: 'Find oldest record' request failed; status_code = {r.status_code}", exc_info=True)

        # Save results of the request as variable 'jsondata' in json format
        jsondata = json.loads(r.text.encode('utf-8'))

        # Extract the observation date from this single oldest record
        # Return the oldest date (oldest_str) for input into 'query_filterbydate' method
        try:
            oldest_str = jsondata['results'][0]['observed_on_details']['date']
            print(f'The earliest record for this query (oldest_str) is {oldest_str}')
            logging.info(f'The earliest record for this query (oldest_str) is {oldest_str}')
            return oldest_str
        except:
            print('Error - the date for the oldest record could not be accessed from query results')
            logging.critical('Error: the date for the oldest record could not be accessed from query results\nThe application has been terminated', exc_info=True)
            sys.exit('The date for the oldest record cannot be accessed. The application has been terminated') 
        

    # Submit filtered-by-date search query to iNaturalist and return single-page results in json format
    def query_filterbydate(self, oldest_str, today):

        '''
            Scrapes json data from specified page of an iNaturalist query, filtered by observation date (ascending order).
            
            Submits search request filtered by observation date in ascending order: oldest ('oldest_str') to most recent ('today')
            Scrapes all observation data from specified page of search results

            Parameters
            ----------
            oldest_str : str
                The date of the oldest record in the search (ISO 8601 format: yyyy-mm-dd)
                Obtained via the 'find_oldest_record' method
            today : str
                The current date (ISO 8601 format: yyyy-mm-dd)

            Returns
            ----------
            jsondata : dict
                Scraped data from the specified page of the query, in json format
        
        '''

        # Set up the search query. Hidden API detected via DevTools, through inspection of 'Network'
        # Processed by Insomnia (Generate Code; Python, Requests) and adjusted appropriately
        url = "https://api.inaturalist.org/v1/observations"

        querystring = {
            "verifiable":"true",
            "order_by":"observed_on",
            "order":"asc",
            "page":f"{self.start_page}",
            "spam":"false",
            "d1":f"{oldest_str}",
            "d2":f"{today}",
            "place_id":f"{self.place_id}",
            "taxon_id":f"{self.taxon_id}",
            "locale":"en",
            "per_page":f"{self.per_page}",
            "return_bounds":"true"
            }

        headers = {"sec-ch-ua": "^\^"}

        # Make filtered search request to access relevant observations in iNaturalist
        try:
            r = self.session.request("GET", url, headers=headers, params=querystring)
            
            if r.status_code == 200:
                print(f"'Filterbydate' request successful; status_code = {r.status_code}")
                logging.info(f"'Filterbydate' request successful; status_code = {r.status_code}")
            else:
                print(f"An error occurred during the 'Filterbydate' request; status_code = {r.status_code}")
                logging.error(f"An error occurred during the 'Filterbydate' request; status_code = {r.status_code}", exc_info=True)
    
        except:
            print(f"'Filterbydate' request failed; status_code = {r.status_code}")
            logging.error(f"Error: 'Filterbydate' request failed; status_code = {r.status_code}", exc_info=True)
        
        # Save results of the request as variable 'jsondata' in json format
        jsondata = json.loads(r.text.encode('utf-8'))

        # Return jsondata variable for processing
        return jsondata
        

    # Submit unfiltered search query to iNaturalist and return results in json format
    # This function is not currently used in this application
    def query_nofilter(self):

        '''
            Scrapes json data from specified page of an unfiltered iNaturalist query.
            
            Submits unfiltered search request
            Scrapes all observation data from specified page of search results

            Returns
            ----------
            jsondata : dict
                Scraped data from the specified page of the query, in json format
        
        '''

        # Set up the search query. Hidden API detected via DevTools, through inspection of 'Network'
        # Processed by Insomnia (Generate Code; Python, Requests) and adjusted appropriately
        search_url = "https://api.inaturalist.org/v1/observations"

        querystring = {
            "verifiable":"true",
            "order_by":"observations.id",
            "order":"desc",
            "page":f"{self.start_page}",
            "spam":"false",
            "place_id":f"{self.place_id}",
            "taxon_id":f"{self.taxon_id}",
            "locale":"en",
            "per_page":f"{self.per_page}",
            "return_bounds":"true"
        }

        headers = {"sec-ch-ua": "^\^"}

        # Make search request to access relevant observations in iNaturalist
        try:
            r = self.session.request("GET", search_url, headers=headers, params=querystring)

            if r.status_code == 200:
                print(f"'Nofilter' request successful; status_code = {r.status_code}")
                logging.info(f"'Nofilter' request successful; status_code = {r.status_code}")
            else:
                print(f"An error occurred during the 'Nofilter' request; status_code = {r.status_code}")
                logging.error(f"An error occurred during the 'Nofilter' request; status_code = {r.status_code}", exc_info=True)
    
        except:
            print(f"'Nofilter' request failed; status_code = {r.status_code}")
            logging.error(f"Error: 'Nofilter' request failed; status_code = {r.status_code}", exc_info=True)

        # Save results of the request as variable 'jsondata' in json format
        jsondata = json.loads(r.text.encode('utf-8'))

        # Return jsondata variable for processing
        return jsondata


    # Extract observation data from a page of query results
    def extract_records(self, data, cycles):

        '''
            Extracts observation data from a page of query results in json format.
            
            The following variables are extracted for each observation record (blank if data missing):

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

            Parameters
            ----------
            data : dict
                Scraped data from the specified page of an iNaturalist query, in json format
            cycles : int
                Integer representing the number of sets of 10000 records that have been scraped through already
                Helps to track which page of query results is being processed

            Returns
            ----------
            page_observations : list
                Extracted data (list of tuples containing variables above, one tuple per observation record)
        
        '''

        try:
            # Define list for extracted variables from observations on current page
            page_observations = []

            # Loop through all observations in the 'results' key of jsondata
            for obs in data['results']:

            # Extract the variables of interest
                try:
                    id = obs['id']
                except:
                    id = ''
                    logging.warning(f'id unavailable for current obs', exc_info=True)

                try:
                    qual_grade = obs['quality_grade']
                except:
                    qual_grade = ''
                    logging.warning(f'qual_grade unavailable for obs id {id}', exc_info=True)

                try:
                    date = obs['observed_on_details']['date']
                except:
                    date = ''
                    logging.warning(f'date unavailable for obs id {id}', exc_info=True)

                try:
                    locality = obs['place_guess']
                except:
                    locality = ''
                    logging.warning(f'locality unavailable for obs id {id}', exc_info=True)

                try:
                    long = obs['geojson']['coordinates'][0]
                    lat = obs['geojson']['coordinates'][1]
                    coords = str(obs['geojson']['coordinates'][::-1])
                except:
                    long = ''
                    lat = ''
                    coords = ''
                    logging.warning(f'coords unavailable for obs id {id}', exc_info=True)

                try:
                    introduced = obs['taxon']['introduced']
                except:
                    introduced = ''
                    logging.warning(f'introduced unavailable for obs id {id}', exc_info=True)

                try:
                    genus = obs['taxon']['name'].split()[0]
                except:
                    genus = ''
                    logging.warning(f'genus unavailable for obs id {id}', exc_info=True)

                try:
                    species = obs['taxon']['name'].split()[1]
                except:
                    species = ''
                    logging.warning(f'species unavailable for obs id {id}', exc_info=True)
                
                try:
                    subspecies = obs['taxon']['name'].split()[2]
                except:
                    subspecies = ''

                # Place all variable values for an observation into a tuple for transfer the SQLite3
                obs_record = (id, date, genus, species, subspecies, coords, lat, long, locality, introduced, qual_grade)
                
                # Append each observation to the 'observations' list
                page_observations.append(obs_record)
        
            print(f'{len(page_observations)} records extracted from page {self.start_page + 100*cycles}')
            logging.info(f'{len(page_observations)} records extracted from page {self.start_page + 100*cycles}')
            return page_observations

        except:
            print(f'Error - unable to extract observation data from page {self.start_page + 100*cycles} of the current search')
            logging.error(f'Error - unable to extract observation data from page {self.start_page + 100*cycles} of the current search', exc_info=True)


    # Sends scraped records from each page to the db
    def pipeline(self, table_name, page_observations):

        '''
            Inserts extracted observation data into the destination table of a sqlite3 database.
            
            Executes 'pipe_to_db' method from class iNatPipeline, imported from 'create_db.py' module
            Detects and ignores duplicate data when piping to the table

            Parameters
            ----------
            table_name : str
                Name of the destination database table for observation data
                Default is the outside variable 'table_name' imported from the 'inat_search_params.py' module
            page_observations : list
                List of tuples, each containing data from a single iNaturalist record
                Data must correspond exactly with columns of the destination table
                Default is 'page_observations' output of 'extract_records' method

        '''

        # Executes 'pipe_to_db' method from class iNatPipeline, imported from 'create_db.py' module    
        self.pipeline.pipe_to_db(table_name, page_observations)



# This function is defined outside of the iNaturalist class definition
# Runs a full scrape job based on parameters in the 'inat_search_params' module
# Routes scraped data via the pipeline to a destination table in the sqlite3 database
def scraper():    

    '''           
        Runs a full scrape job based on parameters in the 'inat_search_params.py' module.

        Instantiates the iNaturalist class
        Executes a query filtered by date ('query_filterbydate' method)
        Loops through pages of filtered observations matching the query until the 'extract_records' method returns zero records
        Pipes extracted observation data to the destination table in the sqlite3 database

        iNaturalist has a limit of start_page*per_page = 10000 for data retrieval via the API. The code loops through pages of
        observations up to this limit, after which the date of the last observation extracted prior to the limit being reached is
        set as the new upper bound (oldest date) for the next round of querying filtered by date. This allows scraping to continue
        into the next set of records.

        If the scrape job terminates unexpectedly, it can be restarted at the last page that was processed prior to termination.
        The user edits the 'inat_search_params.py' file, setting the 'start_page' value to the page number at which the scrape ended.
        If this results in start_page*per_page > 10000, the date of the last observation prior to termination is retrieved from the
        'current_oldest_date.txt' file and set as the upper bound (oldest date) for a new round of querying filtered by date. Scraping
        then begins where it left off, at page 1 of this new filtered search.

        In a fresh scrape, the user may enter a value for the 'start_page' variable such that start_page*per_page > 10000. This application
        does not have functionality to support such a search, and the user is instructed to enter a lower value for 'start_page'. 

        Raises
        ----------
        UnboundLocalError -> FileNotFoundError
            When start_page*per_page > 10000 in a fresh implementation of scraper
            Causes termination of the application
            User is instructed to use a lower 'start_page' value
                
    '''

    # Instantiate the iNaturalist class
    scrape = iNaturalist()

    logging.info('A new scrape job has been initiated\n')

    # Create a destination table in the database
    scrape.pipeline.create_table(table_name)

    # Login to the iNaturalist website
    scrape.login()

    # Variable to track the number of records extracted from a page
    records_on_page = scrape.per_page

    # Counter to track total number of observations scraped
    all_observations = 0

    # Find oldest record in query
    oldest_str = scrape.find_oldest_record()

    # "yyyy-mm-dd" format for present date
    today = datetime.date.today().isoformat()

    # Record no of times the code has cycled through sets of (start_page*per_page = 10000)
    cycles = 0

    # Loop through pages of filtered observations matching the query until the 'extract_records' method returns
    # zero records (records_on_page = 0), at which point the code assumes that all observations have been scraped 
    while records_on_page:

        # iNaturalist has a limit of start_page*per_page = 10000. This code loops through pages of observations
        # up to this limit, after which the query is reset using filtering by date, to allow scraping to
        # continue into the next set of records
        while scrape.start_page*scrape.per_page <= 10000:

            jsondata = scrape.query_filterbydate(oldest_str,today) # takes self.start_page
            page_observations = scrape.extract_records(jsondata,cycles)
            records_on_page = len(page_observations)

            # If no records are present on the page, the code will assume that all records have now been scraped and the
            # application will terminate
            if records_on_page == 0:
                print(f'All records scraped; page {scrape.start_page + 100*cycles - 1} was the last page containing records')
                logging.info(f'All records scraped; page {scrape.start_page + 100*cycles - 1} was the last page containing records')
                break
            # If records have been extracted from the current page, they are piped to the appropriate table of the sqlite3 database
            else:
                with open('current_oldest_date.txt','w') as f:
                    f.write(page_observations[-1][1])
                    f.seek(0)

                scrape.pipeline.pipe_to_db(table_name, page_observations)
                all_observations += records_on_page
                scrape.start_page += 1

        else:
            # If the limit of start_page*per_page = 10000 is reached, this code resets the 'oldest_str' variable to
            # the date of the last observation extracted prior to the limit being reached. This is then set as the
            # upper bound (oldest date) for a new round of querying ('query_filterbydate', ascending order), as the
            # code loops back to the outer 'while' statement. Scraping begins again at page 1 of this new filtered search
            try:
                oldest_str = page_observations[-1][1]
                scrape.start_page = 1
                cycles += 1
                print(f'Scraped {all_observations} records. Now scraping in set {cycles + 1} of records (max 10000 per set)')
                logging.info(f'Scraped {all_observations} records. Now scraping in set {cycles + 1} of records (max 10000 per set)')

            # This exception caters for situations when the scrape job is being restarted after unexpected termination.
            # User will restart the application using a 'start_page' value corresponding with the point at which the scrape ended.
            # When start_page*per_page > 10000, the following code will be executed, accessing the 'current_oldest_date' file and
            # retrieving the date of the last observation recorded prior to the termination. This value is then set as the upper bound
            # (oldest date) for a new round of querying ('query_filterbydate', ascending order) as the code loops back to the outer
            # 'while' statement and scraping begins again at page 1 of this new filtered search 
            except:
                try:
                    with open('current_oldest_date.txt','r') as f:
                        oldest_str = f.read()
                        f.seek(0)

                    scrape.start_page = 1
                    from inat_scrape_longstrings import print_exception1, log_exception1
                    print(print_exception1) 
                    logging.error(log_exception1, exc_info=True)
                    
                # This exception occurs if in a fresh scrape, the user enters a value for the 'start_page' variable such that
                # start_page*per_page > 10000. This application does not have functionality to support such a search, and the
                # user is instructed to enter a lower value for 'start_page' 
                except:
                    from inat_scrape_longstrings import print_exception2, log_exception2
                    print(f'start_page = {scrape.start_page}, per_page = {scrape.per_page}\n' + print_exception2)
                    logging.critical(f'start_page = {scrape.start_page}, per_page = {scrape.per_page}\n' + log_exception2, exc_info=True)
                    break

    # Deletes the 'current_oldest_date.txt' file to avoid interference with subsequent scrape jobs
    try:
        os.unlink('current_oldest_date.txt')
    except:
        pass

    print(f'Total number of observations extracted: {all_observations}')
    print(f'Scraping terminated in set {cycles + 1} of 10000 records')
    logging.info(f'Total number of observations extracted: {all_observations}\nThe code terminated in set {cycles + 1} of 10000 records')
    

# If this module is run as the main module, the scraper function is executed
if __name__ == "__main__":

    scraper()