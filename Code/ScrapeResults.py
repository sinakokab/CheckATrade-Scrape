import requests, bs4, os, sys

## TODO:
## Add Multithreading
## Going to need a proxy and obsfucation or atleast less botty behaviour

LastWebsiteScraped = ""
PostCode = ""

def CheckDirectory(Directory, File):
    d = os.path.dirname(os.getcwd()) + "\\" + Directory
    if not os.path.exists(d):
        print("File path - " + d + " doesn't exist.\nCreating...")
        os.makedirs(d)

    d = d + "\\" + File
    if not os.path.exists(d):
        with open(d, 'w+') as f:
            print("File Path - " + d + " doesn't exist.\nCreating.")
    else:
        print("File Path Exists.")
        return d

def generate_url(page, primaryurl):
    #open a file w/ postcodes.
    #postcode = str() # insert file opening code

    if primaryurl == True:
        print("Generating new root URL")
        global PostCode
        d = CheckDirectory("Storage", "Postcodes.txt")

        with open(d, 'r+') as f:
            postcodes = f.read().splitlines()

        if len(postcodes) == 0:
            print("There are no postcodes in " + d)
            sys.exit()

        if PostCode == "":
            PostCode = postcodes[0]
        else:
            i = postcodes.index(PostCode)
            print(PostCode)
            PostCode = postcodes[(i + 1)]
            print(PostCode)

    if page is None or page == 0:
        page = 1

    urltoscrape = "https://www.checkatrade.com/Search/?location="+ PostCode +"&cat=20&secondary=true&page=" + str(page)
    print("URL GENERATED: " + urltoscrape)
    return urltoscrape

def WriteToFile(Reason, Page, URL):
    if Reason == "No Website":
        d = CheckDirectory("Storage", "NoWebsiteFile.txt")

        with open(d) as f:
            LinesWritten = f.read().splitlines()
            for Line in LinesWritten:
                if (Reason + ":" + Page + ":" + URL) == Line:
                    print("Line already written in file.")
                    return False

        with open(d, 'a') as f:
            NoWebsiteWrite = f.write(Reason + ":" + Page + ":" + URL + "\n")
    else:
        d = CheckDirectory("Storage", "BrokenWebsite.txt")
        with open(d) as f:
            LinesWritten = f.read().splitlines()
        for Line in LinesWritten:
            if (Reason + ":" + Page + ":" + URL) == Line:
                print("Line already written in file.")
                return False

        with open(d, 'a') as f:
            NoWebsiteWrite = f.write(Reason + ":" + Page + ":" + URL + "\n")

def get_page_source(URL):
    response = requests.get(URL, timeout=360)
    soup_object = bs4.BeautifulSoup(response.text, "html.parser")

    return soup_object

def find_number_of_pages(page_source):
    Pages = page_source.find_all("span", "pagination__page--not-current pagination__page")
    print("There are " + Pages[-1].text + " pages")

    return int(Pages[-1].text)

def WebsiteChecks(WebsiteToCheck):
    try:
        r = requests.head("http://"+WebsiteToCheck, timeout=360)
        if r.status_code == 200:
            return False
        else:
            r = requests.head("https://"+WebsiteToCheck, timeout=360)

            if r.status_code == 200 or 301 or 302:
                return False
            else:
                print("Website is down.")
                return True
                
    except Exception as e:
        #print(e)
        print("Status Code Error - " + str(r.status_code))

def ScrapePages(page_to_scrape):
    global LastWebsiteScraped
    url = generate_url(page_to_scrape, False)
    page_source = get_page_source(url)
    links_raw = page_source.find_all("a", "catnow-search-click block") #gets link to plumber page
    for a in links_raw:
        if a['href'] != None and LastWebsiteScraped != a['href']:
            LastWebsiteScraped = a['href']
            print("\nFound URL - " + a['href']) #+ "\nResult Number - " + str(links_raw.index(a)))
            page_source = get_page_source(("https://www.checkatrade.com" + a['href']))
            BusinessName = bs4.BeautifulSoup(str(page_source.find_all("div", "contact-card__details")), "html.parser")
            WebsiteToCheck = bs4.BeautifulSoup(str(page_source.find_all(id="ctl00_ctl00_content_ctlWeb2")), "html.parser")

            try:
                BusinessName = BusinessName.find_all('h1')[0].text.strip()
                WebsiteToCheck = WebsiteToCheck.find_all('a', href=True)[0].text.strip()
                if WebsiteChecks(WebsiteToCheck):
                    print(WebsiteToCheck + " has an issue.")
                    WriteToFile("Website Broken", BusinessName, WebsiteToCheck)

            except Exception as e:
                try:
                    print(BusinessName + " doesn't have a website.")

                    if WebsiteChecks(WebsiteToCheck):
                        print(WebsiteToCheck + " has an issue.")
                        WriteToFile("Website Broken", BusinessName, WebsiteToCheck)
                    else:
                        WriteToFile("No Website", BusinessName, ("https://www.checkatrade.com" + a['href']))
                        
                except Exception as e:
                    print(WebsiteToCheck + " has an issue.")
                    WriteToFile("Website Broken", BusinessName, We
                    print("Why.")
                    print (e)
        else:
            if a['href'] != LastWebsiteScraped:
                print("no href found")

def ScrapePagesAllocation(NumberOfPages):
    for i in range(1, (NumberOfPages + 1)):
        try:
            ScrapePages(i)
        except Exception as e:
            print(e)
            
    Runtime()

def Runtime():
    ScrapePagesAllocation(find_number_of_pages(get_page_source(generate_url(1, True)))) # Need to rotate between postcodes

Runtime()

