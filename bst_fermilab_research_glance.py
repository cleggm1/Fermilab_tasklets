#!/usr/bin/python
# -*- coding: utf-8 -*-
#2021

from inspire_api import get_result_ids
import time
from datetime import datetime
#import datetime
import re
#from StringIO import StringIO
from io import StringIO
from os.path import join

from dateutil.relativedelta import relativedelta
from lxml import etree
import lxml.html
from lxml.html import builder as E

#import pytz

CFG_FERMILAB_PATH = ""
CFG_SITE_SECURE_URL = "https://inspirehep.net/literature/"
#CHICAGO_TIMEZONE = pytz.timezone('America/Chicago')
#NOW = CHICAGO_TIMEZONE.fromutc(datetime.datetime.utcnow())
NOW = datetime.now()
DATE_TIME_STAMP = NOW.strftime('%Y-%m-%d %H:%M:%S')
#NOW = time.strftime('%Y-%m-%d %H:%M:%S')
#DATE_TIME_STAMP = time.strftime('%Y-%m-%d %H:%M:%S')

MONTH = NOW.strftime('%Y-%m')
#MONTH = time.strftime('%Y-%m')
#MONTH_1 = (time.strftime + relativedelta(months=-1)).strftime('%Y-%m')
#MONTH_2 = (time.strftime + relativedelta(months=-2)).strftime('%Y-%m')
MONTH_1 = (NOW + relativedelta(months=-1)).strftime('%Y-%m')
MONTH_2 = (NOW + relativedelta(months=-2)).strftime('%Y-%m')

YEAR = str(NOW.year)
YEAR_1 = str(NOW.year - 1)
YEAR_2 = str(NOW.year - 2)
#YEAR = str(time.strftime('%Y'))
#YEAR_1 = str(time.strftime('%Y' - 1))
#YEAR_2 = str(time.strftime('%Y' - 2))


def create_table():
    """HTML generation by lxml.html tree."""

    divisions = ['All', 'E', 'CMS', 'T', 'A', 'AE', 'PPD', 'AD/APC',
                 'TD', 'CD', 'CCD', 'OCIO', 'SCD', 'ND', 'LBN', 'Other']
    pubtypes = ['All', 'PUB', 'THESIS', 'CONF', 'TM', 'FN', 'SLIDES', 'POSTER', 'CODE', 'CRADA']
    dates = [YEAR_2, YEAR_1, YEAR, MONTH_2, MONTH_1, MONTH]
    years = [YEAR_2, YEAR_1, YEAR]
    months = [MONTH_2, MONTH_1, MONTH]

    # This is a doctype work around for a lxml.etree bug
    doctype_wa = etree.parse(StringIO('''<!DOCTYPE html>\n<html>\n</html>'''))
    head_tag = E.HEAD(
        E.META({'charset': 'utf-8'}),
        E.TITLE("FERMILAB RESEARCH AT A GLANCE"),
        E.STYLE(
            {'type': 'text/css'},
            "td {text-align: right;}",
            " td.l {text-align: left;padding: 7px;}",
            " a.t {display: block;}"
        )
    )
    body = E.BODY(E.P(
        E.A("Fermilab Technical Publications",
            href="http://ccd.fnal.gov/techpubs/fermilab_spires.html")
    ))
    tag_h3 = E.H3("FERMILAB RESEARCH AT A GLANCE")
    tag_p = E.P("Glossary at end.")
    tag_p_and_i = E.P(E.I("Updated: " + DATE_TIME_STAMP))

    body.append(tag_h3)
    body.append(tag_p)
    body.append(tag_p_and_i)
    table = E.TABLE()

    tag_tr_td = E.TR(E.TD, E.TD("Date"))
    for division in divisions:
        if division == 'A':
            division = 'AT'
        tag_tr_td.append(E.TD(division))
    table.append(tag_tr_td)

    pub_table_row = E.TR()
    for pubtype in pubtypes:
        pub_table_row.append(E.TD(pubtype))
        pub_type_datelist = E.TD()
        year_list = E.UL()
        month_list = E.UL()
        for year in years:
            year_list.append(E.LI(year))
        for month in months:
            month_list.append(E.LI(month))
        pub_type_datelist.append(year_list)
        pub_type_datelist.append(month_list)
        pub_type_datelist.append(E.UL())
        pub_table_row.append(pub_type_datelist)
        pub_type_datelist = E.TD()

        for division in divisions:
            tdg = E.TD()
            list_of_searches = E.UL()
            for date in dates:
                if division == 'All':
                    division = ''
                if pubtype == 'All':
                    pubtype = ''
                search = 'r:fermilab-' + pubtype + '-*'
                if division == 'Other':
                    for good_division in divisions[1:len(divisions)-1]:
                        if good_division == 'AD/APC':
                            search += ' not  (r AD or APC)'
                        else:
                            search += ' not r ' + good_division
                elif division == 'AD/APC':
                    search = 'find r fermilab ' + pubtype + \
                             ' and (r AD or APC)'
                else:
                    search += ' ' + division
                search += ' and de ' + date
                search = re.sub(r'\s+', ' ', search)
                result = get_result_ids(search)
