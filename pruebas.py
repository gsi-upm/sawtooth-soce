import ast
import json

p = "{\'voter1': \"{\'a\':1, \'b\':2}\", \'voter2\': \"{\'a\':0, \'b\':1}\"}"

p1 =  ast.literal_eval(p)

p2 = {}

for k, v in p1.items():
	p2[k] = ast.literal_eval(v)

print(p2)

print('json: ', json.dumps(p2))

print(p)

print(str(p2))