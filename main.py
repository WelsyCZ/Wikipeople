import pywikibot as pw
from pywikibot import pagegenerators
import mwparserfromhell as mw
import re
from person import Person
import sqlite3
from sqlite3 import Error

"""
**notes**
1. sex/gender? male/female/trans-male/trans-female?
2. saving links/actual image content
3. rating data reliability

**todos**
1. Currently the script can not resume once it has been stopped
TODO: implement resume capability
https://doc.wikimedia.org/pywikibot/master/_modules/pywikibot/pagegenerators.html - CategorizedPageGenerator
"""

enwiki = pw.Site("en", "wikipedia")
commons = pw.Site("commons", "commons")

noexist = 0
noimage = 0
nodate = 0
nobirthdate = 0
noclaims = 0
dateDescDiscrepancies = 0
multipleDates = 0
nosex = 0

def processPage(pageobj, title=False):
    """
    Retrieve the required parameters from specified wikipedia page

    :param pageobj: pywikibot.Page object to be processed, 
                    if title is True, pageobj is only the pagetitle (str)
    :param title: if True, pageobj will be interpreted as a string containing the page title

    :return: Person object with all the required parameters, 
             None if some were not found
    """
    global nodate, noexist, noimage, dateDescDiscrepancies, multipleDates
    if title:
        # get the page object from the title string
        page = pw.Page(enwiki, pageobj)
    else:
        # get the page title from the page object
        page = pageobj
        pagename = page.title()
    #print("--------------------------------------------------\n", pagename)
    
    # Processing part
    if not page:
        noexist += 1
        return None
    hasImg, img = getPageImage(page)
    # pages without images are of no use, skip the page
    if not hasImg:
        noimage += 1
        return None
    # determine the location of the page image (either wikipedia:en or commons)
    if not img.exists():
        fpage = pw.FilePage(commons, img.title())
    else:
        fpage = pw.FilePage(enwiki, img.title())
    
    imgUrl = fpage.get_file_url()
    pagelink = page.permalink()
    
    if(pagelink[:2] == "//"):
        pagelink = pagelink[2:]
    # get the year in which the page image was taken (to determine the age on the photo)
    date = getImageDate(fpage)
    # not dated images are of no use to us, skip the page
    if not date:
        nodate += 1
        return None
    birthDate = getBirthDate(page)
    sex = getSex(page)
    # both sex and birthDate are required
    if not birthDate or not sex:
        return None
    p = Person(pagename, pagelink, imgUrl, date, birthDate, sex, page.pageid)
    return p

def getSex(page):
    """
    Retrieve persons sex from their wikidata page

    :param page: Page object of said person

    :return: sex in a string, None if no sex was found
    """
    global nosex, noclaims
    
    # get the persons wikidata page, the wikipedia page does not always contain the sex
    item = page.data_item()
    item.get()
    if item.claims:
        # Property 21 (P21) is sex/gender
        if "P21" in item.claims:
            target = item.claims["P21"][0].getTarget()
            return target.text["labels"]["en"]
        else:
            nosex += 1
    else:
        noclaims += 1
    return None

def getBirthDate(page):
    """
    Retrieve persons birth date from their wikidata page

    :param page: Page object of said person

    :return: YY-mm-dd birthdate string, None if no date was found
    """
    global nobirthdate, noclaims

    # get the persons wikidata page, the wikipedia page does not always contain the birthdate
    item = page.data_item()
    item.get()
    if item.claims:
        # Property 569 (P569) is the birth_date
        if "P569" in item.claims:
            return item.claims["P569"][0].getTarget().toTimestamp().strftime("%Y-%m-%d")
        else:
            nobirthdate += 1
    else:
        noclaims += 1
    return None

