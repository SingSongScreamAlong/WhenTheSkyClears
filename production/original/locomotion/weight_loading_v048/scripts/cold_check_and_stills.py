"""Apply the same cold checks to v048, using its actual rolling-sole contract."""
import sys,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'))
import motion_spec as M
M.configure(json.loads((P/'evidence/SUPPORT_GEOMETRY.json').read_text())['characters'])
s=(ROOT/'locomotion/steady_walk_baseline_v047/scripts/cold_check_and_stills.py').read_text()
s=s.replace('WTSC_Steady_Ordinary_Walk_v047.blend','WTSC_Connected_Weight_Loading_v048.blend').replace('V047 | STEADY ORDINARY WALK | no stumble baseline','V048 | CONNECTED WEIGHT LOADING | ordinary walk').replace('STEADY_WALK_BUILD.json','LOADING_WALK_BUILD.json').replace('V047 | shared travel | steady .73125mps','V048 | shared travel | steady .73125mps').replace('source_v046_unchanged','source_v047_unchanged')
lines=s.splitlines();matches=[i for i,l in enumerate(lines) if l.startswith("tree=ast.parse((P/'scripts/build_steady_walk.py')")];assert len(matches)==1
lines[matches[0]]='''def D(f):return M.D(f)
def foot(g,who,side):
 a,b,m=M.foot(g,who,side);return Vector(a),b,m'''
s='\n'.join(lines).replace('TRAVEL_CURVE_v047.csv','TRAVEL_CURVE_v048.csv').replace("for f in [1,5,9,13,17,21,25,29]","for f in [1,3,5,9,17,19,21,25]").replace('STEADY_%04d.png','LOADING_%04d.png').replace('V047_COLD','V048_COLD')
exec(compile(s,'same_cold_check_v048_support_contract','exec'),globals())
