import pywikibot as pw
from pywikibot import pagegenerators
import wikipeoplelib as wlib
from wikipeoplelib import enwiki, commons
import time
import csv
import matplotlib.pyplot as plt
import numpy as np

folder = "csvs/"

def timeGen(gen, maxpages, catname,exclude=None):
    print("Starting processing of at most",maxpages,"pages from",catname)
    start = time.time()
    with open(folder+catname+'.csv', "w", newline='', encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerow(["Pagename", "hasImage(bool)"])
        images = 0
        total = 0
        excluded = 0
        for page in gen:
            if exclude:
                if exclude in page.title():
                    excluded += 1
                    continue
            row = [page.title(), "False"]
            total += 1
            if wlib.hasPageImage(page):
                images+=1
                row[1] = "True"
            writer.writerow(row)
            if total % 100 == 0:
                print(total, "/", maxpages,"pages processed")
            
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
    sampleSize = 50
    sortkey = "!ABCDEFGHIJKLMNOPQRSTUVWXYZ"
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

def countPages(years):
    pref = "Category:"
    suff ="_deaths"
    pages = []
    for i in years:
        catname = pref + str(i) + suff
        cat = pw.Category(enwiki,catname)
        cinfo = cat.categoryinfo
        pages.append(cinfo["pages"])
    return pages

def graphs():
    rawdata = np.genfromtxt("csvs/info.csv",delimiter=",", dtype=None,encoding="utf-8")
    data = rawdata[1:]
    labels = range(2020,1999,-1)
    #pages = countPages(list(labels))
    # zkopírovaný seznam počtů stránek kvůli opakovanému spouštění scriptu
    pages = [11414, 9192, 9209, 9212, 9302, 9430, 9271, 9018, 8551, 8411, 8608, 8368, 8204, 7851, 7561, 7194, 6749, 6654, 6428, 6216, 6057]
    #print(pages)
    evaledPages = np.array(data[:,1],dtype=int)
    images = np.array(data[:,2],dtype=int)
    percent = 100*images/evaledPages
    percent = np.array([round(x,2) for x in percent])
    print(percent)
    print(min(percent))
    print(max(percent))
    print(np.average(percent, weights=evaledPages))

    fig1, axs1 = plt.subplots(2,constrained_layout=True)
    axs1[0].bar(labels,pages)
    axs1[0].set_title("Total number of pages in categories")
    ylims0 = [np.min(pages)-1000,np.max(pages)+1000]
    axs1[0].set_ylim(ylims0)
    axs1[0].set_xlabel("Year")
    axs1[0].set_ylabel("Total pages")
    
    axs1[1].bar(labels,evaledPages,color="green")
    axs1[1].set_title("Number of pages evaluated")
    ylims1 = [np.min(evaledPages)-10,np.max(evaledPages)+10]
    axs1[1].set_ylim(ylims1)
    axs1[1].set_xlabel("Year")
    axs1[1].set_ylabel("Evaluated pages")

    fig2, axs2 = plt.subplots(2,constrained_layout=True)
    axs2[0].bar(labels,percent,color="orange")
    axs2[0].set_title(r"% of evaluated pages containing an image")
    ylims2 = [np.min(percent)-5,np.max(percent)+5]
    axs2[0].set_ylim(ylims2)
    axs2[0].set_xlabel("Year")
    axs2[0].set_ylabel(r"% of pages with img")

    bins = list(range(0,101,5))
    n, _, _ = axs2[1].hist(percent,bins=bins,color="pink")
    axs2[1].set_title(r"Histogram - % of eval. pages with images")
    ylims3 = [np.min(n),np.max(n)+2]
    axs2[1].set_ylim(ylims3)
    axs2[1].set_xlabel("Percentage of pages with images")
    axs2[1].set_ylabel("Occurences")
    fig1.savefig("figures/pages.png")
    fig2.savefig("figures/percentages.png")
    plt.show()

def graphYears(years):
    labels = list(years)
    #pages = countPages(years)
    pages = [11417, 9192, 9211, 9213, 9302, 9431, 9271, 9021, 8551, 8411, 8608, 8368, 8206, 7853, 7561, 7195, 6749, 6655, 6428, 6218, 6059, 6184, 5880, 5765, 
5797, 5816, 5693, 5731, 5505, 5155, 5308, 5196, 5068, 5013, 5036, 5031, 4830, 4793, 4747, 4772, 4740, 4655, 4472, 4599, 4506, 4541, 4378, 4550, 4485, 4621, 4564, 4477, 4480, 4344, 4289, 4076, 4053, 4007, 3981, 3783, 3867, 3539, 3654, 3630, 3683, 3455, 3334, 3375, 3298, 3367, 3383, 3379, 3320, 3364, 3389, 4536, 4759, 4175, 4169, 3805, 3537, 3302, 3369, 3440, 3099, 2892, 2892, 2919, 2766, 2676, 2666, 2835, 2594, 2529, 2353, 2402, 2505, 
2277, 2317, 2298, 2350, 2491, 3091, 2713, 2679, 2616, 2190, 2087, 2084, 1989, 2001, 1911, 1978, 1898, 1749, 1911, 1822, 1860, 1781, 1854, 1858]
    print(pages)
    fig, ax = plt.subplots(1)
    ax.bar(labels, pages)
    ax.set_title("Number of pages in <Year>_deaths categories")
    ax.set_xlabel("Year")
    ax.set_ylabel("Numpages")
    fig.savefig("figures/pages1900-2020.png")
    plt.show()


if __name__ == "__main__":
    graphYears(range(2020,1899,-1))
    
    