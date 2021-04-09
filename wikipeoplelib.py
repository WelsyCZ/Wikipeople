import pywikibot as pw
import mwparserfromhell as mw

enwiki = pw.Site("en", "wikipedia")
commons = pw.Site("commons", "commons")


def hasPageImage(page):
    """
    Check if a page has a pageimage 
    :param page: Page object to be checked for page image
    :return: hasImg (boolean) - True if page has a page image, False otherwise
    """
    return page.page_image() is not None

def getPageImage(page):
    """
    Check if a page has a pageimage and return it
    :param page: Page object to be checked for page image
    :return: page image of specified page
    """
    img = page.page_image()
    if img.file_is_shared():
        img = pw.FilePage(img.site.image_repository(), img.title())
    return img

def uniformPageGenerator(category, sampleSize = 10, sortkey = "!ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    """
    Generator, yields sampleSize(=10) pages starting with each letter of sortkey from the specified category
    :param category: The category from which the pages are yielded
    :param sampleSize: The number of pages yielded for each letter from sortkey
    :param sortkey: For each letter in sortkey, pages will be yielded from category
    """
    size = len(sortkey)
    for i in range(size):
        start = sortkey[i]
        end = None if i+1 >= size else sortkey[i+1]
        gen = category.articles(total = sampleSize, startprefix=start, endprefix=end)
        yield from gen

def getInfoTemplate(filepage):
    """
    Parse filepage text into templates (formatted text objects within curly braces)
    and return the Information template, which contains image description, date and other info
    :param filepage: existing filepage of specified image
    :return: Parsed Information template with
    """
    templates = mw.parse(filepage.text).filter_templates()
    infolist = [t for t in templates if "Information" in t]
    if len(infolist) < 1:
        return None
    return infolist[0]

def getDescription(infotemplate):
    """
    Retrieve the description attribute from image summary template
    :param infotemplate: The Information template of said image
    :return date: Contents of description attribute, None otherwise
    """
    if not infotemplate:
        return None
    paramNames = list(map(lambda x: x.name, infotemplate.params))
    if("Description" in paramNames):
        desc = infotemplate["Description"]
    elif("description" in paramNames):
        desc = infotemplate["description"]
    else:
        desc = None
    return desc

def getDate(infotemplate):
    """
    Retrieve the date attribute from image summary template
    :param infotemplate: The Information template of said image
    :return date: Contents of date attribute, None otherwise
    """
    if not infotemplate:
        return None
    paramNames = list(map(lambda x: x.name, infotemplate.params))
    if("Date" in paramNames):
        date = infotemplate["Date"]
    elif("date" in paramNames):
        date = infotemplate["date"]
    else:
        date = None
    return date

def getSex(item):
    """
    Retrieve persons sex from their wikidata itempage
    :param item: ItemPage object of said person on wikidata
    :return: sex in a string, None if no sex was found
    """
    
    # get the persons wikidata page, the wikipedia page does not always contain the sex
    sex = None
    if item and item.claims:
        # Property 21 (P21) is sex/gender
        if "P21" in item.claims:
            try:
                target = item.claims["P21"][0].getTarget()
                sex = target.text["labels"]["en"]
            except Exception as e:
                print(e)
            except Error as e:
                print(e)
    return sex

def getBirthDate(item):
    """
    Retrieve persons birth date from their wikidata itempage
    :param item: ItemPage object of said person on wikidata
    :return: YY-mm-dd birthdate string, None if no date was found
    """
    # get the persons wikidata page, the wikipedia page does not always contain the birthdate
    birthdate = None
    if item and item.claims:
        # Property 569 (P569) is the birth_date
        if "P569" in item.claims:
            try:
                target = item.claims["P569"][0].getTarget()
                if(target):
                    birthdate = target.toTimestamp().strftime("%Y-%m-%d")
            except Exception as e:
                print(e)
    return birthdate

def getDeathDate(item):
    """
    Retrieve persons deathdate from their wikidata itempage
    :param item: ItemPage object of said person on wikidata
    :return: YY-mm-dd deathdate string, None if no date was found
    """
    # get the persons wikidata page, the wikipedia page does not always contain the deathdate
    
    deathdate = None
    if item and item.claims:
        # Property 570 is the death_date
        if "P570" in item.claims:
            try:
                target = item.claims["P570"][0].getTarget()
                if(target):
                    deathdate = target.toTimestamp().strftime("%Y-%m-%d")
            except Exception as e:
                print(e)
    return deathdate