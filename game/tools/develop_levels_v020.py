"""Second-pass encounter design over the preserved first build. Repeatable."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]
for i in range(1,6):
    l=json.loads((P/'previous/v0.1.0/levels'/f'{i:02}.json').read_text(encoding='utf8'))
    l['build']='0.2.0';l['bridges']=[];l['pushables']=[];l['water_zones']=[];l['safe_zones']=[]
    for p in l['interact']:p['hold_seconds']={'cache':1.1,'wheel':2.0,'latch':1.1,'repair':3.2,'fire':4.0,'end':1.5}.get(p['kind'],1)
    if i==1:
        l['objective']='Find the orchard wheel. Get the two of you beyond the village.'
        l['pushables']=[dict(id='orchard_crate',x=2190,y=672)]
        l['platforms']=[p for p in l['platforms'] if p['x'] not in [1020,2300]]
        l['safe_zones']=[dict(x=3920,w=340)]
        l['tutorials'][0]['text']='A / D  walk     ·     SPACE  jump     ·     SHIFT  run'
        l['tutorials'][1]['text']='Hold E to search. Moving away or letting go interrupts the task.'
        l['tutorials'].append(dict(x=2130,text='Hold E and move against the crate to push. Climb it to reach the wall.'))
        l['tutorials'].append(dict(x=1250,text='Hold SHIFT across a long gap. Release SPACE early for a short jump.'))
    if i==2:
        # A real bridge is needed: the stream is deliberately too wide to jump.
        l['ground'][0]['w']=1210;l['ground'][1]['x']=1540;l['ground'][1]['w']=2100
        l['bridges']=[dict(x=1205,y=700,w=340,h=15,key='forest_bridge')]
        l['interact'].insert(1,dict(kind='bridge',x=1070,y=700,id='forest_bridge',label='Lower the old crossing',hold_seconds=2.4))
        l['tutorials'].append(dict(x=1050,text='The stream has taken the crossing. Hold E at the winch to lower it.'))
        l['pushables']=[dict(id='logging_crate',x=2020,y=672)]
        l['objective']='Lower the crossing. Find a way through the logging gate together.'
        l['tutorials'][1]['text']='The gate needs weight on the plate. Ask him to wait [Q], or push the crate onto it.'
        l['water_zones']=[dict(x=1210,w=330,top=740,key='forest_bridge')]
        l['safe_zones']=[dict(x=3150,w=300)]
    if i==3:
        l['objective']='Open the buried shelter. Repair the roof. Bring him to the stove.'
        l['interact']=[p for p in l['interact'] if p.get('id')!='shelter_door']
        l['interact'].insert(-2,dict(kind='repair',x=4670,y=700,id='shelter_door',label='Clear and brace the shelter door · 2 salvage',hold_seconds=3.5))
        l['interact'].insert(-2,dict(kind='roof',x=4990,y=700,id='shelter_roof',label='Patch the leaking roof · 1 salvage',hold_seconds=3.0))
        for p in l['interact']:
            if p['kind']=='fire':p['x']=5240
        l['safe_zones']=[dict(x=5070,w=430,key='shelter_door')]
        l['covers'] += [dict(x=800,w=200,kind='wall'),dict(x=1450,w=190,kind='wall'),dict(x=3300,w=210,kind='wall')]
        l['tutorials'][0]['text']='The light can find either of you. Keep both children low, behind solid cover.'
        l['tutorials'] += [dict(x=4880,text='The shelter leaks. Salvage for the roof, or save it. Hold E at the damaged beam.')]
    if i==4:
        l['objective']='Find the service passage. Drain the flooded school yard.'
        l['water_zones']=[dict(x=2970,w=570,top=684,key='school_drain')]
        l['interact'].append(dict(kind='pump',x=3190,y=700,id='school_drain',label='Work the old drainage pump',hold_seconds=4.0))
        l['gates'].append(dict(x=3520,y=700,h=160,key='school_drain'))
        l['safe_zones']=[dict(x=3840,w=310)]
        l['tutorials'].append(dict(x=3040,text='Water will soak their clothes and steal their warmth. Find the caretaker’s pump.'))
    if i==5:
        l['objective']='Stay together through the ash. Reach the last doorway.'
        l['safe_zones']=[dict(x=2830,w=220)]
        # A narrow final rest lets the accumulated survival state matter.
        for p in l['interact']:
            if p['kind']=='end':p['hold_seconds']=2.0
    (P/'levels'/f'{i:02}.json').write_text(json.dumps(l,ensure_ascii=False,indent=2),encoding='utf8')
print('v0.2: bridge, physical crates, shelter repair, leaking roof, flood and pump authored.')