def getImageDate(filepage):
    """
    Retrieve the original year the pageimage was taken (created)

    :param filepage: FilePage object of specified page image

    :return: year the pageimage was taken (created), None if no year was found
    """
    global dateDescDiscrepancies, multipleDates
    # parse the structured data provided with the pageimage
    templates = mw.parse(filepage.text).filter_templates()
    # The information segment usually contains the desired date
    infolist = [t for t in templates if "Information" in t]
    if len(infolist) < 1:
        return None
    info = infolist[0]
    dateMatches, descMatches = None, None
    # capital letters differ page by page, need to check all possibilities
    dateparam = "Date" if info.has_param("Date") else ("date" if info.has_param("date") else None)
    descparam = "Description" if info.has_param("Description") else ("description" if info.has_param("description") else None)
    dateMatch, descMatch = None, None
    # check for a "date" parameter, which should contain the desired date
    # we check the date with a simple regexp, we accept the match if all matches are equal
    if dateparam:
        dateMatches = re.findall(r"\d{4}", str(info[dateparam]))
        if(len(dateMatches) > 1):
            multipleDates+=1
        # some users use the "date" param to supply the upload date, which is not desired
        if not(len(dateMatches) < 1 or len(re.findall(r"upload",str(info[dateparam]))) > 0):
            dateMatch = dateMatches[0]
    # the pageimage description could also contain the desired date
    if descparam:
        descMatches = re.findall(r"\d{4}", str(info[descparam]))
        if(len(descMatches) > 1):
            # check if all matches are equal
            if(all(descMatches[0] == x for x in descMatches)):
                descMatch = descMatches[0]
        elif(len(descMatches) == 1):
            descMatch = descMatches[0]
    if dateMatch and descMatch and dateMatch != descMatch:
        dateDescDiscrepancies += 1
    return dateMatch

    

def getPageImage(page):
    """
    Check if a page has a pageimage and if so, return it

    :param page: Page object to be checked for page image

    :return: hasImg (boolean) - True if page has a page image, False otherwise
             pageImage (Page object) - Page object of the page image (different from param page)
    """
    return page.page_image() is not None, page.page_image()

def connToDB(filename):
    """
    Create a connection to the database

    :param filename: Filename of the database we connect to

    :return: conn - connection object used to access the database
    """
    conn = None
    try:
        conn = sqlite3.connect(filename)
        return conn
    except Error as e:
        print(e)
    return conn

def createDBtable(conn, tableSchema):
    """
    Create a table in the database according to the provided schema

    :param conn: Connection used to control the database
    :param tableSchema: SQL schema used to create the DB table
    """
    try:
        c = conn.cursor()
        c.execute(tableSchema)
    except Error as e:
        print(e)

def insertIntoDB(conn, persona):
    """
    Insert a person into the database

    :param conn: Connection used to control the database
    :param persona: Person object containing all the required parameters

    :return: ID of the inserted person, -1 if DB already contains said person
    """
    # check if DB already contains the person
    checkquery = """
            SELECT * FROM people WHERE pageid = ?;
    """
    cur = conn.cursor()
    cur.execute(checkquery, [persona.pageid])
    rows = cur.fetchall()
    if(len(rows) > 0):
        return -1
    # insert the person
    query = """
        INSERT INTO people(pagename, birthdate, sex, pagelink, imagelink, imagedate, pageid)
        VALUES(?,?,?,?,?,?,?)
        """
    try:
        cur.execute(query, persona.toDB())
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(e)
        print(persona)

if __name__ == "__main__":
    # category object and a generator to iterate over said category
    cat = pw.Category(enwiki,'Category:Living people')
    gen = pagegenerators.CategorizedPageGenerator(cat, start="Abbas")
    # database init
    dbfilename = "first10k.db"
    conn = connToDB(dbfilename)
    sqlTableSchema = """
                CREATE TABLE IF NOT EXISTS people(
                    id integer PRIMARY KEY NOT NULL,
                    pagename text NOT NULL,
                    birthdate text NOT NULL,
                    sex text NOT NULL,
                    pagelink text NOT NULL,
                    imagelink text NOT NULL,
                    imagedate text NOT NULL,
                    pageid integer UNIQUE NOT NULL
                )"""
    createDBtable(conn, sqlTableSchema)

    # Iterate over the category (maximum numPages), insert anything returned to the database
    i = 0
    numPages = 10000 # 500 took 337s, avg 0.67s per page
    printnext = False
    for page in gen:
        if i % 50 == 0:
            print("{0}/{1}".format(i,numPages))
            printnext = True
        p = processPage(page)
        if p:
            insertIntoDB(conn, p)
            if printnext:
                print(p.title)
                printnext = False
            
        if i > numPages:
            break
        i += 1

    # Output a simple statistic
    print("noexist",noexist)
    print("noimage",noimage)
    print("nodate", nodate)
    print("nobirthdate", nobirthdate)
    print("nosex", nosex)
    print("noclaims",noclaims)
    print("multiple dates", multipleDates)
    print("Date and Description Discrepancies", dateDescDiscrepancies)