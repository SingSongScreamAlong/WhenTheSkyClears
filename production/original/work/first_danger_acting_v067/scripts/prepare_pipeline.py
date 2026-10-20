from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];S=P.parent/'first_danger_acting_v066'
(P/'evidence/dcc_agent_workflows.md').write_bytes((S/'evidence/dcc_agent_workflows.md').read_bytes())
reuse=json.loads((S/'evidence/reuse_investigation.json').read_text())
reuse['scope']='Continue v066: hand receiving, contact settle, free-arm posing, native blinks and braid lag; same original paintings.'
reuse['continuation']='Same active session and host. Reuse existing project limb solver, drawing caches and successful native 5.2.2 interfaces. Earlier live MCP inventory timed out. No new package fills the bespoke performance gap; no installation or asset acquisition.'
(P/'evidence/reuse_investigation.json').write_text(json.dumps(reuse,indent=2))
for name in ['render_review.py','render_batches.py','validate_candidate.py','verify_review.py']:
 t=(S/'scripts'/name).read_text().replace('v066','v067').replace('V066','V067')
 (P/'scripts'/name).write_text(t)
t=(S/'scripts/package_review.py').read_text().replace('v066','v067').replace('V066','V067')
t=t.replace("R/'work/first_danger_conform_v065/previews/WTSC_First_Danger_Title_v065f_View.mp4'", "R/'work/first_danger_acting_v066/previews/WTSC_First_Danger_Acting_v066_Title_24fps.mp4'")
t=t.replace("R/'work/first_danger_conform_v065/previews/WTSC_First_Danger_Unmasked_v065_4K.mp4'", "R/'work/first_danger_acting_v066/previews/WTSC_First_Danger_Acting_v066_Unmasked_24fps.mp4'")
t=t.replace('BEFORE  |  existing passage','BEFORE  |  v066').replace('AFTER  |  rebuilt acting','AFTER  |  v067 refinement')
(P/'scripts/package_review.py').write_text(t)
print('V067_PIPELINE_READY')
