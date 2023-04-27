""" FTPFuncs
This is the module containing all functions used in this project for FTP crawl searches
Processors: functions preppingn args
Crawlers: given processed args, search and return urls
"""

# import libraries to parse and read through the websites 
import bs4, requests
import plyer
import time 

print('---- Welcome to the Incident Data Web Crawler ---- \n')
print('This program will take your keyword and start from the the Incident Specific Data/ directory. \n')
print('Sample inputs: "Fort Huachuca", "Avenza", "Melozitna", "Dixie", "Contact Creek" \n')
print('WARNING: BE SURE TO CHECK ALL CONSTANTS')

# workflow:
# callerCrawler (filters given arguments -> calls subsequent actual crawlers) ->
# crawler (actual recurse function) vs. gaccYearCrawler (recurse with no keyword functionality) -> searchForKeyword (boolean for crawler to continue)

# IMPORT CONSTANTS
gacc_zones = PerimConsts.gacc_zones
starting_URL = starting

# FUNCTION DEFINITIONS
# processing type: handle input arguments, monitor crawler
# crawler type: actual crawling
# intersect type: read off URL and do intersection test

# @TODO: complete implementation after gaccyear crawling
def intersectFinder(urls, feds):
    """ function to identify true url matches
        see if read object geometrically "matches" w/ intersect
        assume feds is single shape (not full evolution)
        return: list of urls w/ results
    """
    
    return None

# @TODO: define pure year/gacc basic crawler
def gaccYearProcessing(gacc_keyword, year_keyword='0', depth=8):
    """ processor for year/gacc based search only
        for now, do not permit non-gacc term based searches
        
        return: list 
    """
    assert isinstance(gacc_keyword, str) and isinstance(year_keyword, str)
    assert 'unsure' not in gacc_keyword, "Unsure indicated; invalid search"
    assert gacc_keyword in gacc_zones, "This keyword is not in the list of gacc regions. Check intersection results."

    # select gacc keyword based region folders-  (name + '/' char)
    starting_URL = starting_URL + gacc_keyword + '/'
    print('The starting point for the search will be at: ', starting_URL)
    
    # recurse to certain depth to return year matches
    print(f'Selected year: {year_keyword}')
    if year_keyword == '0' or len(year_keyword) < 4:
        assert 1 == 0, 'Failed to initiate search; default/invalid year passed.'
    
    # depth mod / check
    assert depth >= 5, "Passed depth is too low (must be >= 5, adjust call"
    if depth != 8:
        print('WARNING: DEPTH MODIFIED; this may impact your search time. Recommended default is 8.')
    
    # call crawler and return candidates
    found_array = gaccYearCrawler(starting_URL, depth, [])
    
    return found_array

def gaccYearCrawler(pageURL, depth, results):
    """ crawler for year/gacc based search only
        for now, do not permit non-gacc term based searches
        
        return: results list (keeps growing till end)
    """
    # url access attempts
    try:
        getPage = requests.get(pageURL)
        getPage.raise_for_status()
    except requests.exceptions.HTTPError as err: 
        print('Accessed a Forbidden URL/URL with error status, return false')
        return []
    except requests.exceptions.Timeout:
        print('Timeout occured, check FTP site status manually')
        return []
    except requests.exceptions.TooManyRedirects:
        print('Too many re-directs, check FTP site status manually')
        return []
    except requests.exceptions.RequestException as e:
        print('Catostrophic error, bail execution due to RequestException')
        return []
    
    # base case (hit all items/non dirs)
    
    # base case (hit depth limit)
    
    # Parse text for opportunities block
    soup = bs4.BeautifulSoup(getPage.text, 'html.parser')
    
    # check the current text for any emptiness 
    a_categories = soup.find_all('a')
    # pop out using loop to exclude irrelevant categories 
    a_categories_modified = a_categories.copy()
    
    if not a_categories:
        print('Empty page detected, return false')
        return []
    
    # loop through the a_categories to get rid of irreleveant matches like parent dir
    # Also eliminate the Name, Last modified, size from the list to reduce search confusion
    
    for link in a_categories:
        
        # eliminate from the link search to prevent recursive returns:
        # parent directory, name, last modified, size, description
        
        # Note: the filter assumes uniformity per every page for its a-class titles
        # want to eliminate the possibility of lower case misses -> make whole thing lower
        if 'Parent Directory' in str(link):
            # remove this link from the a_categories_modified
            a_categories_modified.remove(link)
        elif 'Name' in str(link) or  'Size' in str(link) or 'Last modified' in str(link) or 'Description' in str(link):
            # remove related categories that do not contribute to search, aka redundant categories
            a_categories_modified.remove(link)
    
    # switch when found
    available = False
    
    # search the modified list of valid links, including files
    for link in a_categories_modified:
        # fetch the a class name of the link
        current_string_check = link.get('href')
        if keyWord in str(current_string_check).lower():
            # if given a year, must check if in URL too
            if selected_a_year:
                if year_keyword in pageURL:
                    available = True
                    break
            else:
                available = True
                break
        # try: if there is %20 -> check one side and the other for appearance
        # check is "_" can appear instead of spaces
        elif ("%20" in keyWord):
            # ISSUE: may be more than one %20 -> iterate through list 
            split = keyWord.split("%20")
            # excluding the %20, try both sides
            # ex: Minto_Lakes != Minto%20Lakes
            # if %20 isn't in, it may bug bc it wants whole thing
            
            # [true, true] -> counter should = 2
            counter_found = 0;
            
            # iterate through splits to see if all are in
            for substring in split:
                if substring in str(current_string_check).lower():
                    counter_found += 1
                
            # if the counter matches arr size -> must be true for all substrings
            # therefore the keyword is found
            if len(split) == counter_found:
                if selected_a_year:
                    if year_keyword in pageURL:
                        # print('TESTING: year in '+ str(pageURL))
                        available = True
                        break
                else:
                    available = True
                    break
            
    # return if available
    assert isinstance(available, bool), "available var is not boolean, check procedure"
    
    # do we want keyword based results? - maybe before diving into incident, check inters?
    
    return results

