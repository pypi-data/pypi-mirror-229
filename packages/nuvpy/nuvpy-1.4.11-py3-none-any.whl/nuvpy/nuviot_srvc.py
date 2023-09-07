import urllib3.request
import urllib.parse
import certifi
import os
import requests
from requests.exceptions import HTTPError

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email

from sendgrid.helpers.mail.attachment import Attachment
import base64
from sendgrid.helpers.mail.file_content import FileContent
from sendgrid.helpers.mail.file_type import FileType
from sendgrid.helpers.mail.file_name import FileName
from sendgrid.helpers.mail.disposition import Disposition
       
class NuvIoTResponse:
    """
    The NuvIoTResponse class contains fields that were returned from
    a call to a NuvIoT service that returns a list of data.  This class
    returns the following fields.  Depending on the underlying data source
    it may return a row key, partition key or both.  It is advisable to return
    both in the requests for additional data.

    The following are the parameters returned by a list data request, not all are present
    with every request
    ------------
    * rows - array of rows of data
    * nextPartitionKey - partition key to be returned to the server to receive the next page of data.
    * nextRowKey - row key to be returned to the server to receive the next page of data.
    * pageSize - total number of records per page.
    * pageIndex - for data sources that can return a page index, the page index of the data requested.
    * pageCount - for data source that can return a total page count, the total number of pages that could be returned.
    * hasMoreRecords - true if there are more records and false if not.
 
    """
    def __init__(self, result):
        self.rows = result['model']
        self.nextPartitionKey = result['nextPartitionKey']
        self.nextRowKey = result['nextRowKey']
        self.pageSize = result['pageSize']
        self.pageIndex = result['pageIndex']
        self.pageCount = result['pageCount']
        self.hasMoreRecords = result['hasMoreRecords']

class NuvIoTRequest:
    def __init__(self, path):
        """
        The NuvIoT request class can be used to make request to different data sources within NuvIoT.  These 
        are generally data streams but may also be used to return other types of data.

        The following are the parameters returned by a list data request, not all are present
        with every request
        ------------

        * path - Path to the end point that will return data, this may include parameters as specified by the REST request specification for the data source.
        * pageSize - number of records per page to be returned most data sources support page size.
        * pageIndex - some data sources expect the page index to perform paging.  If a page index was returned from the list request it should be passed in as a parameter.
        * nextRowKey - some data source expect the a row key to be used to perform paging.  If a row key was returned from the list request it should be passed in as a parameter.
        * nextPartitionKey - some data source expect the a partition key to be used to perform paging.  If a partition key was returned from the list request it should be passed in as a parameter.
        * startDate - for queries that support filtering by date, an optional start date can be provided in the standard JSON format.
        * endDate - for queries that support filtering by date, an optional end date can be provided in the standard JSON format.
        * groupBy - for queries that allow grouping by a field, the name of the field to group the data.
        * groupBySize - for queries that allow grouping of data, the number of records to group data together.
    
        Parameters
        ----------
        path:
            Path used to query data.

        """
        self.path = path
        self.pageSize = 50
        self.pageIndex = 0
        self.nextRowKey = None
        self.nextPartitionKey = None
        self.startDate = None
        self.endDate = None
        self.groupBy = None
        self.groupBySize = None
                                      
def get(ctx, path, content_type = "", pageSize=50):
    """
    Make a GET request to a NuvIoT data source will return a string that includes JSON for the response.

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    path:
        Path used to make the request, the auth and server information will be used from the ctx object.

    contentType: 
        Optional content type parameter used set the Accept HTTP header, defaults to empty.

    pageSize:
        Optional page size parameter used to make list requests, defaults to 50
    """
    if ctx.auth_type == 'user':
        headers={'Authorization': 'Bearer ' + ctx.auth_token, 'x-pagesize' : str(pageSize)}
    else:
        headers={'Authorization': 'APIKey ' + ctx.client_id + ':' + ctx.client_token, 'x-pagesize' : str(pageSize)}
       
    if(content_type != ""):
        headers['Accept'] = content_type
   
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    url = ctx.url + path
    r = http.request("GET", url, headers=headers, preload_content=False)
    
    responseJSON = ''
    for chunk in r.stream(32):
        responseJSON += chunk.decode("utf-8")

    r.release_conn()
    
    if r.status > 299:
        print('Failed http call, response code: ' + str(r.status))
        print('Url: ' + url)
        print('Headers: ' + str(headers))
        print(responseJSON)
        print('--------------------------------------------------------------------------------')
        print()
        raise Exception("Http non success code %d not complete request to %s" % (r.status, path))
   

    return responseJSON

