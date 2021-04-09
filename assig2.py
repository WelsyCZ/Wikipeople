import pywikibot as pw
from pywikibot import pagegenerators
import wikipeoplelib as wlib
from wikipeoplelib import enwiki, commons
import csv
import time
import mwparserfromhell as mw

folder = "testfolder/"
imgfolder = folder+"imgs/"

"""
all pages
1. image
2. sex
3. date of birth
4. image inception
5. image description
6. date of death
7. first sentence
get info from multiple sources where possible
"""

def timeGen(gen, maxpages, catname,exclude=None):
    print("Starting processing of at most",maxpages,"pages from",catname)
    start = time.time()
    total = 0
    images = 0
    excluded = 0
    with open(folder+catname+'.csv', "w", newline='', encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerow(["Name","Sex","Birthdate","Deathdate","ImageName","ImageDescription", "ImageDate"])
        for page in gen:
            if exclude:
                if exclude in page.title():
                    excluded += 1
                    continue
            total += 1
            if wlib.hasPageImage(page):
                images += 1
                img = wlib.getPageImage(page)
                infotemp = wlib.getInfoTemplate(img)
                desc = wlib.getDescription(infotemp)
                date = wlib.getDate(infotemp)
                #print("-----------------\n",page.title())
                desc = "NoDesc" if desc is None else str(desc).replace("\n","\\n")
                date = "NoDate" if date is None else str(date).replace("\n","\\n")
                item = page.data_item()
                item.get()
                sex = wlib.getSex(item)
                sex = "NoSex" if not sex else sex
                birthdate = wlib.getBirthDate(item)
                birthdate = "NoBirthDate" if not birthdate else birthdate
                deathdate = wlib.getDeathDate(item)
                deathdate = "NoDeathDate" if not deathdate else deathdate
                filename = img.title(as_filename=True, with_ns=False)
                filenameWithPath = imgfolder+filename
                #img.download(filename=filenameWithPath)
                writer.writerow([page.title(),sex,birthdate,deathdate,filename,desc,date])
                #break

            if total % 100 == 0:
                tm = time.time()
                print(total, "/", maxpages,"pages processed")
                print(tm-start,"s elapsed so far")
            
    end = time.time()
    print("total", total)
    print("images", images)
    print("excluded", excluded)
    print(100*images/total, "%")
    print("Time:", end-start,"s")
    return {"total":total,"images":images,"excluded":excluded,"%":100*images/total,"time":end-start}

def livingppl():
    prefix = 'Category:'
    catname = 'Living people'
    cat = pw.Category(enwiki,prefix+catname)
    sampleSize = 1000
    #sortkey = "!ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sortkey = "GHIJKLMNOPQRSTUVWXYZ"
    gen = wlib.uniformPageGenerator(cat, sampleSize, sortkey)
    total = len(sortkey)*sampleSize
    d = timeGen(gen, total,catname)
    d['name'] = catname
    return d

def deaths(year):
    prefix = 'Category:'
    catname = str(year)+'_deaths'
    cat = pw.Category(enwiki, prefix+catname)
    print(cat, cat.categoryinfo)
    sampleSize = 50
    sortkey = "!ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    gen = wlib.uniformPageGenerator(cat, sampleSize, sortkey)
    total = len(sortkey)*sampleSize
    d = timeGen(gen, total,catname,exclude=str(year))
    d['name'] = catname
    return d
    
def processYears():
    dicts = []
    for i in range(2020,1999,-1):
        dicts.append(deaths(i))
    with open(folder+"info.csv", "w", encoding="utf-8",newline='') as cf:
        writer = csv.writer(cf)
        writer.writerow(["category","total_pages", "has_image", "time_seconds"])
        for d in dicts:
            writer.writerow([d["name"],d["total"],d["images"],d["time"]])

if __name__ == "__main__":
    livingppl()
    """prefix = 'Category:'
    catname = 'Living people'
    cat = pw.Category(enwiki,prefix+catname)
    gen = cat.articles(startprefix="Gadkari")
    sortkey = "!ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    print(timeGen(gen,1000,catname))"""
    
    #deaths(2020)
