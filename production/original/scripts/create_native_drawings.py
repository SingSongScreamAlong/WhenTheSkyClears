"""Create imagegen-derived GP outlines through the discovered typed DCC tool."""
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CLI=r'WTSC_LOCAL_USER\AppData\Local\dcc-mcp\bin\dcc-mcp-cli.exe'
PREFIX='blender.dda6f921.'
LOG=ROOT/'notes/native_drawing_calls.jsonl'

def call(tool,args):
    payload=ROOT/'notes/dcc_payload.json'
    payload.write_text(json.dumps(args),encoding='utf-8')
    p=subprocess.run([CLI,'--transport','mcp','call',PREFIX+tool,'--json-file',str(payload)],capture_output=True,text=True,encoding='utf-8')
    lines=[line for line in p.stdout.splitlines() if line.startswith('{')]
    records=[json.loads(line) for line in lines]
    with LOG.open('a',encoding='utf-8') as f:
        for r in records: f.write(json.dumps(r)+'\n')
    if p.returncode or not records or not records[0].get('success'):
        raise RuntimeError((p.stdout+p.stderr)[-3000:])
    return records[0]

def part_points(name,data):
    # Source landmarks are measured on the actual generated drawing sheet.
    anchors={
      'head':(225,260,.00120,0,1.09),
      'dress':(195,20,.00180,0,1.085),
      'braid':(152,83,.00115,-.113,1.265),
      'upper_arm_near':(206,37,.00135,.015,1.045),
      'upper_arm_far':(185,37,.00135,-.015,1.045),
      'forearm_near':(185,42,.00123,.015,.815),
      'forearm_far':(174,35,.00120,-.015,.815),
      'thigh_near':(192,30,.00192,0,.68),
      'thigh_far':(153,30,.00192,0,.68),
      'shin_near':(181,31,.00186,0,.36),
      'shin_far':(192,31,.00163,0,.36),
      'shoe_near':(137,125,.00120,0,.09),
      'shoe_far':(176,139,.00120,0,.09),
    }
    ax,ay,s,wx,wy=anchors[name]
    z={ 'thigh_far':-.045,'shin_far':-.044,'shoe_far':-.043,
        'upper_arm_far':-.040,'forearm_far':-.039,
        'braid':-.025,'head':.002,'dress':.01,
        'thigh_near':-.005,'shin_near':-.004,'shoe_near':-.003,
        'upper_arm_near':.030,'forearm_near':.031 }[name]
    return [[round((x-ax)*s+wx,6),round((ay-y)*s+wy,6),z] for x,y in data]

def main():
    source=json.loads((ROOT/'characters/Girl_Parts_Contours_v001.json').read_text())
    for name,part in source['parts'].items():
        obj='GP_Girl_'+name
        call('blender_grease_pencil__create_object',{'name':obj})
        color=[.009,.011,.015,1] if 'far' not in name else [.018,.022,.029,1]
        strokes=[{'points':part_points(name,part['outline']), 'material_name':'Charcoal_'+('far' if 'far' in name else 'near'),
                  'color':color,'fill_color':color,'cyclic':True,'show_stroke':False,'radius':.001}]
        if name=='braid':
            for contour in part.get('ribbon_contours',[]):
                strokes.append({'points':part_points(name,contour),'material_name':'Faded_Blue_Ribbon','color':[.085,.19,.27,1],
                                'fill_color':[.085,.19,.27,1],'cyclic':True,'show_stroke':False,'radius':.001})
        call('blender_grease_pencil__add_drawing',{'object_name':obj,'layer_name':name,'frame':1,'strokes':strokes,'use_lights':False})
        print(obj,len(part['outline']),flush=True)

if __name__=='__main__':main()