# @TODO: FIX PASSED ARRS
# @TODO: FIX KEYWORD RELIANCE - but still enable search if wanted...
def callerCrawler(keyword=None, gacc_keyword, year_keyword='0', depth=8):
    """ Crawl NIFC FTP server for best fire match 
        keyword: NONE (esp for most FEDS perims assume none)
        gacc_keyword: identified gacc region (perimsVsFTP should identify via intersect)
        depth: extent of acceptable dirs to go down into
        
        return: list of URLs to consider for match
    """
    
    assert isinstance(gacc_keyword, str) and isinstance(year_keyword, str)
    
    # result arr
    found_array = []
    # apply keyword search?
    keyword_processing = False
    
    if keyword is not None:
        keyword_processing = True
        # keyword processing
        print('Name "' + keyword  + '" recieved.')
        keyword = keyword.lower()

        # remove instances of fire/Fire
        if 'fire' in keyword:
            keyword = keyword.replace("fire", "")
        if 'Fire' in keyword:
            # in case lower fails
            keyword = keyword.replace("Fire", "")

        # remove any spaces within the string for search - do not string in-between values 
        keyword = keyword.strip()
        # match encoding of inside spaces - " " do not exist in URLs of FTP server!
        # also remove _ as they are mixed with spaces -> this way processing program treats them fairly
        if " " in keyword:
            keyword = keyword.replace(" ", "%20")
            # print('The keyword contained a space, it has been replaced with a "%20" to match URL encoding')
        if "_" in keyword:
            keyword = keyword.replace("_", "%20")
            # print('The keyword contained an underscore, it has been replaced with a "%20" to match URL encoding')

        print('Final keyword for input:')
        print(keyword)

    else:
        keyword_processing = False
        print('No keyword processing applied: ')
    
    # gacc processing:
    selected_a_gacc = True
    
    gacc_zones = ["alaska", "calif_n", "calif_s", "california_statewide", "eastern", "great_basin", "n_rockies", "pacific_nw", "rocky_mtn", "southern", "southwest"]
    
    # try appending gacc to url
    if 'unsure' in gacc_keyword:
        starting_URL = 'https://ftp.wildfire.gov/public/incident_specific_data/'
        print('You have selected "unsure".')
        print('The startig point for the search will be at: ', starting_URL)
    else:
        try:
            assert gacc_keyword in gacc_zones, "This keyword is not in the list of gacc regions. Please try again."
        except AssertionError as msg:
            print(msg)

        if gacc_keyword in gacc_zones:
            # now append to starting_URL (name + '/' char)
            starting_URL = 'https://ftp.wildfire.gov/public/incident_specific_data/'
            starting_URL = starting_URL + gacc_keyword + '/'
            # update boolean for later checking
            selected_a_gacc = True 

            print(' ')
            print('The starting point for the search will be at: ', starting_URL)

    # year processing:
    selected_a_year = True
    print(f'Selected year: {year_keyword}')
    if year_keyword == '0' or len(year_keyword) < 4:
        assert 1 == 0, 'Failed to initiate search; default/invalid year passed.'
    
    # depth mod / check
    assert depth >= 5, "Passed depth is too low (must be >= 5, adjust call"
    if depth != 8:
        print('WARNING: DEPTH MODIFIED; this may impact your search time. Recommended default is 8.')
    
    print('SEARCH INITIATED FOR:')
    # print('Incident Name:' , keyword)
    assert selected_a_gacc and selected_a_year, "Critical failure; year/gacc not provided."
    print('----------------------------------------------------------------------------------------')
    print('OUTPUT LOG:')
    print('----------------------------------------------------------------------------------------')

    # depth = depth
    # clear found_array
    # found_array = []
    
    # directly have the initial array modified and then returned after recursive calls
    found_array = crawler(starting_URL, keyword, depth)

    # search complete, dump results
    print(' ')
    print('----------------------------------------------------------------------------------------')
    print('Search complete!')
    print('----------------------------------------------------------------------------------------')
    print(' ')
    if len(found_array) == 0:
        # if none found, advise user.
        print('No matches found in the search. Check your incident name, year, gacc, or depth.')
    else:
        # else loop and print found links
        print('All found directories containing user-input info:')
        for i in found_array:
            print(i)
    
    return found_array


