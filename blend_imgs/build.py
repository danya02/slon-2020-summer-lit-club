#!/usr/bin/python3
import os
import json
import re
import hashlib
import base64
from concurrent.futures import ThreadPoolExecutor


def error(line, why):
    print('ERROR:', why)
    print('\t' + line)
    raise SystemExit(1)

files = []
# get list of all files in "assets" dir
for folder, _,  names in os.walk('assets'):
    folder = folder[7:]
    for name in names:
        files.append(folder + '/' + name)

def hash_file(file_name, add_prefix=True):
    hasher = hashlib.blake2b()
    try:
        with open(('assets/' if add_prefix else '')+file_name, 'rb') as o:
            while chunk := o.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except FileNotFoundError:
        return '0'*32
        
def image_by_name(name):
    return '../../game/images/'+name+'.png'


def process(lines, do_wildcards, ignore_paths=[]):
    properties = dict()
    to_render = []
    for line in lines:
        if line.startswith('%'):  # then it is a command
            line = line.split()
            command = line[0][1:]
            arguments = line[1:]
            def arg_count(count):
                if len(arguments)!=count:
                    error(line, f'Expected {count} arguments, but found {len(arguments)} instead: {arguments}')
                if count==1:
                    return arguments[0]
            if command == 'set':
                arg = arg_count(1)
                if '=' in arg:
                    try:
                        name, value = arg.split('=')
                    except ValueError:
                        error(line, 'A "set" command argument can only include a single equals sign')
                else:
                    name = arg
                    value = ''
                    if '!' in arg: 
                        error(line, 'Do not use the negation symbol ("!") when setting, use "unset" instead.')
                properties[name] = value
            elif command == 'unset':
                arg = arg_count(1)
                if '=' in arg:
                    error(line, 'When unsetting a parameter, use its name only.')
                try:
                    properties.pop(arg)
                except KeyError:
                    error(line, f'Tried to remove parameter/key with name "{arg}", but it was not set before.')
            else:
                error(line, f'No such command found: "{command}"')
        else:  # then it is a normal line
            try:
                path, renpy_name = line.split('->')
            except ValueError:
                error(line, 'Line does not contain path/Ren\'Py name separator ("->")')
            path = path.strip()
            renpy_name = renpy_name.strip()
            if path.count('*')>1:
                error(line, 'More than one wildcard symbol ("*") in path')
            if '--' in renpy_name:
                try:
                    renpy_name, parameters = renpy_name.split('--')
                except ValueError:
                    error(line, 'More than one parameter separator ("--")')
            else:
                parameters = ''
            parameters = parameters.strip()
            if renpy_name.count('*') != path.count('*'):
                error(line, f'Wildcard symbol ("*") count in path ({path.count("*")}) differs from count in Ren\'Py name ({renpy_name.count("*")})')

            resolved_parameters = properties.copy()
            for prop in parameters.split(','):
                negate = False
                if '=' in prop:
                    try:
                        name, value = prop.split('=')
                    except ValueError:
                        error(line, 'A parameter can only include a single equals sign')
                else:
                    name = arg
                    value = ''
                    if arg.startswith('!'):
                        negate = True
                        name = arg[1:]
                if negate:
                    try:
                        resolved_properties.pop(name)
                    except KeyError:
                        error(line, f'Property "{name}" is being negated, but it was not set')
                else:
                    resolved_parameters[name] = value

            if path in ignore_paths:
                continue
            if '*' in path:
                if not do_wildcards:
                    continue
                renpy_prefix, renpy_suffix = renpy_name.split('*')
                prefix, suffix = path.split('*')
                for filename in files:
                    if filename in [i[0] for i in to_render]:
                        error(line, f'Wildcard resolution resulted in filename "{filename}", which was already marked earlier')
                    if match := re.match('^' + re.escape(prefix) + '(.*?)' + re.escape(suffix) + '$', filename):
                        matched_wildcard = match.group(1)
                        to_render.append( (filename, renpy_prefix + matched_wildcard + renpy_suffix, resolved_parameters) )

            else:
                to_render.append( (path, renpy_name, resolved_parameters) )


    return to_render



                


# load data
lines = []
with open('mapping.txt') as o:
    for line in o:
        line = line.rstrip()
        if line:
            if not line.startswith('#'):
                lines.append(line)
with open('assets/prev_renders.json') as o:
    prev_renders = json.loads(o.read())


# parse file to get render sources, targets and properties
single_renders = process(lines, False)
single_paths = [i[0] for i in single_renders]
wildcard_renders = process(lines, True, single_paths)
renders = single_renders + wildcard_renders

# exclude those files for which the .blend file/target name/parameter combo did not change

true_render_tasks = []

hashes = dict()
for file, name, props in renders:
    hashes[file] = hash_file(file)
    blend_hash = hashes[file]
    img_file = image_by_name(name)
    hashes[img_file] = hash_file(img_file)
    img_hash = hashes[img_file]
    if [blend_hash, name, props, img_hash] in prev_renders:
        continue
    true_render_tasks.append((file, image_by_name(name), props))

# start actual render

import random
import time

def render(data):
    source, target, props = data
    os.system('blender '+repr(source)+' --background --python ../render.py -- ' + repr(os.path.abspath(target))+' '+str(base64.b64encode(bytes(json.dumps(props), 'utf-8')), 'utf-8'))
    time.sleep(random.random())  # mitigate race conditions?
    with open('prev_renders.json') as o:
        prev_renders = json.load(o)
    target_name = target.split('/')[-1].split('.')[0]
    prev_renders.append( (hashes[source], target_name, props, hash_file(os.path.abspath(target), False)) )
    with open('prev_renders.json', 'w') as o:
        o.write(json.dumps(prev_renders))
    
os.chdir('assets')
with ThreadPoolExecutor(max_workers=8) as executor:
    list(executor.map(render, true_render_tasks))