#                result = perform_request_search(p=search, cc="Fermilab")
                result = len(result)
                if result == 0:
                    hit_number = E.LI()
                else:
                    link = search.replace(' ', '+')
                    link = CFG_SITE_SECURE_URL + '/?sort=mostrecent&size=100&page=1&q=' + link
                    hit_number = E.LI(E.A({'class': 't'}, str(result),
                                          href=link))
                list_of_searches.append(hit_number)
                if date == YEAR or date == MONTH:
                    tdg.append(list_of_searches)
                    list_of_searches = E.UL()

            pub_table_row.append(tdg)

        table.append(pub_table_row)
        pub_table_row = E.TR()
    glos = E.H4('Glossary')
    table2 = E.TABLE()
    glos_tr_td = E.TR(
        E.TD({'class': 'l'}, "E: Experimental papers"),
        E.TD({'class': 'l'}, "PPD: Particle Physics Division papers")
    )
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, "T: Particle Physics Division \
Theoretical Physics Department papers"),
                      E.TD({'class': 'l'}, "AD/APC: Accelerator Division \
and Accelerator Physics Center papers"))
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, "AT: Fermilab Center for Particle \
Astrophysics theoretical papers"),
                      E.TD({'class': 'l'}, "TD: Technical Division papers"))
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, "AE: Fermilab Center for Particle \
Astrophysics experimental papers"),
                      E.TD({'class': 'l'}, "CD: Computing Sector papers (up to \
2019-08-16, now split into CCD, SCD and OCIO)"))
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, "CCD: Core Computing Division papers \
(starting 2019-08-16; previously labeled CD)"),
                      E.TD({'class': 'l'}, "OCIO: Office of the Chief Information \
Officer papers (starting 2019-08-16; previously labeled CD)"))
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, "SCD: Scientific Computing Division \
papers (starting 2019-08-16; previously labeled CD)"),
                      E.TD({'class': 'l'}, "ND: Neutrino Division papers"))
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, "LBN: Long Baseline Neutrino \
Sector papers"))
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, " "), E.TD({'class': 'l'}, " "))
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, " "), E.TD({'class': 'l'}, " "))
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, " "), E.TD({'class': 'l'}, " "))
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, "PUB: Paper intended for \
publication in a journal"),
                      E.TD({'class': 'l'}, "FN: Physics note - short paper not \
fitting the other categories"))
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, "CONF: Paper written as part of a \
conference"),
                      E.TD({'class': 'l'}, "SLIDES: Slides presented at a \
conference or lecture"))
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, "THESIS: Ph.D. thesis based on \
work done at Fermilab"),
                      E.TD({'class': 'l'}, "POSTER: Poster presented at a \
conference"))
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, "TM: Technical memo"),
                      E.TD({'class': 'l'}, "CODE: Software code"))
    table2.append(glos_tr_td)
    glos_tr_td = E.TR(E.TD({'class': 'l'}, "CRADA: Cooperative Research and \
Development Agreement"))
    table2.append(glos_tr_td)


    body.append(table)
    body.append(glos)
    body.append(table2)
    doctype_wa.getroot().append(head_tag)
    doctype_wa.getroot().append(body)
    print(type(doctype_wa))
#    out = lxml.html.tostring(doctype_wa, encoding='UTF-8', pretty_print=True,
#                            method='html').rstrip(b'\n')
    out = lxml.html.tostring(doctype_wa, encoding='UTF-8', pretty_print=True,
                            method='html').decode('utf-8').rstrip('\n')
    return out

def bst_fermilab_research_glance():
    """Writes html product to file with extension html."""

    filename = 'fermilab_research_glance.html'
    filename_w = join(CFG_FERMILAB_PATH, filename)
    table = create_table()
    with open(filename_w, 'w') as output:
        output.write(table)

if __name__ == '__main__':
    try:
        bst_fermilab_research_glance()
    except KeyboardInterrupt:
        print('Exiting')