def searchForKeyword(pageURL, keyWord, selected_a_year, year_keyword):
    """ searchForKeyword() function
        Description: given a page URL, return true if the keyWord is found within the listed files/directories listed in the URL.
        Inputs: pageURL (string), keyWord (string)
        Output: boolean
        if selected_a_year == True, must check if year exists in the URL!
    """

    # Download page
    # Example of valid pageURL string input: 'https://ftp.wildfire.gov/public/incident_specific_data/'
    # try status and throw if forbidden is encountered
    try:
        getPage = requests.get(pageURL)
        getPage.raise_for_status()
    except requests.exceptions.HTTPError as err: 
        print('Accessed a Forbidden URL/URL with error status, return false')
        return False
    except requests.exceptions.Timeout:
        print('Timeout occured, check FTP site status manually')
        return False
    except requests.exceptions.TooManyRedirects:
        print('Too many re-directs, check FTP site status manually')
        return False
    except requests.exceptions.RequestException as e:
        print('Catostrophic error, bail execution due to RequestException')
        return False
  
    # Parse text for opportunities block
    soup = bs4.BeautifulSoup(getPage.text, 'html.parser')
    
    # check the current text for any emptiness 
    a_categories = soup.find_all('a')
    # pop out using loop to exclude irrelevant categories 
    a_categories_modified = a_categories.copy()
    
    if not a_categories:
        print('Empty page detected, return false')
        return False
    
    # loop through the a_categories to get rid of irreleveant matches like parent dir
    # Also eliminate the Name, Last modified, size from the list to reduce search confusion
    
    for link in a_categories:
        
        # eliminate from the link search to prevent recursive returns:
        # parent directory, name, last modified, size, description
        
        # Note: the filter assumes uniformity per every page for its a-class titles
        # want to eliminate the possibility of lower case misses -> make whole thing lower
        if 'Parent Directory' in str(link):
            # remove this link from the a_categories_modified
            a_categories_modified.remove(link)
        elif 'Name' in str(link) or  'Size' in str(link) or 'Last modified' in str(link) or 'Description' in str(link):
            # remove related categories that do not contribute to search, aka redundant categories
            a_categories_modified.remove(link)
    
    # switch when found
    available = False
    
    # search the modified list of valid links, including files
    for link in a_categories_modified:
        # fetch the a class name of the link
        current_string_check = link.get('href')
        if keyWord in str(current_string_check).lower():
            # if given a year, must check if in URL too
            if selected_a_year:
                if year_keyword in pageURL:
                    available = True
                    break
            else:
                available = True
                break
        # try: if there is %20 -> check one side and the other for appearance
        # check is "_" can appear instead of spaces
        elif ("%20" in keyWord):
            # ISSUE: may be more than one %20 -> iterate through list 
            split = keyWord.split("%20")
            # excluding the %20, try both sides
            # ex: Minto_Lakes != Minto%20Lakes
            # if %20 isn't in, it may bug bc it wants whole thing
            
            # [true, true] -> counter should = 2
            counter_found = 0;
            
            # iterate through splits to see if all are in
            for substring in split:
                if substring in str(current_string_check).lower():
                    counter_found += 1
                
            # if the counter matches arr size -> must be true for all substrings
            # therefore the keyword is found
            if len(split) == counter_found:
                if selected_a_year:
                    if year_keyword in pageURL:
                        # print('TESTING: year in '+ str(pageURL))
                        available = True
                        break
                else:
                    available = True
                    break
            
    # return if available
    assert isinstance(available, bool), "available var is not boolean, check procedure"
    return available 
    

