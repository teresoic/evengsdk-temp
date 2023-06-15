#Not so pretty script that creates links for iol and non-iol type devices
#it uses the device type (qemu/iol etc) and creates links based on this information
#required inputs are labname, filename and eveng server IP address
#you can replace x.x.x.x with the eveng ip address
#filename.csv should contain list of devices and ports

import requests
import json
from pprint import pprint
import csv



login_url = 'http://x.x.x.x/api/auth/login'

cred = '{"username": "admin", "password": "eve", "html5": "-1"}'

headers = {'Accept': 'application/json'}

login = requests.post(url=login_url, data=cred)

cookies = login.cookies

print(cookies)



labname = 'Link_Create.unl'
filename = 'CreateLinks.csv'

def get_device_id_from_hostname(labname, hostname):

    #login to the required lab and get the json data for parsing
    url = f"http://x.x.x.x/api/labs/{labname}/nodes"
    nodes = requests.get(url=url, headers=headers, cookies=cookies)
    data = nodes.json()
    #pprint(data)

#    hostname = 'F1'
    #create a set from the node dict and iterate all device_ids along with their json data
    changes = {}
    for x in data['data']:
        changes[x] = data['data'][x]['name']
#    print(changes)

    # find device ID from hostname by finding the value (hostname) from the key/value pairs and return the key
    device_id = list(changes.keys())[list(changes.values()).index(f"{hostname}")]
    return device_id
#    print("hostname to device: f{device_id}")
    
def get_interface_id_from_intname(labname, hostname, intid):
    
    nodeid = get_device_id_from_hostname(labname, hostname)
#    sortid = get_sortid_from_hostname(labname,hostname)
#    print(sortid)
    #login to the required lab and get the json data for parsing
    url = f"http://x.x.x.x/api/labs/{labname}/nodes/{nodeid}/interfaces"
    nodes = requests.get(url=url, headers=headers, cookies=cookies)
    data = nodes.json()
    pprint(data)

    hostname_type = get_sortid_from_hostname(labname, hostname)
#    print(hostname_type)
    if hostname_type == 'iol':


        #create a set from the node dict and iterate all device_ids along with their json data
        changes = {}
        for x in data['data']['ethernet']:
            changes[x] = data['data']['ethernet'][x]['name']
#        print(changes)
    
        # find device ID from hostname by finding the value (hostname) from the key/value pairs and return the key
        int_id = list(changes.keys())[list(changes.values()).index(f"{intid}")]
        return int_id
#        print("hostname to device: f{int_id}")
        
    else:
        changes = data['data']['ethernet']
        pprint(changes)

        b = changes.index(next(item for item in changes if item['name'] == intid))

        return b
   
def get_sortid_from_hostname(labname, hostname):
    
    device_id = get_device_id_from_hostname(labname, hostname)
    #login to the required lab and get the json data for parsing
    url = f"http://x.x.x.x/api/labs/{labname}/nodes"
    nodes = requests.get(url=url, headers=headers, cookies=cookies)
    data = nodes.json()
    pprint(data)

    a = data['data'][device_id]['type']
    return a
#    print(a)

with open(filename, 'r') as csvfile:
    datareader = csv.reader(csvfile)
    next(datareader)
    for row in datareader:
        a=row[0]

        s_node = row[0]
        d_node = row[2]
        
        src_int = row[1]
        dst_int = row[3]
        
        
        
        bridge_name = 'Brdg'+s_node+src_int
        #create network
        data = {    
                  "name": bridge_name,       
                  "type": 'bridge',
                  "visibility": 1,
                }
        url = f"http://x.x.x.x/api/labs/{labname}/networks"
        network = requests.post(url=url, headers=headers, cookies=cookies, data=json.dumps(data))
        data = network.json()
        bridge_id = data['data']['id']
#        print(data)
        
        #join src_int to bridge network
        
        s_node_id = get_device_id_from_hostname(labname, s_node)
        s_node_type = get_sortid_from_hostname(labname, s_node)
#        print(s_node_type)
#        print(s_node_id)
        src_int_id = get_interface_id_from_intname(labname, s_node, src_int)
#        print(src_int_id)
        
        payload = {src_int_id: str(bridge_id)}
        
        url = f"http://x.x.x.x/api/labs/{labname}/nodes/{s_node_id}/interfaces"
        
        create_link = requests.put(url, headers=headers, cookies=cookies, data=json.dumps(payload))
        data = create_link.json()
#        print(data)
        
        #join dst_int to bridge network
        
        d_node_id = get_device_id_from_hostname(labname, d_node)
#        print(d_node_id)
        d_node_type = get_sortid_from_hostname(labname, d_node)
#        print(d_node_type)
        dst_int_id = get_interface_id_from_intname(labname, d_node, dst_int)
#        print(dst_int_id)
        
        payload = {dst_int_id: str(bridge_id)}
        
        url = f"http://x.x.x.x/api/labs/{labname}/nodes/{d_node_id}/interfaces"
        
        create_link = requests.put(url, headers=headers, cookies=cookies, data=json.dumps(payload))
        data = create_link.json()
        print(data)
        
        #hide network
        
        payload = {    
                  "visibility": "0",
                }
        
        url = f"http://x.x.x.x/api/labs/{labname}/networks/{bridge_id}"
        network = requests.put(url=url, headers=headers, cookies=cookies, data=json.dumps(payload))
        data = network.json()
        print(data)
