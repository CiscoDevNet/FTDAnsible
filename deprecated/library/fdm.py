import requests
import json
import getpass
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
 
requests.packages.urllib3.disable_warnings()
headers = {
    "Authorization": "Bearer "
}
auth_headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

hostname = raw_input("Enter Device URL: ")
username = raw_input("Enter username: ")
password = getpass.getpass("Enter password: ")

auth_payload = '{"grant_type": "password","username": "' + username + '","password": "' + password + '"}'
 
ReferenceModel = None
 
api_prefix = "/api/fdm/v1"
global interfaces
interfaces = {}
nwobjects = {}
global output
output = None

def login():
    r = requests.post(hostname + api_prefix + "/fdm/token", data=auth_payload, verify=False, headers=auth_headers)
    #print r.json()
    access_token = "Bearer %s" % r.json()['access_token']
    headers['Authorization'] = access_token
    print "Logged in to", hostname
 
def logout():
    prefix_length = len("Bearer ")
    access_token = headers['Authorization'][prefix_length:]
    del headers['Authorization']
    logout_payload = {'grant_type':'revoke_token','access_token':access_token,'token_to_revoke':access_token}
    requests.post(hostname + api_prefix + "/fdm/token", data=json.dumps(logout_payload), verify=False, headers=auth_headers)
   
def get_spec_json(also_return_response=False):
    login()
    http_client = RequestsClient()
    http_client.session.verify = False
    http_client.session.headers = headers
 
    #bravado will validate field type if it's in the JSON
    cli = SwaggerClient.from_url(hostname + '/apispec/ngfw.json', http_client=http_client, config={'validate_responses':False,'also_return_response':also_return_response})
    global ReferenceModel
    ReferenceModel = cli.get_model('ReferenceModel')
    return cli

def build_interfaces_dict():
    global interfaces
    o = fdm.Interface.getPhysicalInterfaceList().result()['items']
    for intf in o:
        interfaces[intf.hardwareName] = intf 

def print_output(obj, ts=""):
    print ts, type(obj).__name__
    ts += "\t"
    for i in dir(obj):
        if type(obj[i]).__name__ in ['NoneType', 'unicode', 'str', 'int', 'float', 'bool', 'list', 'dict']:
            print ts, i, ":", obj[i]
        else:
            print_output(obj[i], ts)
 
def create_network_object(nw, name = None):
    global output
    if "/" not in nw:
        print "Please enter a network value e.g.: 192.168.2.0/24"
        return False
    NetworkObject = fdm.get_model('NetworkObject')()
    if name == None:
        NetworkObject.name = nw.split("/")[0] 
    else:
        NetworkObject.name = name
    
    NetworkObject.value = nw
    NetworkObject.subType = 'NETWORK'
    NetworkObject.type='networkobject'
    output = fdm.NetworkObject.addNetworkObject(body = NetworkObject).result()
 
def create_host_object(host, name = None):
    global output
    if "/" in host:
        print "Please enter a host value e.g.: 192.168.2.1"
        return False
    NetworkObject = fdm.get_model('NetworkObject')()
    if name == None:
        NetworkObject.name = host
    else:
        NetworkObject.name = name
    
    NetworkObject.value = host
    NetworkObject.subType = 'HOST'
    NetworkObject.type='networkobject'
    output = fdm.NetworkObject.addNetworkObject(body = NetworkObject).result()
 
def retrieve_system_info():
    global output
    output = fdm.SystemInformation.getSystemInformation(objId="default").result()
    print_output(output)
 
def retrieve_licensing_info():
    global output
    output = fdm.SmartLicensing.getSmartAgentConnectionList().result()['items'][0]
    print_output(output)
  
def retrieve_licensing_status():
    global output
    output = fdm.SmartLicensing.getSmartAgentStatusList().result()['items'][0]
    print_output(output)
    
def retrieve_interface_info(hwName = None):
    global output, interfaces
    output = fdm.Interface.getPhysicalInterfaceList().result()['items']
    if hwName == None:
        for intf in output:
            interfaces[intf.hardwareName] = intf
            print_output(intf)
    else:
        for intf in output:
            if intf.hardwareName == hwName:
                print_output(intf)
                return
        else:
            print hwName, "does not exist"
        
