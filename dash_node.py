import bpy
from bpy import data as D
from bpy import context as C
from mathutils import *
from math import *
import numpy as np 
import matplotlib.pyplot as plt



def deleteAllObjects():
    """    Deletes all objects in the current scene    """
    deleteListObjects = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 
        'POINTCLOUD', 'VOLUME', 'GPENCIL', 
                     'ARMATURE', 'LATTICE', 'EMPTY', 
                     'LIGHT', 'LIGHT_PROBE', 'CAMERA', 'SPEAKER']
    for o in bpy.context.scene.objects:
        for i in deleteListObjects:
            if o.type == i:
                o.select_set(False)
            else:
                o.select_set(True)
    bpy.ops.object.delete() 

    # remove collections 
    for l in range(0,len(list(bpy.data.collections))): 
        bpy.data.collections.remove(list(bpy.data.collections)[0])
    

def set_camera():
    scn = bpy.context.scene    
    cam1 = bpy.data.cameras.new("Camera 1")
    cam_obj1 = bpy.data.objects.new("Camera 1", cam1)
    cam_obj1.location = (37, -14, 5) # 24,-6,12 (18,2,8)
    cam_obj1.rotation_euler = (1.4, 0,1.2) # 1,-.2,0.9 (1., 0.,1.2)
    scn.collection.objects.link(cam_obj1)



def put_area_light():
    bpy.ops.object.light_add(type='AREA')
    light_obj             = bpy.data.objects['Area']
    light_obj.data.energy = 9500
    light_obj.color       = [1.0, 0.0, 0.0, 1.0]
    light_obj.location       = [6.0,17, 6.0]
    light_obj.scale = (40,40,40) #
    light_obj.rotation_euler = (-.13, 0.15, -.38)


deleteAllObjects()
set_camera()
put_area_light()


#####################

def set_material_colors(obj, val, frame_num, cm=None):
    # Create a new material for the object
    mat = bpy.data.materials.new(name="ColorMat")
    obj.data.materials.append(mat)
    
#    for i, val in enumerate(values):
    if cm:
        color = cm(val)
    else:
#    color = (val, val, val, 1.0) 
        color = plt.cm.jet(val) 
    
    mat.diffuse_color = color



 

###########################################33

def generate_curve(i):
    curve_name = '11'
    curve_location = (0,0,i)
    desired_length = 12
    location = (0,0,0)
#    bpy.ops.curve.primitive_bezier_curve_add(location=curve_location)
    bpy.ops.curve.primitive_nurbs_path_add(radius=1, enter_editmode=False, align='WORLD', 
    location=(0, 0, i), scale=(1, 1, 1))
    

    curve_obj = bpy.context.active_object
    curve_obj.name = curve_name

    #   # --- Now the Geometry Nodes part (using the direct approach) ---
    geom_nodes_modifier = curve_obj.modifiers.new(name="Resample Curve", type='NODES')
    node_tree = bpy.data.node_groups.new(type='GeometryNodeTree', name="Resample_Curve_Tree")
    geom_nodes_modifier.node_group = node_tree

    ## Clear existing nodes
    for node in node_tree.nodes:
        node_tree.nodes.remove(node)
        
    group_input = node_tree.nodes.new(type='NodeGroupInput')
    group_input.location = (-500, 0)

    group_output = node_tree.nodes.new(type='NodeGroupOutput')
    group_output.location = (700, 0)

    ## Create input/output sockets if they don't exist
    i1 = node_tree.interface.new_socket('Geometry', in_out = 'INPUT',socket_type='NodeSocketGeometry')
    o1 = node_tree.interface.new_socket('Geometry', in_out = 'OUTPUT',socket_type='NodeSocketGeometry')



    resample_node = node_tree.nodes.new(type="GeometryNodeResampleCurve")
    resample_node.location = (-300, 0)
    resample_node.inputs[2].default_value = 30

    nodes = [x for x in node_tree.nodes] 

    #node_tree.interface.new_socket('value', description="", in_out='INPUT', socket_type='NodeSocketFloat')

    join_geometry = node_tree.nodes.new("GeometryNodeJoinGeometry")
    join_geometry.location = (500, 0)

    instance_points = node_tree.nodes.new("GeometryNodeInstanceOnPoints")
    instance_points.location = (100,-100)

    cube_node = node_tree.nodes.new("GeometryNodeMeshCube")
    cube_node.location = (-300, -200)
    cube_node.inputs[0].default_value = (0.05,0.05,0.05) # size of cube... 

    #capture_attribute = node_tree.nodes.new("GeometryNodeCaptureAttribute")
    #capture_attribute.location = (-100,100)
    #capture_attribute.domain = 'POINT' # ('POINT', 'EDGE', 'FACE', 'CORNER', 'CURVE', 'INSTANCE', 'LAYER')
    #capture_attribute.socket_value_update(
    spline_parameter = node_tree.nodes.new("GeometryNodeSplineParameter")
    spline_parameter.location = (-500, -150)

    set_position = node_tree.nodes.new("GeometryNodeSetPosition")
    set_position.location = (300,-150) 

    sample_curve = node_tree.nodes.new("GeometryNodeSampleCurve")
    sample_curve.location = (-70,-400)


    #print(list(capture_attribute.id_data.links))

    euler = node_tree.nodes.new("FunctionNodeAlignEulerToVector")
    euler.location = (500, -189)



    store_color = node_tree.nodes.new("GeometryNodeStoreNamedAttribute")  
    store_color.location = (0,200)
    store_color.data_type = 'FLOAT_COLOR'
    store_color.domain = 'FACE'
    store_color.inputs[3].default_value = (0.265654, 0.333429, 0.592842, 1)

    
    node_tree.links.new(cube_node.outputs[0],store_color.inputs[0])

    node_tree.links.new(group_input.outputs[0],resample_node.inputs[0])
    node_tree.links.new(resample_node.outputs[0],join_geometry.inputs[0])
    node_tree.links.new(join_geometry.outputs[0], group_output.inputs[0])
    node_tree.links.new(resample_node.outputs[0], instance_points.inputs[0])
    node_tree.links.new(resample_node.outputs[0], sample_curve.inputs[0])
    #node_tree.links.new(capture_attribute.outputs[1], sample_curve.inputs[1])
    node_tree.links.new(instance_points.outputs[0], set_position.inputs[0])
    node_tree.links.new(cube_node.outputs[0], instance_points.inputs[2])


    node_tree.links.new(spline_parameter.outputs[0],sample_curve.inputs[2])

    node_tree.links.new(sample_curve.outputs[2], euler.inputs[2])
    node_tree.links.new(euler.outputs[0], instance_points.inputs[5])
    #node_tree.links.new(sample_curve.outputs[1], set_position.inputs[2])
    #node_tree.links.new(resample_node.outputs[0], capture_attribute.inputs[0])

    #node_tree.links.new(spline_parameter.outputs[0], capture_attribute.inputs[1])

    node_tree.links.new(set_position.outputs[0], join_geometry.inputs[0])


    #bpy.ops.node.add_node(use_transform=True, type="FunctionNodeAlignEulerToVector")



    #bpy.data.node_groups["Resample_Curve_Tree.157"].nodes["Align Euler to Vector"].axis = 'X'

    set_material_colors(curve_obj, np.random.rand(), 20, plt.cm.jet)    



    
for i in range(10):
    generate_curve(i*1)
    
    print ('fff')
