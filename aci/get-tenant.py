""" ACI Get Tenant Information
"""

import requests
import xml.dom.minidom
import json

requests.packages.urllib3.disable_warnings()
encoded_body = json.dumps({
            "aaaUser": {
                "attributes": {
                    "name": "admin",
                    "pwd": "!v3G@!4@Y"
                 }
            }
})
resp = requests.post("https://sandboxapicdc.cisco.com/api/aaaLogin.json",\
                      data=encoded_body, verify=False)

header = {"Cookie": "APIC-cookie=" +  resp.cookies["APIC-cookie"]}

tenants = requests.get("https://sandboxapicdc.cisco.com/api/node/class/fvTenant.xml?\
rsp-subtree-include=health,faults", headers=header, verify=False)

#print(tenants.text)

print("*"*79)
print("*"*79)

dom = xml.dom.minidom.parseString(tenants.text)
xml = dom.toprettyxml()
#print(type(xml)) # String
print(xml)

tenant_objects = dom.firstChild
if tenant_objects.hasChildNodes:
    tenant_element = tenant_objects.firstChild
    while tenant_element is not None:
        if tenant_element.tagName == 'fvTenant':
            health_element = tenant_element.firstChild
            output = "Tenant: "  + tenant_element.getAttribute('name') + '\t Health Score: ' + health_element.getAttribute('cur')
            print(output.expandtabs(40))
            tenant_element = tenant_element.nextSibling

print("*"*20,"\n","*"*20)

tenant_list = dom.getElementsByTagName('fvTenant')
for tenants in tenant_list:
  tenant_name = tenants.getAttribute('name')
  tenant_dn = tenants.getAttribute('dn')
  health_score = tenants.firstChild.getAttribute('cur')
  output = "Tenant: " + tenant_name + "\t Health Score: " + health_score + "\n DN: " + tenant_dn
  print(output.expandtabs(40))