def _get_interface_by_name(hwName):
    if interfaces == {}:
        build_interfaces_dict()
    if hwName in interfaces.keys():
        id = interfaces[hwName]['id']
        o = fdm.Interface.getPhysicalInterface(objId = id).result()
        return o
    else:
        print hwName, "does not exist"
        return None
        
def show_interfaces_brief():
    build_interfaces_dict()
    print "%-20s"%"Hardware Name", "%-25s"%"Name", "%-10s"%"Enabled", "%-10s"%"IP Type", "%-20s"%"IP Address"  
    print "--------------------------------------------------------------------------------------------------"    
    for intf in interfaces:
        if interfaces[intf].ipv4 and interfaces[intf].ipv4.ipAddress:
            print "%-20s"%interfaces[intf].hardwareName, "%-25s"%interfaces[intf].name, "%-10s"%interfaces[intf].enabled, "%-10s"%interfaces[intf].ipv4.ipType, "%-20s"%interfaces[intf].ipv4.ipAddress.ipAddress
        else:
            print "%-20s"%interfaces[intf].hardwareName, "%-25s"%interfaces[intf].name, "%-10s"%interfaces[intf].enabled
        
def shutdown_interface(hwName):
    global output
    output = _get_interface_by_name(hwName)
    print output
    if output != None:
        output.enabled = False
        output = fdm.Interface.editPhysicalInterface(objId = output.id, body = output).result()

def enable_interface(hwName):
    global output
    output = _get_interface_by_name(hwName)
    if output != None:
        output.enabled = True
        output = fdm.Interface.editPhysicalInterface(objId = output.id, body = output).result()

def configure_interface_name(hwName, name):
    global output
    output = _get_interface_by_name(hwName)
    if output != None:
        output.name = name
        output = fdm.Interface.editPhysicalInterface(objId = output.id, body = output).result()

def configure_interface_ip(hwName, ip, mask):
    global output
    output = _get_interface_by_name(hwName)
    if output != None:
        ipv4 = fdm.get_model('IPv4Address')()
        ipv4.ipAddress = ip
        ipv4.netmask = str(mask)
        ipv4.type = 'ipv4address'
        output.ipv4.ipAddress = ipv4
        output.ipv4.ipType = 'STATIC'
        output = fdm.Interface.editPhysicalInterface(objId = output.id, body = output).result()

def configure_interface_ipv6(hwName, ip):
    global output
    output = _get_interface_by_name(hwName)
    if output != None:
        ipv6 = fdm.get_model('IPv6Address')()
        ipv6.ipAddress = ip
        ipv6.type = 'ipv6address'
        if output.ipv6.ipAddresses == None:
            output.ipv6.ipAddresses = []
        output.ipv6.ipAddresses = [ipv6]
        output = fdm.Interface.editPhysicalInterface(objId = output.id, body = output).result()

def configure_interface_mtu(hwName, mtu):
    global output
    output = _get_interface_by_name(hwName)
    if output != None:
        try:
            mtu = int(mtu)
        except:
            print "MTU value should be an integer"
            return
        output.mtu = int(mtu)
        output = fdm.Interface.editPhysicalInterface(objId = output.id, body = output).result()

def configure_interface_speed(hwName, speed):
    global output
    output = _get_interface_by_name(hwName)
    if output != None:
        output.speedType = speed
        output = fdm.Interface.editPhysicalInterface(objId = output.id, body = output).result()

def configure_interface_duplex(hwName, duplex):
    global output
    output = _get_interface_by_name(hwName)
    if output != None:
        output.duplexType = duplex
        output = fdm.Interface.editPhysicalInterface(objId = output.id, body = output).result()

def add_host_to_ssh_management_access_list(host):
    global output
    if create_host_object(host) == False:
        return
    al = fdm.SSHAccessList.getSSHAccessListList().result()['items'][0]
    al.networkObjects.append(output)
    output = fdm.SSHAccessList.editSSHAccessList(objId = al.id, body = al).result()
    
def add_network_to_ssh_management_access_list(nw):
    global output
    if create_network_object(nw) == False:
        return
    al = fdm.SSHAccessList.getSSHAccessListList().result()['items'][0]
    al.networkObjects.append(output)
    output = fdm.SSHAccessList.editSSHAccessList(objId = al.id, body = al).result()
    