def post_json(ctx, path, json):
    """
    Make a POST request with a JSON payload to be sent to a NuvIoT endpoint.
    
    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    path:
        Path used to make the request, the auth and server information will be used from the ctx object.

    json:
        JSON object to be posted

    Returns
    -------
        Will return any JSON returned from the server, if the response code is not a success code an exception will be raised.
    """
    if ctx.auth_type == 'user':
        headers={'Authorization': 'Bearer ' + ctx.auth_token, 'Content-Type':'application/json'}
    else:
        headers={'Authorization': 'APIKey ' + ctx.client_id + ':' + ctx.client_token, 'Content-Type':'application/json'}
    
    url = ctx.url + path

    encoded_data = json.encode('utf-8')
    
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    r = http.request('POST', url,
             headers=headers,
             preload_content=False,
             body=encoded_data)
    
    responseJSON = ''
    responseStatus = r.status
    for chunk in r.stream(32):
        responseJSON += chunk.decode("utf-8")
    
    r.release_conn()

    if responseStatus > 299:
        print('Failed http call, response code: ' + str(responseStatus))
        print('Url: ' + url)
        print('Headers: ' + str(headers))
        print(responseJSON)
        print('--------------------------------------------------------------------------------')
        print()
        raise Exception("Could not post JSON to %s" % url)

    return responseJSON  
  
def post_file(ctx, path, file_name):
    """
    Post a file to a NuvIoT end point.

    If the method does not raise an exception the file will be uploaded. 
    
    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    path:
        Path used to make the request, the auth and server information will be used from the ctx object.

    file:
        full path to the file including the file name and extension to be uploaded.

    """
    if ctx.auth_type == 'user':
        headers={'Authorization': 'Bearer ' + ctx.auth_token}
    else:
        headers={'Authorization': 'APIKey ' + ctx.client_id + ':' + ctx.client_token}

    url = ctx.url + path

    if(not os.path.isfile(file_name)):
        raise Exception("File %s does not exists" % file_name)    
    
    session = requests.Session()
    files = {'file': open(file_name, 'rb')}
    r = requests.post(url, headers = headers, files = files)
    if r.status_code > 299:
        print('Failed http call, response code: ' + str(r.status_code))
        print('Url: ' + url)
        print('Headers: ' + str(headers))
        print(r.text)
        print('--------------------------------------------------------------------------------')
        print()
        raise Exception("Error %d, could not upload %s to %s." % (r.status_code, file_name, path))  


def download_file(ctx, path, dest, accept = ""):
    """
    Download a file to a NuvIoT
    
    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    path:
        Path used to make the request, the auth and server information will be used from the ctx object.

    dest:
        The full path including the file name and extension of where the downloaded file should be saved.

    Returns
    -------
        Will return True if the file is download and saved locally, other wise it will return False.
    """
    if ctx.auth_type == 'user':
        headers={'Authorization': 'Bearer ' + ctx.auth_token}
    else:
        headers={'Authorization': 'APIKey ' + ctx.client_id + ':' + ctx.client_token}
       
    if(accept != ""):
        headers['Accept'] = accept
    
    url = ctx.url + path
    
    print("Downloading file: %s" % url)

    chunk_size = 65536
        
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    r = http.request("GET", url, headers=headers, preload_content=False)
 
    if r.status > 299:
        print('Failed http %d url: %s' % (r.status, url))
        print('Headers: ' + str(headers))
        print('--------------------------------------------------------------------------------')
        print()
        r.release_conn()
        return False

    print('Headers: ' + str(r.headers))
    print('Headers: ' + str(r.headers["Content-Disposition"]))
    with open(dest, 'wb') as out:
        while True:
            data = r.read(65535)
            if not data:
                break
            
            out.write(data)
    r.release_conn()
    return True
  
def get_paged(ctx, rqst):
    """
    Make a GET request to a NuvIoT paged data source will return a string that includes JSON for the response.

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    path:
        Path used to make the request, the auth and server information will be used from the ctx object.

    contentType: 
        Optional content type parameter used set the Accept HTTP header, defaults to empty.

    pageSize:
        Optional page size parameter used to make list requests, defaults to 50
    """    
    if ctx.auth_type == 'user':
        headers={'Authorization': 'Bearer ' + ctx.auth_token, 'x-pagesize' : rqst.pageSize}
    else:
        headers={'Authorization': 'APIKey ' + ctx.client_id + ':' + ctx.client_token, 'x-pagesize' : rqst.pageSize}    

    if(rqst.nextRowKey):
        headers['x-nextrowkey'] = rqst.nextRowKey

    if(rqst.nextPartitionKey):
        headers['x-nextpartitionkey'] = rqst.nextPartitionKey

    if(rqst.pageIndex):
        headers['x-pageindex'] = rqst.pageIndex

    if(rqst.startDate):
        headers['x-filter-startdate'] = rqst.startDate

    if(rqst.endDate):
        headers['x-filter-enddatex'] = rqst.endDate

    if(rqst.groupBy):
        headers['x-group-by'] = rqst.groupBy        

    if(rqst.groupBySize):
        headers['x-group-by-size'] = rqst.groupBySize

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    url = ctx.url + rqst.path
    r = http.request("GET", url, headers=headers, preload_content=False)
    responseJSON = ''
    for chunk in r.stream(32):
        responseJSON += chunk.decode("utf-8")

    r.release_conn()
    
    if r.status > 299:
        print('Failed http call, response code: ' + str(r.status))
        print('Url: ' + url)
        print('Headers: ' + str(headers))
        print(responseJSON)
        print('--------------------------------------------------------------------------------')
        print()
        return None
      
    return responseJSON