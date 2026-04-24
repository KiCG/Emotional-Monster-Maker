import bpy
import sys

bpy.ops.wm.open_mainfile(filepath="Emotional-Monster-Maker_template.blend")
render = bpy.context.scene.render
settings = render.image_settings
print(f"File Format: {settings.file_format}")
if settings.file_format == 'FFMPEG':
    print(f"Codec: {render.ffmpeg.codec}")
    print(f"Format: {render.ffmpeg.format}")
    print(f"Color Mode: {settings.color_mode}")