def add_host_to_https_management_access_list(host):
    global output
    if create_host_object(host) == False:
        return
    al = fdm.HTTPAccessList.getHTTPAccessListList().result()['items'][0]
    al.networkObjects.append(output)
    output = fdm.HTTPAccessList.editHTTPAccessList(objId = al.id, body = al).result()
    
def add_network_to_https_management_access_list(nw):
    global output
    if create_network_object(nw) == False:
        return
    al = fdm.HTTPAccessList.getHTTPAccessListList().result()['items'][0]
    al.networkObjects.append(output)
    output = fdm.HTTPAccessList.editHTTPAccessList(objId = al.id, body = al).result()
    
def configure_hostname(name):
    global output
    dh = fdm.DeviceHostname.getDeviceHostnameList().result()['items'][0]
    dh.hostname = name
    output = fdm.DeviceHostname.editDeviceHostname(objId = dh.id, body = dh).result()
    
def get_hostname():
    global output
    output = fdm.DeviceHostname.getDeviceHostnameList().result()['items'][0]
    print output.hostname

def build_network_objects_dict():
    global nwobjects
    nwobjects = {}
    o = fdm.NetworkObject.getNetworkObjectList().result()['items']
    for nw in o:
        nwobjects[nw.name] = nw
    
def _get_network_object_by_name(name):
    build_network_objects_dict()
    if name in nwobjects.keys():
        id = nwobjects[name]['id']
        o = fdm.NetworkObject.getNetworkObject(objId = id).result()
        return o
    else:
        print "NetworkObject", name, "does not exist"
        return None
        
    
def list_static_routes():
    global output
    id = fdm.StaticRouteEntryContainer.getStaticRouteEntryContainerList().result()['items'][0].id
    output = fdm.StaticRouteEntry.getStaticRouteEntryList(parentId=id).result()['items']
    for o in output:
        print o.iface.name, o.ipType, o.networks[0].name, o.gateway.name

def add_static_route(intfName, network, gateway, metric = 1):
    global output
    build_interfaces_dict()
    for intf in interfaces:
        if interfaces[intf].name == intfName:
            intfName = interfaces[intf]
    else:
        print "Interface", intfName, "does not exist"
        return
        
    nwObj = _get_network_object_by_name(network)
    gwObj = _get_network_object_by_name(gateway)
    if nwObj == None or gwObj == None:
        return
    rtEntry = fdm.get_model('StaticRouteEntry')()  
    rtEntry.iface = intfName
    rtEntry.networks = [nwObj]
    rtEntry.gateway = gwObj
    rtEntry.ipType = "IPv4"
    rtEntry.metricValue = metric
    id = fdm.StaticRouteEntryContainer.getStaticRouteEntryContainerList().result()['items'][0].id
    output = fdm.StaticRouteEntry.addStaticRouteEntry(parentId=id, body = rtEntry).result()

def delete_network_object(name):
    global output
    obj = _get_network_object_by_name(name)
    if obj == None:
        return
    output = fdm.NetworkObject.deleteNetworkObject(objId = obj.id).result()
    
def edit_network_object(currentName, **kwds):
    '''name: The name of the object \
    kwds: You can supply the parameters that you want to modify. The avallable parameters are: \
    name, description, value, subType. \
    An example call:  fdm.edit_network_object(my-obj, name = "new-name", description = "my-desc", value = "2.3.4.0/24", subType = "NETWORK") \
    '''
    global output
    obj = _get_network_object_by_name(currentName)
    if obj == None:
        return
    for param in kwds:
        if param in obj:
            obj[param] = kwds[param]
    output = fdm.NetworkObject.editNetworkObject(objId = obj.id, body = obj).result()
    
def list_network_objects(limit = 0):
    '''limit can be set to any positive number so that only the first so many objects can be retrieved. \
    if limit is omitted, then all the objects are retrieved
    '''
    global output
    o = fdm.NetworkObject.getNetworkObjectList(limit = limit).result()['items']
    for nw in o:
        print "%-50s"%nw.name, "%-25s"%nw.value, "%-10s"%nw.subType
    
try:
    fdm
except:
    fdm = get_spec_json()
    build_interfaces_dict()
try:
    output
except:
    output = None
