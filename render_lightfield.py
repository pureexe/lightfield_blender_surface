# render_lightfield.py


import bpy
import numpy as np
import os
import math
from mathutils import Matrix, Vector

DEPTH_WIDTH = 512
DEPTH_HEIGHT = 512
ENVMAP_WIDTH = 512
ENVMAP_HEIGHT = 256
DEPTH_NPY = "depth.npy"
CLIP_START = 0.00000001
CLIP_END = 10000.0
MAINCAMERA_NAME = "camera_0_0"
PANOCAM_NAME = "camera_pano"
PANO_OUTPUT_DIR = "C:/tmp/surface_light_field"

# === SET RENDER SETTINGS ===
scene = bpy.context.scene
scene.render.engine = 'CYCLES'  
bpy.context.scene.render.engine = 'CYCLES'
scene.render.image_settings.file_format = 'OPEN_EXR'
scene.render.image_settings.color_depth = '32'
scene.render.resolution_x = ENVMAP_WIDTH
scene.render.resolution_y = ENVMAP_HEIGHT


# === GET PANOCAMERA ===
pano_cam = bpy.data.objects.get(PANOCAM_NAME)
if pano_cam is None:
    # create new camera if not exist 
    cameras_coll = bpy.data.collections["cameras"]
    bpy.ops.object.camera_add(location=(0,0,0))
    pano_cam = bpy.context.object
    pano_cam.name = PANOCAM_NAME
    pano_cam.data.type = 'PANO'
    pano_cam.data.panorama_type = 'EQUIRECTANGULAR'
    pano_cam.data.clip_start = CLIP_START
    pano_cam.data.clip_end = CLIP_END
    cameras_coll.objects.link(pano_cam)
    bpy.context.scene.collection.objects.unlink(pano_cam)

#if pano_cam.name not in scene.collection.objects:
#    scene.collection.objects.link(pano_cam)


# === SET ACTIVE CAMERA TO PANOCAMERA ===
bpy.context.scene.camera = pano_cam 

# === COMPUTE INTRINSIC MATRIX ===
main_cam = bpy.data.objects.get(MAINCAMERA_NAME)
fx = DEPTH_WIDTH / (2 * math.tan(main_cam.data.angle / 2))
fy = DEPTH_HEIGHT / (2 * math.tan(main_cam.data.angle / 2))
cx = DEPTH_WIDTH / 2
cy = DEPTH_HEIGHT / 2


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

# === FOR EACH PIXEL: RENDER FROM PANORAMIC CAM ===
step = 128  # Reduce step to avoid rendering 512x512 = 260K images
for y in range(0, DEPTH_HEIGHT, step):
    for x in range(0, DEPTH_WIDTH, step):
        z = depth[y, x]
        if z == np.inf or z == 0 or np.isnan(z):
            continue
        world_loc = pixel_to_world(x, y, z)
        pano_cam.location = world_loc
        print(f"spatial_envmap_{x}_{y}")
        scene.render.filepath = os.path.join(PANO_OUTPUT_DIR, f"{x}_{y}.exr")
        print("Rendering:", scene.render.filepath)
        bpy.ops.render.render(write_still=True)
        print("Saved:", os.path.exists(scene.render.filepath))



