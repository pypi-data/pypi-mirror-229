import json
import nuvpy.nuviot_srvc as nuviot_srvc
import nuvpy.nuviot_util as nuviot_util
from nuvpy.nuviot_srvc import NuvIoTRequest
from nuvpy.nuviot_srvc import NuvIoTResponse

def get_streams(ctx):
    """
    Load the details for the data streams that have been allocated for the
    the current organization

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    """
    responseJSON = nuviot_srvc.get(ctx, '/clientapi/datastreams')
    if responseJSON == None:
        return

    rj = json.loads(responseJSON)
    return nuviot_util.to_item_array(rj)   

def print_streams(ctx):
    """
    Print the streams along with their ids that have been allocated for the current organization. 

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    """
    responseJSON = nuviot_srvc.get(ctx, '/clientapi/datastreams')
    if responseJSON == None:
        return
 
    rj = json.loads(responseJSON)
    return nuviot_util.print_array("Data Stream", nuviot_util.to_item_array(rj))  

def get_stream(ctx, stream_id, device_id, page_size=1500):
    """
    Get a JSON array containing the data in a data stream for a particular device id. 

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    stream_id:
        Identifier of the data stream where data should be pulled.

    device_id:
        Device Id to pull data for.
    
    page_size:
        (optional) Number of records to return the default is 1500.

    """
    rqst = NuvIoTRequest('/clientapi/datastream/' + stream_id + '/data/' + device_id)
    rqst.pageSize = page_size
    responseJSON = nuviot_srvc.get_paged(ctx, rqst)
    if responseJSON == None:
        return
    
    rj = json.loads(responseJSON)
    response = NuvIoTResponse(rj)
    return response.rows

def get_paged_stream(ctx, stream_id, device_id, page_size, next_row_key = None):
    """
    Get a JSON array containing the data in a data stream for a particular device id. 

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    stream_id:
        Identifier of the data stream where data should be pulled.

    device_id:
        Device Id to pull data for.
    
    page_size:
        Number of record to return.

    next_row_key
        filter to pull next set of data.

    """
    rqst = NuvIoTRequest('/clientapi/datastream/' + stream_id + '/data/' + device_id)
    rqst.pageSize = page_size
    if next_row_key != None:
        rqst.nextRowKey = next_row_key
    
    responseJSON = nuviot_srvc.get_paged(ctx, rqst)
    if responseJSON == None:
        return
    
    rj = json.loads(responseJSON)
    response = NuvIoTResponse(rj)
    return response