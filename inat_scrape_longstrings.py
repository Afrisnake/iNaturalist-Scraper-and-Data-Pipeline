'''
    Long 'print' and 'logging' messages for the 'scraper' function of the 'inaturalist_scraper.py' module.

    These messages reduce readability of the 'scraper' code, so are imported to the function from this module. 

'''

print_exception1 = '''It seems that the scrape job is being continued where it left off after the application failed for some reason.
The date of the last observation recorded prior to the termination has been retrieved from the 'current_oldest_date' file.
This value has been set as the upper bound (oldest date) for a new round of querying in which scraping begins again where it left off
at page 1 of this new filtered search'''

log_exception1 = '''It seems that the scrape job is being continued where it left off after the application failed for some reason.
The date of the last observation recorded prior to the termination has been retrieved from the 'current_oldest_date' file. 
This value has been set as the upper bound (oldest date) for a new round of querying in which scraping begins again where it left off
at page 1 of this new filtered search'''

print_exception2 = '''This application does not permit you to select an initial 'start_page' such that the product start_page*per_page > 10000
Select a lower value for the start_page variable and restart the scraping job'''

log_exception2 = '''This application does not permit you to select an initial 'start_page' such that the product start_page*per_page > 10000
Select a lower value for the start_page variable and restart the scraping job'''