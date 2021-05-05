# -*- coding: utf-8 -*-
from inspire_api import get_result,get_result_ids,get_record
#import datetime
import os
import re
import time
from html import escape

#import pytz
#chicago_timezone = pytz.timezone('America/Chicago')



SERIES1 = ['thesis', 'misc', 'tm', 'fn', 'proposal',
           'workbook', 'bachelors', 'masters', 'design',
           'loi', 'eoi', 'pbar', 'nal', 'annual', 'upc',
           'ap', 'en', 'exp', 'lu', 'habil', 'vlhcpub',
           'slides', 'poster', 'code', 'crada']
SERIES2 = ['PUB', 'CONF']
SERIES1.sort()
SITE_URL = 'https://inspirehep.net'
CFG_FERMILAB_PATH = ''
ADMIN_EMAIL = 'cleggm1@fnal.gov'
errors = []

def get_author(report):
    search = 'ids.value:' + report[4]
    result = get_result_ids(search,collection='authors')
    if len(result) == 1:
        report[2] = '<a href="%(site)s/authors/%(recid)s">%(rep2)s</a>'\
                                % {'site': SITE_URL,
                                   'recid': str(result[0]),
                                   'rep2': report[2]}
    else:
        errors.append('HEP record: ' + report[4] + ' | Problem Id: ' + report[1] + \
                      ' | Number of results in HEPNames: ' + str(len(result)))
    return report

def get_collab(report):
    search = 'legacy_name:' + report[5]
#    result = get_result_ids(search,collection='experiments')
    result = get_result(search,fields=('collaboration',),collection='experiments')
    if len(result) == 1:
#        record = get_record(result[0])
        try:
            collaboration = result[0]['collaboration']['value']
            collaboration = collaboration.replace(' Collaboration','')
            report[5] = report[5] + ' (' + collaboration + ')'
            report[5] = '<a href="%(site)s/experiments/%(recid)s">%(rep5)s</a>' \
                        % {'site': SITE_URL,
                           'recid': str(result[0]['control_number']),
                           'rep5': report[5]}
        except KeyError:
            pass
    return report

def bst_fermilab():
    for series in SERIES1:
        reports = []
        authorId = False
        fields = ("authors","accelerator_experiments","report_numbers","titles",)
        result = get_result("d:2020 r:fermilab-" + series + "-*",fields=fields)
#        result = get_result_ids("d:2020 r:fermilab-" + series + "-*")
        for record in result:
            recid = str(record['control_number'])
            try:
                reportValues = [r['value'] for r in record['report_numbers']]
            except KeyError:
                reportValues = []
            try:
                author = record['authors'][0]['full_name']
            except KeyError:
                author = ''
            try:
                authorAff = record['authors'][0]['affiliations'][0]['value']
            except KeyError:
                authorAff = ''
            try:
                orcid = False
                ids = record['authors'][0]['ids']
                for id in ids:
                    if id['schema'] == 'orcid':
                        authorId = id['value']
                        orcid = True
                    elif id['schema'] == 'inspire_id' and not orcid:
                        authorId = id['value']
            except KeyError:
                 authorId = ''
            try:
                experiment = record['accelerator_experiments'][0]['value']
            except KeyError:
                experiment = ''
            try:
                title = record['titles'][0]['title'][:100]
                title = '<i>' + title + '</i>'
            except KeyError:
                title = ''
            for report in reportValues:
#                if re.match('FERMILAB-' + series, report['value'], re.IGNORECASE):
                if re.match('FERMILAB-' + series, report, re.IGNORECASE):
#                    y = [report['value'], recid, author, title, authorId, experiment, authorAff]
                    y = [report, recid, author, title, authorId, experiment, authorAff]
                    reports.append(y)
        reports.sort(reverse=True)
        filename = os.path.join(CFG_FERMILAB_PATH,
                                'fermilab-reports-' + series + '.html')
        output = open(filename, 'w')
        output.write('''

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Fermilab Technical Publications: %(series)s</title>
  <meta http-equiv="content-type" content="text/html;charset=utf-8" />
</head>
<body>
  <a href="https://ccd.fnal.gov/techpubs/tech-pubs-search.html">Fermilab Technical Publications</a>
  <br /><br /><i>Updated %(dateTimeStamp)s</i>
  <br />
  <table>''' % {'series': escape(series),
                'dateTimeStamp': time.strftime('%Y-%m-%d %H:%M:%S')})
