import os, sys
import errno
import json
import urllib3.request
import urllib.parse
import certifi
import requests
import nuvpy.nuviot_srvc as nuviot_srvc
import re

import datetime
import pandas as pd

def init(output_dir):
    """
    Initialize the report builder by passing in the directory where the output files 
    will be saved.

    Parameters
    ----------

    output_dir:
        directory where output files will be saved 

    """
    try:
        os.makedirs(output_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

def add_generated_report_header(report_header):
    """
    Upload report history and return the id of the header that was generated
    on the server.

    Parameters
    ----------
    
    report_header:
        Required Parmeters:
        A dictionary of parameters that will be used to describe the report that consist of:
        - report: Name of the report
        - executionTimeMS: The number of milliseconds it took to generate the report
        - scheduled: True if the report was scheduled, false if it was not
        - note: Any notes to be added to the report
        - user: An Entity Header (dictionary of id and text) of the user (which could be a system user) that requested the report.
        - contentType: Mime type of the report, generally this is application/pdf
        - fileName: name of the file (not including the path) of the report
        - reportTitle: tile of the report as it was generated
        Optional Parameters
        - reportSummary: report summary as returned from the generatred report
        - reportDate: date of for the report
        - device: An Entity Header (dictionary of id and text) of the device that this report is for, if this is provided reports for specific devices will be available in the dashboard
    
    Returns
    -------
    
    out: string
        Returns the id of the generated report that can be used to upload a report.
    
    """
    job_server = os.environ.get('JOB_SERVER_URL')
    if(job_server is None):
        raise Exception("Missing environment variable [JOB_SERVER_URL]")

    headers={'Content-Type':'application/json'}
    
    generated_report_json = json.dumps(report_header)
    url = "%s/api/generatedreport/header" % (job_server)
    
    encoded_data = generated_report_json.encode('utf-8')
    
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    r = http.request('POST', url,
             headers=headers,
             preload_content=False,
             body=encoded_data)

    responseText = ''
    responseStatus = r.status
    for chunk in r.stream(32):
        responseText += chunk.decode("utf-8")
    
    responseJSON = json.loads(responseText)

    r.release_conn()

    if responseStatus > 299:
        print('Failed http call, response code: ' + str(responseStatus))
        print('Url: ' + url)
        print(responseJSON)
        print('--------------------------------------------------------------------------------')
        print()
        raise Exception("Could not upload report header to %s" % url)

    if(responseJSON["successful"]):
        return responseJSON["result"]
    else:
        raise Exception(responseJSON["errors"][0]["message"])

def upload_report(report_id, generated_report_id, output_file):
    """
    upload a report file to the server

    Parameters
    ----------
    report_id
        The id of the report definition that was originally created for this report.

    generated_report_id
        Id returned from adding the report_header to the server

    output_file
        Full path and file of the report that was generated

    Returns
    --------
    out: string
        Returns the full URL that can be used to access this report, note that access to this PDF will be secured by authentication.

    """
    job_server = os.environ.get('JOB_SERVER_URL')
    if(job_server is None):
        raise Exception("Missing environment variable [JOB_SERVER_URL]")

    url = "%s/api/generatedreport/%s/%s/upload" % (job_server, report_id, generated_report_id)

    if(not os.path.isfile(output_file)):
        raise Exception("File %s does not exists" % output_file)    
    
    files = {'file': open(output_file, 'rb')}
    r = requests.post(url, files = files)

    print(r.text)

    responseText = r.text
    responseStatus = r.status_code
    
    responseJSON = json.loads(responseText)

    print(responseStatus)
    if responseStatus > 299:
        print('Failed http call, response code: ' + str(responseStatus))
        print('Url: ' + url)
        print(r.text)
        print('--------------------------------------------------------------------------------')
        print()
        raise Exception("Error %d, could not upload %s to %s." % (r.status_code, output_file, url))  

    if(responseJSON["successful"]):
        return responseJSON["result"]
    else:
        raise Exception(responseJSON["errors"][0]["message"])

def add_page_header(pdf, report_title, device_name, logo_file = None, date = None):
    """
    Add a report header to a PDF

    Parameters
    ----------
    pdf
        Instance of the the PDF document that is being built.
    
    report_title
        Title to be placed at the top of the report

    device_name
        Name of the device that will be added to the report header

    logo_file
        Logo file to be added to the top of the report (optional)

    date
        Date to be added to the top of the report (optional)
    """
    if(date == None):
        date = datetime.datetime.now()
   
    if(isinstance(date, datetime.date) or isinstance(date, datetime.datetime)):
        report_date = date
    else:
        p = re.compile('[0-1]?\d\/[0-3]?\d\/\d{4} \d{1,2}:\d{2}')
        if(p.match(date) != None):
            report_date = datetime.datetime.strptime(date, "%m/%d/%Y %H:%M")
        else:
            p = re.compile('^\d{4}\/[0-1]?\d\/[0-3]?\d$')
            if(p.match(date) != None):
                report_date = datetime.datetime.strptime(date, "%Y/%m/%d")
            
    if(report_date == None):
        report_date = datetime.datetime.now()

    if(logo_file != None):
        pdf.set_xy(183.,6.0)
        pdf.image(logo_file,  link='', type='', w=1586/80, h=1920/80)
    
    pdf.set_font('Arial', 'B', 24)
    pdf.set_text_color(50, 50, 50)
    pdf.set_xy(0,2.0)
    pdf.cell(w=210.0, h=40.0, align='C', txt=report_title, border=0)
    pdf.set_font('Arial', 'B', 18)

    
    pdf.set_xy(10,12.0)
    pdf.cell(w=210.0, h=40.0, align='L', txt=device_name, border=0)

    pdf.set_font('Arial', '', 10)
    pdf.set_xy(10,18.0)
    pdf.cell(w=210.0, h=40.0, align='L', txt=report_date.strftime("%b %d, %Y"), border=0)

def add_table(pdf, title, y, cols, df):
    """
    Add a table to PDF

    Parameters
    ----------
    pdf
        Instance of the PDF document that is being built.

    title
        Title to be placed at the top of the table.

    y 
        Y position to add the table to the report

    cols
        Definition of the table to include name of the data column, width and alignment 
    """
    x = 20
   
    pdf.set_font('Arial', 'B', 14)
    pdf.set_xy(20, y)
    pdf.cell(w=40.0, h=8.0, align='L', txt=title, border=0)
    
    y += 10
    totals = []
   
    for col in cols:
        colWidth = col['w']
        hdr = col['hdr']
        pdf.set_font('Arial', 'B', 12)
        pdf.set_xy(x, y)
        pdf.cell(w=colWidth, h=5.0, align='C', txt=hdr, border=0)
        x += colWidth
        totals.append(0)

    y += 5
    pdf.set_line_width(0.0)
    pdf.line(20, y, x, y) 
    y += 2

    for i, j in df.iterrows(): 
        x = 20
        idx = 0
        for col in cols:
            pdf.set_xy(x, y)
            colWidth = col['w']

            value = j[col['fld']]
            align = None
            if('align' in col):
                align = col['align']
           
            if(isinstance(value,float)):
                totals[idx] += value
                rnd = 1
                if('rnd' in col):
                    rnd = col['rnd']

                strFmt = '{0:.' + str(rnd) + 'f}'

                value = strFmt.format(value)

                if(align == None):
                    align = 'R'
            
            if(isinstance(value, pd._libs.tslibs.timestamps.Timestamp)):
                if('fmt' in col):
                    value = value.strftime(col['fmt'])

            if(align == None):
                align = 'L'

            pdf.cell(w=colWidth, h=5.0, align=align, txt=str(value) , border=0)
            x += colWidth
            idx += 1

        y += 5

    y += 1
    pdf.set_line_width(0.0)
    pdf.line(20, y, x, y) 
    y += 1
    pdf.line(20, y, x, y) 
    y += 2

    idx = 0
    x = 20
    for col in cols:
        if('total' in col):
            pdf.set_xy(x, y)
            colWidth = col['w']
            align = 'R'
            if('align' in col):
                align = col['align']

            rnd = 1
            if('rnd' in col):
                rnd = col['rnd']
    
            total_hdr = ""
            if('tlthdr' in col):
                total_hdr = col["tlthdr"] + " "

            value = totals[idx]
        
            if(col['total'] == 'avg'):
                value /= df[col['fld']].count()

            strFmt = '{0:.' + str(rnd) + 'f}'
            
            if('units' in col):
                strFmt += col['units']
            
            actual = strFmt.format(value)
           
            pdf.cell(w=colWidth, h=5.0, align=align, txt=total_hdr + str(actual) , border=0)
       
        x += col['w']    

        idx += 1
        
    return y