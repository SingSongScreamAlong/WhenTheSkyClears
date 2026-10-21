import json,shutil
from pathlib import Path
O=Path(__file__).resolve().parents[1];R=O.parents[1]
shutil.copy2(R/'work/first_danger_acting_v067/evidence/dcc_agent_workflows.md',O/'evidence/dcc_agent_workflows.md')
(O/'evidence/REUSE.json').write_text(json.dumps({
 'date':'2026-10-19','guide_contract':'dcc-mcp-production-reuse/v1','guide_source':'Prior verified canonical Core Markdown retained task-locally; substantive Production reuse gate reread and checker passed.',
 'native_discovery':{'query':'layered 2d animation drawing pose; Blender skill','result':'Native MCP search failed: owning CLI list timed out after15 seconds. No ready owned live MCP instance established. No mutation replay.'},
 'official_market':{'query':'layered 2d animation drawing pose grease pencil','candidates':[
 {'name':'Frame By Plane','version':'7.2.1 advertised','url':'https://extensions.blender.org/add-ons/frame-by-plane/','fit':'Image sequences and layered plane workflow already present. Does not supply bespoke character poses or drawing decisions. No package acquired; current output rights and installed compatibility untested.'},
 {'name':'Gp Select','url':'https://extensions.blender.org/add-ons/gp-select/','fit':'Rigging/selection utility; does not create the required performance. No installation or redistribution.'},
 {'name':'GP Tween','version':'2.4.0 advertised','url':'https://extensions.blender.org/add-ons/gp-tween/','fit':'Drawing interpolation utility. Key acting drawings still need authoring; existing native timing/display sufficient. No package acquired.'}]},
 'reuse':'Original project camera, environment, title, color/audio clocks; v067 preserved as before. Reuse installed Blender5.2.2 native mesh drawing, shape/material/action, save/render interfaces. New independent whole-body drawings and manually specified acting keys in a separate candidate.',
 'fallback':'Background native Blender on a new candidate. No claims of live MCP qualification. Source stays read-only. No third-party assets or acquisitions. All new contour drawings task-owned and editable; supplied project art/audio reused within project.',
 'scope':'Full7 seconds G913-1080 at24fps; normal speed before/after; no full-trailer integration.'},indent=2))
print('V068_PREPARED')
