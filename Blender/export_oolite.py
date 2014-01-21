#!BPY
 
"""
Name 'Oolite DAT'
Blender: 263
Group: 'Export'
Tooltip 'Oolite mesh exporter'
"""
 
bl_info = {
	"name":		"Oolite (.dat)",
	"author":	"Ben Merritt",
	"blender":	(2,6,3),
	"version":	(0,0,1),
	"location":	"File > Import-Export",
	"description": "Exports the selected mesh to an Oolite .dat file",
	"category": "Import-Export",
}
 
import os.path
#from types import *
 
import bpy
import mathutils
 
def convertCoords(vec):
	return mathutils.Vector((vec.x, vec.z, -vec.y))
 
def formatVector(vec):
	return "{},{},{}".format(vec.x, vec.y, vec.z)
 
def formatTex(tc):
	return "{} {}".format(vec.x, vec.y)
 
 
def write(filename):
	object = bpy.context.active_object
	if object.type != "MESH":
		raise Exception("Invalid active object; must be a mesh")
 
	#Apply modifiers.
	mesh = object.to_mesh(bpy.context.scene, True, "PREVIEW")
 
	#Write mesh data.
	verts = []
	normals = []
	writtenSmoothVerts = {}
 
	vertsOut = []
	normsOut = []
	facesOut = []
	uvsOut = []
 
	for v in mesh.vertices:
		verts.append(convertCoords(v.co))
		normals.append(convertCoords(v.normal))
 
	uvs = None
 
	if len(mesh.tessface_uv_textures) > 0:
		uvs = mesh.tessface_uv_textures[0]
 
	for face in mesh.tessfaces:
		faceOut = []
		texName = None
		if uvs is not None:
			texName = os.path.basename(uvs.data[face.index].image.filepath)
			if texName is None:
				raise Exception("Face with missing texture")
 
		def writeTri(vertexNumbers):
			triOut = ",".join((str(faceOut[vn]) for vn in vertexNumbers))
			facesOut.append("0,0,0 {} 3,{}\n".format(formatVector(convertCoords(face.normal)), triOut))
			if uvs is not None:
				faceUvs = uvs.data[face.index].uv
				uvOut = " ".join(",".join((str(val) for val in (faceUvs[vn]))) for vn in vertexNumbers)
				uvsOut.append("{} 1.0,1.0 {}\n".format(texName, uvOut))
 
		for v in face.vertices:
			vOut = None
			if(face.use_smooth):
				if v in writtenSmoothVerts:
					vOut = writtenSmoothVerts[v]
				else:
					vOut = len(vertsOut)
					writtenSmoothVerts[v] = vOut
					vertsOut.append(formatVector(verts[v]) + "\n")
					normsOut.append(formatVector(normals[v]) + "\n")
			else:
				vOut = len(vertsOut)
				vertsOut.append(formatVector(verts[v]) + "\n")
				normsOut.append(formatVector(convertCoords(face.normal)) + "\n")
			faceOut.append(vOut)
 
		writeTri(range(2, -1, -1))
		#If this is a quad, add another triangle to fill it out.
		if len(faceOut) == 4:
			writeTri([0, 3, 2])
 
	#Remove the temporary mesh.
	bpy.data.meshes.remove(mesh)
 
	out = open(filename, "w")
 
	out.write("NVERTS %d\n" % len(vertsOut))
	out.write("NFACES %d\n" % len(facesOut))
 
	out.write("VERTEX\n")
	out.writelines(vertsOut)
 
	out.write("FACES\n")
	out.writelines(facesOut)
 
	if uvs is not None:
		out.write("TEXTURES\n")
		out.writelines(uvsOut)
 
	out.write("NORMALS\n")
	out.writelines(normsOut)
 
	out.write("END\n")
 
	out.close()
 
 
class Exporter(bpy.types.Operator):
	"""Exporter for Oolite .dat meshes"""
	bl_idname = "export.oolite_dat"
	bl_label = "Export Oolite .dat mesh"
	bl_options = {'PRESET'}
 
	filename_ext = ".dat"
 
	filepath = bpy.props.StringProperty(subtype="FILE_PATH")
 
	@classmethod
	def poll(cls, context):
		return True
 
	def execute(self, context):
		write(self.filepath)
		return {'FINISHED'}
 
	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
 
def menu_func(self, context):
	self.layout.operator_context = 'INVOKE_DEFAULT'
	self.layout.operator(Exporter.bl_idname, text="Oolite (.dat)")
 
def register():
	bpy.utils.register_class(Exporter)
	bpy.types.INFO_MT_file_export.append(menu_func)
 
def unregister():
	bpy.utils.unregister_class(Exporter)
	bpy.types.INFO_MT_file_export.remove(menu_func)
 
if __name__ == "__main__":
	register()

