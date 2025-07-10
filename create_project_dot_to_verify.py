# render_lightfield.py


import bpy
import numpy as np
import os
import math
from mathutils import Matrix, Vector

RENDER_WIDTH = 512
RENDER_HEIGHT = 512
DEPTH_NPY = "depth.npy"
CLIP_START = 0.0
CLIP_END = 10000.0
CAMERA_NAME = "camera_0_0"

# === SET RENDER SETTINGS ===
scene = bpy.context.scene
scene.render.engine = 'CYCLES'  
scene.render.image_settings.file_format = 'OPEN_EXR'
scene.render.image_settings.color_depth = '32'
scene.render.resolution_x = RENDER_WIDTH
scene.render.resolution_y = RENDER_HEIGHT

# === SET ACTIVE CAMERA TO CAMERA_0_0 ===
main_cam = bpy.data.objects.get(CAMERA_NAME)
bpy.context.scene.camera = main_cam

# === COMPUTE INTRINSIC MATRIX ===
fx = RENDER_WIDTH / (2 * math.tan(main_cam.data.angle / 2))
fy = RENDER_HEIGHT / (2 * math.tan(main_cam.data.angle / 2))
cx = RENDER_WIDTH / 2
cy = RENDER_HEIGHT / 2

def pixel_to_world(i, j, z):
    """
    Convert pixel (i, j) with depth z to world coordinates.
    """
    x = ((i+0.5) - cx) * z / fx # we sample depth from the middle of pixel, So, we need +0.5
    y = ((j+0.5) - cy) * z / fy
    point_camera = Vector((x, -y, -z))  # this camera view uses -Z forward, Y up
    world_point = main_cam.matrix_world @ point_camera
    return world_point

# === LOAD DEPTH === 
depth = np.load(DEPTH_NPY)

# create depth correction for sphere
if "DepthPoints" not in bpy.data.collections:
    depth_coll = bpy.data.collections.new("DepthPoints")
    bpy.context.scene.collection.children.link(depth_coll)
else:
    depth_coll = bpy.data.collections["DepthPoints"]


# === FOR EACH PIXEL: RENDER FROM PANORAMIC CAM ===
step = 8  # Reduce step to avoid rendering 512x512 = 260K images
for y in range(0, RENDER_HEIGHT, step):
    for x in range(0, RENDER_WIDTH, step):
        z = depth[y, x]
        if z == np.inf or z == 0 or np.isnan(z):
            continue
        world_loc = pixel_to_world(x, y, z)
        # Visualize with sphere
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=world_loc)
        sphere_obj = bpy.context.active_object
        print(f"{x}_{y}")
        sphere_obj.name = f"sphere_{x}_{y}"
        
        # Link sphere to collection and unlink from master collection
        depth_coll.objects.link(sphere_obj)
        bpy.context.scene.collection.objects.unlink(sphere_obj)

        # pano_cam.location = world_loc
        # scene.render.filepath = os.path.join(PANO_OUTPUT_DIR, f"{x}_{y}.exr")
        # bpy.ops.render.render(write_still=True)




