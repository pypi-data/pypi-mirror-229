from ruamel.yaml import YAML, CommentedMap
from collections import OrderedDict
import sys

yaml = YAML()
with open('../tests/templates/jsontags.yml') as cfn:
    data = yaml.load(cfn)

#print(data)
addtags = OrderedDict(
        {
            "Key": 'Testing',
            "Value": 'nojsontag'
         }
        )
addjsontags = OrderedDict(
        {
            'Testing': 'jsontag'
            }
        )

for res in data['Resources']:
    print(f"UPDATE: {res}...")
    print(data['Resources'][res])
    if 'Tags' in data['Resources'][res]['Properties']:
        print(type(data['Resources'][res]['Properties']['Tags']))
        if type(data['Resources'][res]['Properties']['Tags']) == CommentedMap:
            print(data['Resources'][res]['Properties']['Tags'])
            data['Resources'][res]['Properties']['Tags'] = addjsontags
        else:
            data['Resources'][res]['Properties']['Tags'].append(addtags)
    else:
        data['Resources'][res]['Properties']['Tags'] = addtags
yaml.dump(data, sys.stdout)
