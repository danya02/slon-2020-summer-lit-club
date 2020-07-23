import jinja2
import sys
import os

loader = jinja2.FileSystemLoader(searchpath='./')
env = jinja2.Environment(loader=loader)

template = env.get_template(sys.argv[1])
with open(sys.argv[1]+'.compiled', 'w') as o:
        o.write(template.render())

os.system(f'./node_modules/.bin/mmdc -i {sys.argv[1]+".compiled"} -o {sys.argv[1]+".png"}')
