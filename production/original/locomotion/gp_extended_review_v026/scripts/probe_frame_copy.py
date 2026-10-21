import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];g=bpy.data.grease_pencils.new('frame copy probe');l=g.layers.new('probe',set_active=True);l.frames.new(1)
r={'functions':{fn.identifier:[{'name':p.identifier,'type':p.type} for p in fn.parameters] for fn in l.frames.bl_rna.functions},'copy_doc':l.frames.copy.__doc__}
(P/'evidence/FRAME_COPY_RUNTIME_API.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
