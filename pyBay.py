#!/usr/bin/python3

import requests
import argparse
from bs4 import BeautifulSoup as BS
import re
from functools import reduce

# Don't forget to add the / at the end
sites=[
    "https://piratebaylive.online/",
    "https://piratebaylive.com/",
    "https://pirateproxy.live/"
]

search_options = {
    "Audio" :   [ ('101', 'Music'), ('102', 'Audio books'), ('103', 'Sound clips'), ('104', 'FLAC'), ('199', 'Other') ],
    "Video" :   [ ('201', 'Movies'), ('202', 'Movies DVDR'), ('203', 'Music videos'), ('204', 'Movie clips'), ('205', 'TV shows'), ('206', 'Handheld'), ('207', 'HD - Movies'), ('208', 'HD - TV shows'), ('209', '3D'), ('299', 'Other') ],
    "App"   :   [ ('301', 'Windows'), ('302', 'Mac'), ('303', 'UNIX'), ('304', 'Handheld'), ('305', 'IOS (iPad/iPhone)'), ('306', 'Android'), ('399', 'Other OS') ],
    "Games" :   [ ('401', 'PC'), ('402', 'Mac'), ('403', 'PSx'), ('404', 'XBOX360'), ('405', 'Wii'), ('406', 'Handheld'), ('407', 'IOS (iPad/iPhone)'), ('408', 'Android'), ('499', 'Other')],
    "Porn"  :   [ ('501', 'Movies'), ('502', 'Movies DVDR'), ('503', 'Pictures'), ('504', 'Games'), ('505', 'HD - Movies'), ('506', 'Movie clips'), ('599', 'Other')],
    "Other" :   [ ('601', 'E-books'), ('602', 'Comics'), ('603', 'Pictures'), ('604', 'Covers'), ('605', 'Physibles'), ('699', 'Other')]
}


DEGUB = False

def build_search_pattern(txt,option):
    ret_str = "search?q="
    for i in txt.strip():
        if( i != ' ' and not i.isalnum() ):
            ret_str+="%"+hex(ord(i))[-2:].upper()
        else:
            ret_str+=i
    ret_str = ret_str.replace(" ","+")

    if not option:
        option = 0

    ret_str+="&cat="+str(option)
    return ret_str


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o","--option", help="Pass the option number.")
    parser.add_argument("-v","--view_options",help="View available options.",action="store_true")
    parser.add_argument("-s","--search",help="Search string enclosed in \" \"")
    return parser.parse_args()
       


def print_options():
    for k,v in search_options.items():
        print(k)
        for i in v:
            print("\t{}\t:{}".format(i[0],i[1]))


def print_search_results(url):
    resp = requests.get(url)

    if DEGUB:
        with open("page.html","w") as f:
            f.write(resp.text)

    soup = BS(resp.text,"lxml")
    ol = soup.find("ol", {"id":"torrents"})
    li = ol.find_all("li",{"class":"list-entry"})

    for i in li:
        magnet = i.find("a",{"class":"js-magnet-link"})
        link = re.findall(r'href="(.*?)"',str(magnet))

        x = i.find_all("span",{"class":"list-item"})

        categories = re.findall(r'title="(.*?)"',str(x[0]))
        name = re.findall(r'<a\s.*?">(.*?)</a>',str(x[1]))
        upload_date = re.findall(r'\d{4}-\d{2}-\d{2}',str(x[2]))
        size = re.findall(r'<span\s.*?>(.*?)<',str(x[3]))
        seeders = re.findall(r'<span\s.*?>(\d+)</span>',str(x[4]))
        leachers = re.findall(r'<span\s.*?>(\d+)</span>',str(x[5]))


        print("Category: {} \n Name: {} \n Upload Date: {} \n Seeders: {} \n Leachers: {} \n Size: {} \n Magnet: {} \n -------------------------------------------------------".format(
                reduce(lambda x,y:x+" "+y, categories if categories else ["None"]),
                name[0],
                upload_date[0],
                seeders[0],
                leachers[0],
                size[0],
                link[0] if categories else None
            )
        )

def main():
    args = get_args()
    if args.view_options:
        print_options()

    if not args.search:
        print("Need to pass search string. Use -h for help.")
        exit()

    search_str = build_search_pattern(args.search,args.option)
    for i in sites:
        try:
            url = i+search_str
            print_search_results(url)
            break
        except requests.exceptions.ConnectionError:
            continue    


main()