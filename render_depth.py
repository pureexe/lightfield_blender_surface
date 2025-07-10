import bpy
import numpy as np
import os
import math
from mathutils import Matrix, Vector

RENDER_WIDTH = 512
RENDER_HEIGHT = 512
IMAGE_PATH = "image.exr"
DEPTH_PATH = "depth.exr"
CAMERA_NAME = "camera_0_0"
CLIP_START = 0.0
CLIP_END = 10000.0

# === SET RENDER SETTINGS ===
scene = bpy.context.scene
scene.render.engine = 'CYCLES'  
scene.render.image_settings.file_format = 'OPEN_EXR'
scene.render.image_settings.color_depth = '32'
scene.render.resolution_x = RENDER_WIDTH
scene.render.resolution_y = RENDER_HEIGHT

# === SET ACTIVE CAMERA TO CAMERA_0_0 ===
camera_obj = bpy.data.objects.get(CAMERA_NAME)
bpy.context.scene.camera = camera_obj

# === ADD COMPOSITOR DEPTH NODE SETUP ===
scene.use_nodes = True
tree = scene.node_tree

# Make sure depth pass is enabled
bpy.context.view_layer.use_pass_z = True

# Enable denoising on final render
bpy.context.scene.cycles.use_denoising = True

# Check if nodes already exist
depth_node = tree.nodes.get("DepthFile")
rl_node = tree.nodes.get("RenderLayers")

if rl_node is None:
    rl_node = tree.nodes.new('CompositorNodeRLayers')
    rl_node.name = "RenderLayers"

if depth_node is None or rl_node is None:
    depth_node = tree.nodes.new('CompositorNodeOutputFile')
    depth_node.name = "DepthFile"
    depth_node.base_path = "/tmp"
    depth_node.file_slots[0].path = DEPTH_PATH
    depth_node.format.file_format = 'OPEN_EXR'
    depth_node.format.color_depth = '32'
    tree.links.new(rl_node.outputs['Depth'], depth_node.inputs[0])

# === RENDER MAIN CAMERA TO GET DEPTH ===
print("START RENDERING DEPTH")
bpy.ops.render.render(write_still=True)
print("RENDERING DEPTH FINISHED")