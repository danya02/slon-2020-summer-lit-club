import bpy
from bpy.app.handlers import persistent
import sys
import re
import json
import base64
props = json.loads(base64.b64decode(bytes(sys.argv[-1], 'utf-8')))
target = sys.argv[-2]
print(repr(target))

@persistent
def do_render(dummy):
    bpy.data.scenes['Scene'].render.resolution_percentage=100
    bpy.data.scenes['Scene'].frame_start = 0
    bpy.data.scenes['Scene'].frame_end = bpy.data.scenes['Scene'].frame_start
    
    if isinstance(props.get('transparent', None), str):
        bpy.data.scenes['Scene'].render.film_transparent = True

    if isinstance(props.get('resolution', None), str):
        match = re.match('([0-9])+:([0-9])+', props['resolution'])
        if match: 
            bpy.data.scenes['Scene'].render.resolution_x = int(match.group(1))
            bpy.data.scenes['Scene'].render.resolution_y = int(match.group(2))

    bpy.data.scenes['Scene'].render.filepath=target
    bpy.data.scenes['Scene'].render.engine='BLENDER_EEVEE'
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.quit_blender()
bpy.app.handlers.load_post.append(do_render)
do_render(...)
