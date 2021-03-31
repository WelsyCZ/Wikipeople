import pywikibot as pw

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
    return page.page_image()

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