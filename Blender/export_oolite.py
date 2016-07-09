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

# TODO:
# * Material/texture support

import os.path
#from types import *

import bpy
import mathutils

# Converts vectors in Blender's coordinate system to Oolite's coordinate system
def convertCoords(vec):
	return mathutils.Vector((vec.x, vec.z, -vec.y))

def formatVector(vec):
	return "{},{},{}".format(vec.x, vec.y, vec.z)

def formatTex(tc):
	return "{} {}".format(vec.x, vec.y)

class Exporter(object):
	def __init__(self, filename):
		self.filename = filename
		# Mesh data to be written out
		self.verts_out = []
		self.norms_out = []
		self.faces_out = []
		self.uvs_out = []
		# Keeps track of smooth verts' indices in verts_out so we can share them between
		# faces
		self.written_smooth_verts = {}

	# TODO: break up into smaller methods.
	def write(self):
		object = bpy.context.active_object
		if object.type != "MESH":
			raise Exception("Invalid active object; must be a mesh")

		# Write mesh data.
		verts = []
		normals = []

		# Apply modifiers.
		mesh = object.to_mesh(bpy.context.scene, True, "PREVIEW")

		try:
			for v in mesh.vertices:
				verts.append(convertCoords(v.co))
				normals.append(convertCoords(v.normal))

			uvs = None

			if len(mesh.tessface_uv_textures) > 0:
				uvs = mesh.tessface_uv_textures[0]

			for face in mesh.tessfaces:
				face_out = []
				tex_name = None
				if uvs is not None:
					tex_name = os.path.basename(uvs.data[face.index].image.filepath)
					if tex_name is None:
						raise Exception("Face with missing texture")

				def writeTri(vertex_numbers):
					tri_out = ",".join((str(face_out[vn]) for vn in vertex_numbers))
					self.faces_out.append("0,0,0 {} 3,{}\n".format(formatVector(convertCoords(face.normal)), tri_out))
					if uvs is not None:
						face_uvs = uvs.data[face.index].uv
						# Formats UV coords for each face ("v1x,v1y v2x,v2y ...")
						uv_out = " ".join(",".join((str(coord) for coord in (face_uvs[vn]))) for vn in vertexNumbers)
						self.uvs_out.append("{} 1.0,1.0 {}\n".format(texName, uv_out))

				for vert_num in face.vertices:
					# TODO: rename to vert_num_out?
					vert_out = None
					if(face.use_smooth):
						if vert_num in written_smooth_verts:
							vert_out = writtenSmoothVerts[vert_num]
						else:
							vert_out = len(self.verts_out)
							written_smooth_verts[vert_num] = vert_out
							self.verts_out.append(formatVector(verts[vert_num]) + "\n")
							self.norms_out.append(formatVector(normals[vert_num]) + "\n")
					else:
						vert_out = len(self.verts_out)
						self.verts_out.append(formatVector(verts[vert_num]) + "\n")
						self.norms_out.append(formatVector(convertCoords(face.normal)) + "\n")
					face_out.append(vert_out)

				writeTri([2, 1, 0])
				#If this is a quad, add another triangle to fill it out.
				if len(face_out) == 4:
					writeTri([0, 3, 2])
		finally:
			# Remove the temporary mesh.
			bpy.data.meshes.remove(mesh)

		with open(self.filename, 'w') as out:
			out.write("NVERTS %d\n" % len(self.verts_out))
			out.write("NFACES %d\n" % len(self.faces_out))

			out.write("VERTEX\n")
			out.writelines(self.verts_out)

			out.write("FACES\n")
			out.writelines(self.faces_out)

			if uvs is not None:
				out.write("TEXTURES\n")
				out.writelines(uvs_out)

			out.write("NORMALS\n")
			out.writelines(self.norms_out)

			out.write("END\n")

class ExportOperator(bpy.types.Operator):
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
		# TODO: put all the write code in here.
		Exporter(self.filepath).write()
		return {'FINISHED'}

	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}

def menu_func(self, context):
	self.layout.operator_context = 'INVOKE_DEFAULT'
	self.layout.operator(ExportOperator.bl_idname, text="Oolite (.dat)")

def register():
	bpy.utils.register_class(ExportOperator)
	bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
	bpy.utils.unregister_class(Exporter)
	bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
	register()