def crawler(currPageURL, keyword, depth, selected_a_year, year_keyword):
    """
        # crawler() function
        # Description: 
        # Inputs: keyword (string which was inputted by user and processed in earlier block), startingPageURL (string)
        # Output: found_URL_matches (array with all URL strings found with matches)

        # starting URL -> this can be customized, but is used to reduce the search span for the function 
        # DEFAULT:

        # empty array which will be returned 
        # append to array after every recursive call to the searchForKeyword function 
        # found_URL_matches = []
    """
    # search the current page with boolean returned
    keyword_boolean = searchForKeyword(currPageURL, keyword)
    
    if keyword_boolean:
        # if found, display result
        print('')
        print('NAME FOUND! Printing directory URL that has "' + keyword + '" in it (along with year if provided by user)...')
        print(currPageURL)
        found_array.append(currPageURL)
        print('')
        # append the URL to arr
        # found_URL_matches.append(currPageURL)
        
    # now for every directory, append -> create URL -> recurse
    # make sure to update the stored ver 
    # this could cause issues depending on how it traverses the file tree
    
    # repeat get page process for the current URL before access
    try:
        getPage = requests.get(currPageURL)
        getPage.raise_for_status()
    except requests.exceptions.HTTPError as err: 
        # in case of forbidden access URL 
        print('Accessed a Forbidden URL/URL with error status, return false')
        return False
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        print('Timeout occured, check FTP site status manually')
        return False
    except requests.exceptions.TooManyRedirects:
        # Tell the user their URL was bad and try a different one
        print('Too many re-directs, check FTP site status manually')
        return False
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        print('Catostrophic error, bail execution due to RequestException')
        return False
  
    # Parse text for opportunities block
    soup = bs4.BeautifulSoup(getPage.text, 'html.parser')
    
    # check the current text for any emptiness 
    a_categories = soup.find_all('a')
    # pop out using loop to exclude irrelevant categories 
    a_categories_modified = a_categories.copy()
    
    # loop through the a_categories to get rid of irreleveant matches like parent dir
    # Also eliminate the Name, Last modified, size from the list to reduce search confusion
        
    for link in a_categories:
        # eliminate from the link search to prevent recursive returns:
        # want to eliminate the possibility of lower case misses -> make whole thing lower
        if 'Parent Directory' in str(link):
            # remove this link from the a_categories_modified
            a_categories_modified.remove(link)
        elif 'Name' in str(link) or  'Size' in str(link) or 'Last modified' in str(link) or 'Description' in str(link):
            # remove related categories that do not contribute to search, aka redundant categories
            a_categories_modified.remove(link)
    
    
    for link in a_categories_modified:
        # recurse and pick directories
        # if is a directory -> call function with the URL name appended to meet it
        actual_URL = str(link.get('href'))
        # if ends with '/' -> is a directory -> recurse 
        # DO NOT RECURSE ON FILES!
        if actual_URL.endswith('/'):
            # print(actual_URL)
            # print('Directory detected through / in link')
            
            # modify currentURL by appending this
            new_URL_to_recurse = currPageURL + actual_URL
            
            # CONDITIONAL YEAR CHECK - perform only if the user picked a year
            if selected_a_year:
                # count slashes: if seven or more, it now must have the year to do a search
                if new_URL_to_recurse.count('/') >= depth:
                    if year_keyword not in actual_URL:
                        # at a certain depth the year will not be present
                        # to prevent useless recursion, change the depth before calling.
                        pass
                        # print('This dir has reached >= 8 slashes with no year, skipping...')
                    else:
                        print('Year match found. Recursing in: ' + new_URL_to_recurse)
                        crawler(new_URL_to_recurse, keyword, depth)

                else:
                    # not enough slashes quite yet, keep going
                    print('Recursing in: ' + new_URL_to_recurse)
                    # recursive call
                    crawler(new_URL_to_recurse, keyword, depth)
            
            # if there is no year, we don't narrow search in any circumstances
            else:
                # recurse on this file branch
                print('No year given. Recursing in: ' + new_URL_to_recurse)
                # print(found_URL_matches)
                # found_URL_matches.append(crawler(new_URL_to_recurse, keyword, []))

                # recursive call
                crawler(new_URL_to_recurse, keyword, depth)
    
    # return found_URL_matches
    return 1


