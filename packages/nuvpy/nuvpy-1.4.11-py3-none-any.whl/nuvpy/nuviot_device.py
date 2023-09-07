import json
import nuvpy.nuviot_srvc as nuviot_srvc
import nuvpy.nuviot_util as nuviot_util

def get_device_types(ctx):
    """
    Returns a list of device types that have been configured for the current organization. 

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    """    
    responseJSON = nuviot_srvc.get(ctx, '/api/devicetypes')
    if responseJSON == None:
        return
 
    rj = json.loads(responseJSON)
    return nuviot_util.to_item_array(rj)

def get_device_configs(ctx):
    """
    Returns a list of device device configurations that have been configured for the current organization. 

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    """    
    responseJSON = nuviot_srvc.get(ctx, '/api/deviceconfigs')
    if responseJSON == None:
        return
 
    rj = json.loads(responseJSON)
    return nuviot_util.to_item_array(rj)

def print_device_types(ctx):
    """
    Prints a list of device types that have been configured for the current organization. 

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    """    
    responseJSON = nuviot_srvc.get(ctx, '/api/devicetypes')
    if responseJSON == None:
        return
 
    rj = json.loads(responseJSON)
    nuviot_util.print_array("Device Types", nuviot_util.to_item_array(rj))

def print_device_configs(ctx):
    """
    Prints a list of device device configurations that have been configured for the current organization. 

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    """   
    responseJSON = nuviot_srvc.get(ctx, '/api/deviceconfigs')
    if responseJSON == None:
        return
 
    rj = json.loads(responseJSON)
    nuviot_util.print_array("Device Configs", nuviot_util.to_item_array(rj))

def get_device_groups(ctx):
    """
    Returns a list of device device groups that have been configured for the current application. 

    When a client id and token are created, they are created for a specific instance, that instance
    and the associated device repository will be used to filter the data within this response.


    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    """   
    responseJSON = nuviot_srvc.get(ctx, '/clientapi/repo/groups')        
    if responseJSON == None:
        return
 
    rj = json.loads(responseJSON)
    return nuviot_util.to_item_array(rj) 

def get_devices_by_group(ctx, group_id):
    """
    Returns a list of device that belong to a specific device group. 

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    group_id:
        Group Id to return the list of devices within that group.
    """   
    responseJSON = nuviot_srvc.get(ctx, '/clientapi/repo/group/' + group_id + '/devices')
    if responseJSON == None:
        return
 
    rj = json.loads(responseJSON)
    return nuviot_util.to_item_array(rj)

def get_devices(ctx):
    """
    Gets a list of devices for the device repository associated with the IoT application. 

    When a client id and token are created, they are created for a specific instance, that instance
    and the associated device repository will be used to filter the data within this response.

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    """    
    responseJSON = nuviot_srvc.get(ctx, '/clientapi/devices')
    if responseJSON == None:
        return
 
    rj = json.loads(responseJSON)
    return nuviot_util.to_item_array(rj)

def print_device_groups(ctx):
    """
    Prints a list of device device groups that have been configured for the current application. 

    When a client id and token are created, they are created for a specific instance, that instance
    and the associated device repository will be used to filter the data within this response.


    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    """   
    responseJSON = nuviot_srvc.get(ctx, '/clientapi/repo/groups')

    if responseJSON == None:
        return
 
    rj = json.loads(responseJSON)
    nuviot_util.print_array("Device Groups",nuviot_util.to_item_array(rj))
    
def print_devices(ctx):
    """
    Prints a list of device device groups that have been configured for the current application. 

    When a client id and token are created, they are created for a specific instance, that instance
    and the associated device repository will be used to filter the data within this response.

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    """    
    responseJSON = nuviot_srvc.get(ctx, '/clientapi/devices')
    if responseJSON == None:
        return
 
    rj = json.loads(responseJSON)
    nuviot_util.print_array("Devices by Repo", nuviot_util.to_item_array(rj, "deviceId"))
    
def print_devices_by_group(ctx, group_id):
    """
    Returns a list of device that belong to a specific device group. 

    Parameters
    ----------
    ctx:
        Context Object that defines how this method should call the server to include authentication.

    group_id:
        Group Id to return the list of devices within that group.
    """       
    responseJSON = nuviot_srvc.get(ctx, '/clientapi/repo/group/' + group_id + '/devices')
    if responseJSON == None:
        return
 
    rj = json.loads(responseJSON)
    nuviot_util.print_array("Devices by Group", nuviot_util.to_item_array(rj))