#                'dateTimeStamp': chicago_timezone.fromutc(
#                    datetime.datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S')})
        for report in reports:
            if report[4]:
                report = get_author(report)
            line = '''
    <tr>
      <td><a href="%(site)s/literature/%(rep1)s">%(rep0)s</a></td>
      <td>%(rep2)s</td>
      <td>%(rep3)s</td>
    </tr>''' % {'site': SITE_URL,
                'rep0': report[0],
                'rep1': report[1],
                'rep2': report[2],
                'rep3': report[3]}
            if re.search(r'THESIS|MASTERS|BACHELORS', report[0]):
                if report[5]:
                    report = get_collab(report)
                line = '''
    <tr>
      <td><a href="%(site)s/literature/%(rep1)s">%(rep0)s</a></td>
      <td>%(rep2)s</td>
      <td>%(rep5)s</td>
      <td>%(rep6)s</td>
      <td>%(rep3)s</td>
    </tr>''' % {'site': SITE_URL,
                'rep0': report[0],
                'rep1': report[1],
                'rep2': report[2],
                'rep3': report[3],
                'rep5': report[5],
                'rep6': report[6]}
            output.write(line)
        output.write('''
  </table>
</body>
</html>
''')
        output.close()
#        write_message('\\rm fermilab-reports-' + series + '.html')
#        write_message('cp %s .' % filename)

    reports = []
    for series in SERIES2:
        for year in range(1970, time.localtime()[0]+1):
            dd = str(year)
            dd = re.sub(r"19", "", dd)
            dd = re.sub(r"20", "", dd)
            fields = ("report_numbers","authors","titles",)
#            result = get_result_ids("r:fermilab-" + series + "-" + dd + "*")
            result = get_result("r:fermilab-" + series + "-" + dd + "*",fields=fields)
            for record in result:
                recid = str(record['control_number'])
                try:
                    reportValues = record['report_numbers']
                except KeyError:
                    reportValues = []
                try:
                    author = record['authors'][0]['full_name']
                except KeyError:
                    author = ''
                try:
                    title = record['titles'][0]['title'][:100]
                    title = '<i>' + title + '</i>'
                except KeyError:
                    title = ''
                for report in reportValues:
#                    print(report)
                    if re.match('FERMILAB-' + series, report['value'], re.IGNORECASE):
                        number = re.sub("FERMILAB-" + series + "-", "", report['value'])
                        y = [year, number, report['value'], recid, author, title]
                        reports.append(y)
    reports.sort(reverse=True)
    filename = os.path.join(CFG_FERMILAB_PATH, 'fermilab-reports-preprints.html')
    output = open(filename, 'w')
    output.write('''
<html>
<header>
<title>Fermilab Technical Publications: preprints</title>
</header>
<body>
  <a href="https://ccd.fnal.gov/techpubs/tech-pubs-search.html">Fermilab Technical Publications</a>
  <br /><br /><i>Updated %(dateTimeStamp)s</i>
  <br />
  <table>
''' % {'dateTimeStamp': time.strftime('%Y-%m-%d %H:%M:%S')})
    for report in reports:
        line = '''
    <tr>
        <td><a href="%(site)s/literature/%(rep3)s">%(rep2)s</a></td>
        <td>%(rep4)s</td><td>%(rep5)s</td>
    </tr>
        ''' % {'site': SITE_URL,
               'rep2': report[2],
               'rep3': report[3],
               'rep4': report[4],
               'rep5': report[5]}
        output.write(line)
    output.write('''
  </table>
</body>
</html>
''')
    output.close()
#    write_message('cd /afs/fnal.gov/files/expwww/bss/html/techpubs')
#    write_message('\\rm fermilab-reports-preprints.html')
#    write_message('cp %s .' % filename)

    if errors:
        send_notification_email(errors)

def send_notification_email(errorlist):
    """Notify on errors by mail."""
#    emails = 'cleggm1@fnal.gov,hoc@fnal.gov'
    emails = 'cleggm1@fnal.gov'

    msg_html = """<p>Message from BibTasklet bst_fermilab:</p>
<p>Problems have occurred in %d author identifier(s):'</p>

""" % (len(errorlist))
    for e in errorlist:
        msg_html += e + "<br>"
    send_email(fromaddr=ADMIN_EMAIL, toaddr=emails,
               subject="Issues from BibTasklet bst_fermilab", html_content=msg_html)

if __name__ == "__main__":
    bst_fermilab()

