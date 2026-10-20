"""Editable level design source; writes engine-neutral JSON, never flattened scenes."""
import json
from pathlib import Path
P=Path(__file__).resolve().parents[1]

def ground(*spans): return [dict(x=a,y=y,w=b-a,h=600,kind='earth') for a,b,y in spans]
def platform(x,y,w,kind='stone'): return dict(x=x,y=y,w=w,h=27,kind=kind)
def item(kind,x,label='',**extra): return dict(kind=kind,x=x,y=700,label=label,**extra)

levels=[
dict(id='01',title='Before the silence',subtitle='THE VILLAGE',epigraph='Once, the distance between us was only a game.',
 objective='Follow the old road. Stay together.',width=5200,sky='#9da59c',fog='#bfc3ad',cold=0.025,
 ground=ground((0,1450,700),(1570,3350,700),(3495,5200,700)),
 platforms=[platform(1020,648,135),platform(1770,650,190),platform(2300,651,88,'crate'),platform(2420,616,180),platform(3750,635,210)],
 scenery=['village','woods'],
 props=[item('sign',570,'THE OLD ROAD'),item('cart',2080),item('well',3890),item('washing',1090),item('bench',4350)],
 interact=[item('cache',830,'A paper parcel',id='village_parcel',rations=1,scrap=1),item('wheel',2900,'Raise the orchard gate',id='orchard_gate'),item('fire',4040,'The last warm hearth'),item('cache',4600,'Bread left on a sill',id='village_sill',rations=1,scrap=1)],
 gates=[dict(x=3170,y=700,h=185,key='orchard_gate')],
 covers=[dict(x=1870,w=150,kind='wall'),dict(x=4080,w=150,kind='wall')],
 memories=[dict(x=1850,y=610,id='ribbon',text='A blue ribbon. She tied it twice so it would stay.'),dict(x=3840,y=595,id='puddle',text='He used to jump over the puddles just to make her laugh.')],
 checkpoints=[180,1680,3600,4800],
 tutorials=[dict(x=300,text='A / D  move     ·     SPACE  jump     ·     SHIFT  run'),dict(x=760,text='E  search or interact. Some things were left for someone else.'),dict(x=2670,text='The gate has a hand wheel. Stand beside it and press E.'),dict(x=3980,text='Rest at a fire. One ration restores food, warmth and strength.')]),
dict(id='02',title='Where the birds went',subtitle='THE WOODS',epigraph='She waited until he could hear her footsteps again.',
 objective='Cross the logging gate. Leave no one behind.',width=5500,sky='#778e91',fog='#9aafad',cold=.075,
 ground=ground((0,1210,700),(1350,3640,700),(3790,5500,700)),
 platforms=[platform(700,640,150,'log'),platform(1540,642,145,'log'),platform(4050,635,160,'log'),platform(4290,580,220,'log')],
 scenery=['woods'],props=[item('sign',400,'LOGGING ROAD'),item('cart',1640),item('stump',3140),item('stump',4740)],
 interact=[item('cache',940,'A forester’s pack',id='woods_pack',rations=1,scrap=1),item('latch',2790,'Release the gate latch',id='forest_latch'),item('fire',3230,'A sheltered hollow'),item('cache',4490,'A tin beneath the roots',id='woods_tin',rations=1,scrap=1)],
 gates=[dict(x=2580,y=700,h=205,key='forest_latch',plate=2230)],
 covers=[dict(x=1600,w=150,kind='log'),dict(x=3250,w=220,kind='tree')],
 memories=[dict(x=1590,y=600,id='birds',text='They listened. The trees held no birds.'),dict(x=4390,y=538,id='drawing',text='A house, two windows, a sun. Someone had folded it carefully.')],
 checkpoints=[180,1430,2980,4800],
 tutorials=[dict(x=650,text='Q  asks him to wait. Press Q again to call him back.'),dict(x=2040,text='The plate holds the gate. Let him stand on it, then ask him to wait [Q].'),dict(x=2670,text='Release the latch [E] on this side. Then call him through [Q].')]),
dict(id='03',title='Under a borrowed roof',subtitle='THE DISPLACEMENT CAMP',epigraph='The light came first. Then the earth remembered.',
 objective='Find two pieces of salvage. Repair the shelter door.',width=5700,sky='#65787e',fog='#8c9a9c',cold=.5,
 ground=ground((0,1590,700),(1730,3430,700),(3570,5700,700)),
 platforms=[platform(1130,640,190),platform(2310,648,180),platform(3850,640,180)],
 scenery=['camp','battlefield'],props=[item('sign',450,'KEEP LOW'),item('washing',1230),item('cart',3260),item('barricade',4460)],
 interact=[item('cache',720,'An abandoned tool roll',id='camp_tools',scrap=1),item('cache',1910,'Inside a torn rucksack',id='camp_bag',rations=1,scrap=1),item('cache',2840,'A medical tin',id='camp_med',medicine=1,scrap=1),item('repair',4700,'Repair the shelter door · 2 salvage',id='shelter_door'),item('fire',4990,'A roof for a little while'),item('cache',5400,'A shared loaf',id='camp_loaf',rations=1)],
 gates=[dict(x=4880,y=700,h=180,key='shelter_door')],
 covers=[dict(x=1030,w=210,kind='wall'),dict(x=2000,w=240,kind='tent'),dict(x=2790,w=200,kind='wall'),dict(x=3700,w=240,kind='tent'),dict(x=4400,w=250,kind='wall')],
 danger=[600,4650],searchlight=True,
 memories=[dict(x=1200,y=600,id='cup',text='A cup still warm. Whoever was here had not meant to leave.'),dict(x=3910,y=600,id='names',text='Names scratched into a post. Too many to count.')],
 checkpoints=[180,1810,3620,5100],
 tutorials=[dict(x=450,text='Listen for the warning. Reach cover together. Hold S / DOWN to shelter.'),dict(x=1850,text='A moving light sweeps the camp. Crouch behind walls and tents.'),dict(x=4500,text='Search the camp for salvage. The shelter needs two pieces.')]),
dict(id='04',title='The last school',subtitle='THE RUINED STREET',epigraph='The lesson on the board had never been finished.',
 objective='Open the school passage. Keep warm through the rain.',width=5500,sky='#536972',fog='#81969d',cold=.7,
 ground=ground((0,1100,700),(1235,2760,700),(2910,4120,700),(4270,5500,700)),
 platforms=[platform(670,642,160),platform(1600,640,160),platform(1810,580,210),platform(3320,640,200),platform(4530,640,160)],
 scenery=['school','battlefield'],props=[item('sign',300,'SCHOOL'),item('barricade',1440),item('bench',1960),item('cart',3650),item('washing',4830)],
 interact=[item('cache',780,'A lunchbox in the rubble',id='school_food',rations=2),item('wheel',2300,'Open the old service passage',id='school_gate'),item('cache',3190,'The caretaker’s cupboard',id='school_cupboard',medicine=1,scrap=1),item('fire',3800,'A flame out of the rain'),item('cache',4780,'A blanket and a biscuit',id='school_blanket',rations=1)],
 gates=[dict(x=2550,y=700,h=220,key='school_gate')],
 covers=[dict(x=780,w=180,kind='wall'),dict(x=1680,w=200,kind='wall'),dict(x=2390,w=200,kind='wall'),dict(x=3300,w=200,kind='wall'),dict(x=3860,w=200,kind='wall'),dict(x=4670,w=200,kind='wall')],
 danger=[500,5000],searchlight=False,
 memories=[dict(x=1890,y=540,id='lesson',text='Tomorrow, the teacher had written. Nothing after that.'),dict(x=4600,y=600,id='shoe',text='A small shoe beside the road. She turned him away from it.')],
 checkpoints=[180,1350,3020,4380],
 tutorials=[dict(x=450,text='Cold and rain take their strength. Fires cost one ration; use them wisely.'),dict(x=3090,text='H  uses medicine. TAB  opens the pack and survival notes.')]),
dict(id='05',title='The hand that stayed',subtitle='THE ASH FIELDS',epigraph='There was no promise of morning. Only another step.',
 objective='Cross the ash. Take his hand at the far end.',width=5700,sky='#788992',fog='#b0b9b8',cold=.12,
 ground=ground((0,1500,700),(1630,3200,700),(3340,4210,700),(4345,5700,700)),
 platforms=[platform(1070,640,200),platform(1830,640,170,'letter'),platform(2060,584,190,'letter'),platform(2310,640,200,'letter'),platform(3570,640,180,'letter'),platform(3810,580,200,'letter'),platform(4550,640,220,'letter')],
 scenery=['battlefield'],props=[item('sign',480,'KEEP GOING'),item('title',1600)],
 interact=[item('cache',720,'The last parcel',id='ash_parcel',rations=1,medicine=1),item('fire',2850,'A small fire in the ash'),item('end',5400,'Take his hand')],
 gates=[],covers=[dict(x=1120,w=200,kind='wall'),dict(x=2730,w=200,kind='wall'),dict(x=4640,w=220,kind='wall')],
 memories=[dict(x=2150,y=544,id='sun',text='He drew the sun even after he had forgotten its warmth.'),dict(x=3890,y=540,id='hand',text='The hand that pulled him into play was the hand that would not let go.')],
 checkpoints=[180,1710,3400,4900],
 tutorials=[dict(x=480,text='Stay close. There is still a road ahead.'),dict(x=5100,text='Some things survive because we carry them together.')])
]
for l in levels:
    (P/'levels'/f"{l['id']}.json").write_text(json.dumps(l,ensure_ascii=False,indent=2),encoding='utf8')
print('Five connected chapters authored:',sum(l['width'] for l in levels),'world pixels')
