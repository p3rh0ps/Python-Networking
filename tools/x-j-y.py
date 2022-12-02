import xmltodict
import json
import yaml

xml_file = "data.xml"
yaml_file = "data.yml"

with open(xml_file, 'r') as jf:
  dict_data = xmltodict.parse(jf.read())
  json_data = json.dumps(dict_data, indent=2)
  print(json_data)

  print("*"*20)

  with open(yaml_file, 'w') as yfw:
    yaml.dump(dict_data, yfw, default_flow_style=False, encoding=None)

  with open(yaml_file, 'r') as yfr:
    print(yfr.read())
