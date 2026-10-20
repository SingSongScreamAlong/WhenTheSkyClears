"""Author v0.4's decisions and physical route forks from preserved v0.3 data.

The five existing chapters stay intact. New sections add genuinely different
lower/upper paths instead of extending a single compulsory flat corridor.
"""
from pathlib import Path
import json
import math

P=Path(__file__).resolve().parents[1]
BASE=P/'previous/v0.3.0/levels'
WIDTHS=[15000,18600,16000,15400,14200]

# Supplies are authored across the whole journey, rather than giving a meal
# at every search point. Optional high passages keep the strongest food reward.
FOOD={
    'village_parcel':1,'village_sill':1,'orchard_basket':1,
    'mill_garden_basket':1,'mill_kitchen_tin':1,
    'woods_pack':1,'ridge_lunch':1,'woods_canal_ledger':2,'signal_keeper_supper':1,
    'mill_approach_bread':1,
    'camp_bag':1,'camp_loaf':1,'freight_kitchen':1,'freight_bread':1,'station_arcade_loaf':1,
    'school_food':2,'school_blanket':1,'school_kitchen_tin':1,'school_arcade_satchel':2,
    'ash_parcel':1,'ash_garden_tin':1,'terrace_seed_tin':1,'terrace_last_supper':1,
}
SALVAGE={
    'village_parcel':1,'orchard_shed_food':1,'mill_kitchen_tin':1,
    'woods_pack':1,'woods_tin':1,'ridge_scarf':1,'canal_approach_pack':1,
    'camp_tools':1,'camp_bag':1,'camp_med':1,'signal_approach_food':1,'signal_keeper_box':1,
    'school_cupboard':1,'school_staff_flask':1,'arcade_approach_food':1,'library_garden_food':1,
    'garden_table':1,'terrace_last_supper':1,
}
LABELS={
    'orchard_shed_food':'A spool of wire in the empty shed',
    'woods_tin':'A tin of nails beneath the roots',
    'ridge_scarf':'A length of wire wrapped in a scarf',
    'woods_keeper_tin':'The keeper’s medical tin',
    'woods_high_sack':'A bandage on the high shelf in a ruined hut',
    'canal_approach_pack':'The canal keeper’s copper and wire',
    'signal_approach_food':'A wire stores tin behind the drainage door',
    'school_staff_flask':'The caretaker’s ties and wire in the staff room',
    'arcade_approach_food':'Wire in a dry kitchen tin',
    'library_garden_food':'A bundle of useful ties in the greenhouse corner',
    'garden_table':'A repaired cup and a length of garden wire',
    'terrace_bowl':'A bandage in a bowl beneath a dry stone',
}


def terrain(l,x,w,profile,kind='earth'):
    l['ground'].append(dict(x=x,y=700,w=w,h=650,kind=kind,profile=profile))


def floor_y(l,x):
    for g in reversed(l['ground']):
        if g['x']<=x<=g['x']+g['w']:
            points=g.get('profile',[[0,0],[g['w'],0]])
            for a,b in zip(points,points[1:]):
                if a[0]<=x-g['x']<=b[0]:
                    return round(g['y']+a[1]+(b[1]-a[1])*(x-g['x']-a[0])/(b[0]-a[0]),3)
            return g['y']
    raise ValueError(('Missing ground',x))


def item(l,kind,x,label,ident=None,y=None,**extra):
    p=dict(kind=kind,x=x,y=floor_y(l,x) if y is None else y,label=label,
           hold_seconds={'cache':1.2,'fire':4.0,'relay':3.2,'clear':2.8,
                         'brace':3.5,'pump':4.0}.get(kind,2.0))
    if ident:p['id']=ident
    if kind=='relay':p['companion_required']=True
    p.update(extra)
    l['interact'].insert(-1 if l['id'] in ['04','05'] else len(l['interact']),p)
    return p


def gate(l,x,key,kind='barrier',y=None,h=190):
    l['gates'].append(dict(x=x,y=floor_y(l,x) if y is None else y,h=h,key=key,kind=kind))


def cover(l,x,w=300,kind='wall',y=None):
    l['covers'].append(dict(x=x,w=w,kind=kind,y=floor_y(l,x) if y is None else y))


def station(l,x,ident,label,rations=1,scrap=0,medicine=0):
    item(l,'cache',x-110,label,ident,rations=rations,scrap=scrap,medicine=medicine)
    item(l,'fire',x+70,'Share warmth before choosing the next way')
    cover(l,x+35,390,'tent')
    l['safe_zones'].append(dict(x=x+35,w=390))
    l['checkpoints'].append(x+35)


def lane(l,x,w,kind,period,active,offset,key=None,**extra):
    p=dict(x=x,w=w,kind=kind,period=period,active=active,offset=offset)
    if key:p['key']=key
    p.update(extra);l['hazard_lanes'].append(p)
    cover(l,x-150);cover(l,x+w+150)
    return p


def clue(l,x,text):l['tutorials'].append(dict(x=x,text=text))


def memory(l,x,ident,text,y=None):
    l['memories'].append(dict(x=x,y=floor_y(l,x)-64 if y is None else y,id=ident,text=text))


def prop(l,kind,x,label=''):
    l['props'].append(dict(kind=kind,x=x,y=floor_y(l,x),label=label))


def high_route(l,ident,entry,exit_x,steps,brace_x,gate_x,cache_x,
               safe_key,cache_id,pump_id,lower_y,upper_y,label):
    indices=[]
    for x,y,w in steps:
        indices.append(len(l['platforms']))
        l['platforms'].append(dict(x=x,y=y,w=w,h=20,kind='scaffold',
             one_way=True,optional_route=True,route=ident))
    item(l,'brace',brace_x,'Lash the upper passage open · 1 salvage',safe_key,
         y=upper_y,optional=True,route=ident)
    gate(l,gate_x,safe_key,'upper_crossbar',y=upper_y,h=174)
    item(l,'cache',cache_x,label,cache_id,y=upper_y,optional=True,
         route='branch_supply',branch=ident,rations=2,medicine=1)
    cover(l,cache_x,230,'tent',y=upper_y)
    l['branch_routes'].append(dict(id=ident,entry_x=entry,exit_x=exit_x,
         from_x=entry,to_x=exit_x,upper_y=upper_y,lower_y=lower_y,
         safe_key=safe_key,cache_id=cache_id,pump_id=pump_id,
         cost=1,platform_indices=indices,
         description='The lower canal costs warmth and makes noise. Spend one salvage at the pump to drain it, or climb and spend that salvage on the upper crossbar. The upper path stays dry and reaches a finite food/medicine cache. Crouching quietly through the lower water remains a no-salvage alternative.'))
    clue(l,entry-160,'Two ways: the water below, or the boards above. One piece of salvage can make either way safer.')
    clue(l,entry+150,'Jump onto the upper boards to climb. Keep walking underneath to take the lower way.')


levels=[]
for number,width in enumerate(WIDTHS,1):
    l=json.loads((BASE/f'{number:02}.json').read_text(encoding='utf8'))
    old_width=int(l['width'])
    l.update(build='0.4.0',width=width,route_length_units=width,
             previous_route_end=old_width,branch_routes=[],mechanisms=[])

    if number==1:
        l['objective']='Beyond the orchard, choose when to spend what you have. Bring him through the old mill road.'
        terrain(l,10800,1400,[[0,0],[250,0],[600,-76],[920,-76],[1270,0],[1400,0]])
        terrain(l,12200,1400,[[0,0],[250,0],[550,44],[850,44],[1190,0],[1400,0]])
        terrain(l,13600,1400,[[0,0],[420,0],[680,-42],[940,-42],[1220,0],[1400,0]])
        l['zones'] += [dict(x=10800,w=1400,theme='terraced_garden',caption='The mill gardens'),
                       dict(x=12200,w=1400,theme='canal',caption='The dry floodbank'),
                       dict(x=13600,w=1400,theme='drainage_tunnel',caption='Under the old mill')]
        station(l,10960,'mill_garden_basket','A basket in a sheltered allotment',rations=2,scrap=1)
        lane(l,12010,440,'wind',12.0,2.5,4.0)
        clue(l,11810,'The bank is exposed. A fast crossing spends strength; a low crossing waits out the wind.')
        item(l,'cache',12790,'A keeper’s coat in the flooded grass','mill_keeper_coat',rations=1,medicine=1,optional=True)
        item(l,'relay',13220,'Lift the old mill-road beam together','mill_road_beam')
        gate(l,13460,'mill_road_beam','fallen_bough')
        station(l,13700,'mill_kitchen_tin','Bread in the old mill kitchen',rations=1,scrap=1)
        item(l,'brace',14130,'Secure the mill passage roof · 1 salvage','mill_passage_roof',optional=True)
        lane(l,14240,260,'debris',12.0,2.2,6.0,'mill_passage_roof')
        clue(l,14050,'There is wire for one repair. Keep it, or spend it here and make the roof safe for him.')
        item(l,'clear',14700,'Lift the tangled roots from the mill exit','mill_roots')
        gate(l,14860,'mill_roots','fallen_bough')
        memory(l,11570,'mill_handprints','Handprints in the old mortar. His hand was nearly the same size.')
        memory(l,12950,'mill_waterline','A line on the wall showed where the water had reached. Above their heads.')
        prop(l,'well',11020);prop(l,'bench',11690);prop(l,'cart',13290)
        prop(l,'washing',13890);prop(l,'sign',14900,'THE LOW ROAD')
        l['checkpoints'] += [12670,13600,14640]

    elif number==2:
        l['objective']='Find the drainage way. Decide whether to spend salvage below, or climb to the dry boards above.'
        terrain(l,11200,700,[[0,0],[180,0],[370,28],[500,28],[700,0]])
        terrain(l,11900,1850,[[0,0],[280,0],[580,80],[1280,80],[1550,0],[1850,0]])
        terrain(l,13750,1650,[[0,0],[350,0],[700,-58],[1040,-58],[1370,0],[1650,0]])
        l['zones'] += [dict(x=11200,w=700,theme='drainage_tunnel',caption='The drainage mouth'),
                       dict(x=11900,w=1850,theme='canal',caption='Below the towing path'),
                       dict(x=13750,w=1650,theme='signal_yard',caption='An abandoned signal hut')]
        station(l,11580,'canal_approach_pack','The canal keeper’s emergency bag',rations=2,scrap=1)
        item(l,'pump',11920,'Drain the canal · 1 salvage · both children','woods_canal_drain',
             scrap_cost=1,companion_required=True,optional=True)
        l['water_zones'].append(dict(x=12420,w=700,top=754,key='woods_canal_drain'))
        high_route(l,'woods_canal_high',11980,13730,
            [(12000,640,150),(12190,580,150),(12380,540,900),
             (13320,600,170),(13530,650,170)],
            12550,12650,12900,'woods_canal_crossbar','woods_canal_ledger','woods_canal_drain',780,540,
            'A dry medicine case on the towing-path shelf')
        lane(l,12420,700,'listener',16.0,3.0,2.0,feet_min_y=650)
        clue(l,12230,'Someone listens beyond the canal. Running, moving crates and splashing carry. Crouch in the water to keep both of you quiet.')
        station(l,13900,'signal_keeper_supper','A supper tin in the signal hut',rations=1,scrap=1)
        item(l,'clear',14600,'Move the sleepers from the signal path','woods_signal_sleepers')
        gate(l,14800,'woods_signal_sleepers','rubble')
        memory(l,11750,'canal_rope','The rope was worn smooth where many hands had held it.')
        memory(l,12890,'canal_ledger_memory','A name, a date, a small drawing of a boat. She kept the page dry.',y=475)
        memory(l,14320,'signal_left_on','The lamp had been left on. Someone had expected to return before dark.')
        prop(l,'cart',11470);prop(l,'sign',11840,'TOWING PATH')
        prop(l,'well',12160);prop(l,'bench',13880);prop(l,'barricade',14550)
        l['checkpoints'] += [11860,13720,14000,15100]
        # The mill's bridge, wheel and moving gate are mechanism-owned native
        # collision bodies. Do not put decorative duplicate solids in bridges
        # or gates: the continuous route must use the actual coupled encounter.
        terrain(l,15400,320,[[0,0],[320,0]])
        terrain(l,15930,2670,[[0,0],[2670,0]])
        l['zones'].append(dict(x=15400,w=3200,theme='mill',caption='The mill chain'))
        station(l,15530,'mill_approach_bread','A little bread beneath the mill eaves',rations=1)
        l['mechanisms'].append(dict(kind='breakaway_mill',id='woods_mill',
            key='mill_gate_open',bridge_x=15720,bridge_y=700,bridge_w=210,bridge_h=20,
            wheel_x=16700,wheel_y=604,radius=96,gate_x=17350,gate_y=700,gate_h=205,
            travel_required=240,load_seconds=.4,warning_seconds=1.2,roll_direction=1,
            retreat_x=16540,exit_x=17800))
        l['platforms'] += [dict(x=16320,y=640,w=150,h=20,kind='scaffold',one_way=True,route='mill_wheel_approach'),
                           dict(x=16510,y=580,w=125,h=20,kind='scaffold',one_way=True,route='mill_wheel_approach')]
        clue(l,15600,'The bridge and the mill gate are still joined by the old chain.')
        clue(l,16200,'Jump up the boards. The wheel’s weight can pull the gate. Keep a way back for him.')
        clue(l,16600,'The frame is giving way. Get both children clear when the chain begins to strain.')
        memory(l,16070,'mill_fence_marks','The marks on the fence were worn by hands waiting for the wheel to turn.')
        memory(l,18050,'mill_chain_silence','The chain fell quiet behind them. He waited for the sound to end before letting go.')
        prop(l,'sign',18480,'THE CAMP')
        l['checkpoints'] += [15500,17800,18200]

    elif number==3:
        l['objective']='Cross the signal yard. A quiet stop can turn the light away; an exposed rush leaves him behind.'
        terrain(l,11800,1400,[[0,0],[350,0],[700,-64],[1000,-64],[1400,0]],'stone')
        terrain(l,13200,1700,[[0,0],[300,0],[600,56],[1000,56],[1400,0],[1700,0]],'stone')
        terrain(l,14900,1100,[[0,0],[250,0],[520,-44],[760,-44],[1030,0],[1100,0]],'stone')
        l['zones'] += [dict(x=11800,w=1400,theme='drainage_tunnel',caption='A way beneath the freight road'),
                       dict(x=13200,w=1700,theme='signal_yard',caption='The signal yard'),
                       dict(x=14900,w=1100,theme='shattered_arcade',caption='The station arcade')]
        station(l,12080,'signal_approach_food','A stores tin behind the drainage door',rations=2,scrap=1)
        lane(l,13020,420,'wind',12.5,2.5,5.0)
        item(l,'cache',13570,'Inside the switch keeper’s box','signal_keeper_box',rations=1,scrap=1,optional=True)
        item(l,'relay',14040,'Turn the yard signal together','camp_yard_signal',optional=True)
        cover(l,14050,310,'tent')
        clue(l,13880,'Four hands can turn the signal away. Or wait for the light and cross while it is gone.')
        # Retain a sweep as this chapter's terminal lane for the older patrol fixture.
        lane(l,14300,480,'sweep',13.5,2.6,3.0,'camp_yard_signal')
        station(l,15000,'station_arcade_loaf','A loaf wrapped in a damp timetable',rations=1,scrap=1)
        item(l,'clear',15300,'Clear the fallen arcade stones','camp_arcade_stones')
        gate(l,15520,'camp_arcade_stones','rubble')
        memory(l,12650,'signal_whistle','He raised an empty fist to his mouth. The train sound did not come.')
        memory(l,13720,'signal_buttons','Three bright buttons in a tin. He chose the blue one and put the others back.')
        memory(l,15740,'station_roots','A root had found a crack between the tiles. It was growing toward the light.')
        prop(l,'barricade',12290);prop(l,'cart',13320);prop(l,'washing',14200)
        prop(l,'bench',15120);prop(l,'sign',15880,'THE SCHOOL ROAD')
        l['checkpoints'] += [12900,13850,14900,15800]

    elif number==4:
        l['objective']='Past the classrooms, choose the broken arcade: a wet quiet way below, or the dry upper gallery.'
        terrain(l,11400,700,[[0,0],[400,0],[520,24],[590,24],[700,0]],'stone')
        terrain(l,12100,2200,[[0,0],[160,0],[460,60],[1600,60],[2070,0],[2200,0]],'stone')
        terrain(l,14300,1100,[[0,0],[260,0],[530,-64],[790,-64],[1060,0],[1100,0]],'stone')
        l['zones'] += [dict(x=11400,w=700,theme='drainage_tunnel',caption='Behind the school kitchens'),
                       dict(x=12100,w=2200,theme='shattered_arcade',caption='The broken gallery'),
                       dict(x=14300,w=1100,theme='terraced_garden',caption='The garden behind the library')]
        station(l,11690,'arcade_approach_food','A dry tin under the kitchen stair',rations=2,scrap=1)
        item(l,'pump',12010,'Drain the arcade · 1 salvage · both children','school_arcade_drain',
             scrap_cost=1,companion_required=True,optional=True)
        l['water_zones'].append(dict(x=12620,w=760,top=744,key='school_arcade_drain'))
        high_route(l,'school_arcade_high',12120,14220,
            [(12140,640,150),(12330,580,150),(12520,540,1220),
             (13780,600,170),(13990,650,170)],
            12720,12830,13320,'school_arcade_crossbar','school_arcade_satchel','school_arcade_drain',760,540,
            'The nurse’s dry satchel in the upper gallery')
        lane(l,12620,760,'listener',17.0,3.0,8.0,feet_min_y=650)
        clue(l,12430,'The water makes every footstep louder. A crouched crossing is slow but quiet. Keep him beside you.')
        station(l,14400,'library_garden_food','A biscuit tin in a greenhouse corner',rations=1,scrap=1)
        item(l,'clear',14840,'Move the greenhouse frames from the road','school_greenhouse_frames')
        gate(l,15060,'school_greenhouse_frames','fallen_shelf')
        memory(l,11960,'arcade_cooking_marks','Pencil marks beside the kitchen door measured someone growing taller.')
        memory(l,13330,'arcade_sun_paper','A yellow paper sun. There was still a fold where it had been held.',y=475)
        memory(l,14680,'greenhouse_soil','He brushed the broken glass away from a little square of soil.')
        prop(l,'bench',11770);prop(l,'washing',12120);prop(l,'cart',13650)
        prop(l,'well',14490);prop(l,'sign',15280,'THE GARDENS')
        l['checkpoints'] += [12060,14220,14500,15220]

    elif number==5:
        l['objective']='There are gardens beyond the ash. Keep a little strength for both of you. Keep going together.'
        terrain(l,10800,1200,[[0,0],[260,0],[570,-92],[840,-92],[1170,0],[1200,0]])
        terrain(l,12000,1200,[[0,0],[220,0],[500,38],[790,38],[1100,0],[1200,0]])
        terrain(l,13200,1000,[[0,0],[220,0],[450,-44],[650,-44],[850,0],[1000,0]])
        l['zones'] += [dict(x=10800,w=1200,theme='terraced_garden',caption='The first living terraces'),
                       dict(x=12000,w=1200,theme='canal',caption='The garden watercourse'),
                       dict(x=13200,w=1000,theme='terraced_garden',caption='The hand that stayed')]
        # The previous final doorway is retained as a memory of a threshold,
        # while the actual ending remains the same held hand-taking action.
        l['interact'][-1]['x']=13900;l['interact'][-1]['y']=floor_y(l,13900)
        station(l,10980,'terrace_seed_tin','Bread beneath a packet of seeds',rations=2,scrap=1)
        lane(l,11520,360,'wind',13.0,2.4,1.0)
        clue(l,11330,'The high terraces catch the wind first. Slow down before he spends the last of his strength.')
        item(l,'relay',12350,'Lift the garden trellis together','ash_garden_trellis')
        gate(l,12590,'ash_garden_trellis','fallen_bough')
        item(l,'cache',12910,'A bowl set beneath a dry stone','terrace_bowl',rations=1,optional=True)
        station(l,13220,'terrace_last_supper','A little bread in a folded cloth',rations=1,scrap=1)
        item(l,'brace',13500,'Tie the greenhouse beam · 1 salvage','ash_greenhouse_beam',optional=True)
        lane(l,13620,220,'debris',12.0,2.0,5.0,'ash_greenhouse_beam')
        clue(l,13400,'One more roof. One more choice to make before he passes beneath it.')
        memory(l,11280,'terrace_first_leaf','The green was too small to see from the road. He had seen it first.')
        memory(l,12740,'terrace_water','He cupped his hands below the slow drip. She waited until they were steady.')
        memory(l,13860,'terrace_ribbon','She tied the ribbon twice. This time he held the ends.')
        for t in l['tutorials']:
            if t['x']==10400:t['x']=13830
        prop(l,'bench',11080);prop(l,'well',12220);prop(l,'washing',13040)
        prop(l,'bench',13980)
        l['checkpoints'] += [12000,12680,13200,13870]

    for cache in l['interact']:
        if cache['kind']=='cache':
            ident=cache['id']
            cache['rations']=FOOD.get(ident,0)
            cache['scrap']=SALVAGE.get(ident,0)
            if ident in ['woods_high_sack','terrace_bowl']:cache['medicine']=1
            if ident in LABELS:cache['label']=LABELS[ident]
            assert cache['rations']+cache['scrap']+cache.get('medicine',0)>0,ident
    l['checkpoints']=sorted(set(l['checkpoints']))
    assert l['interact'][1]['kind']=='bridge' if number==2 else True
    assert l['interact'][-1]['id']=='school_drain' if number==4 else True
    assert l['interact'][-1]['kind']=='end' if number==5 else True
    original=json.loads((BASE/f'{number:02}.json').read_text(encoding='utf8'))
    first_cache=next(p for p in l['interact'] if p['kind']=='cache')
    original_first=next(p for p in original['interact'] if p['kind']=='cache')
    assert first_cache['id']==original_first['id']
    assert all(first_cache.get(k,0)==original_first.get(k,0) for k in ['rations','scrap','medicine'])
    if number==3:assert sum(p.get('scrap',0) for p in l['interact'] if p['kind']=='cache' and p['x']<4670)==3
    ids=[p['id'] for p in l['interact'] if p.get('id')]
    assert len(ids)==len(set(ids))
    for g in l['ground']:
        profile=g.get('profile',[])
        if profile:
            assert profile[0]==[0,0] and profile[-1]==[g['w'],0]
            for a,b in zip(profile,profile[1:]):
                assert b[0]>a[0]
                assert abs(math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])))<18.0
    for h in l['hazard_lanes']:
        assert h['x']>=0 and h['x']+h['w']<width
        if h['kind']!='listener':
            assert (h['w']+150)/166 < h['period']-h['active']-1.0
    for route in l['branch_routes']:
        assert route['entry_x']<route['exit_x']<width
        assert route['upper_y']<650<route['lower_y']
        assert all(l['platforms'][j]['one_way'] for j in route['platform_indices'])
        assert any(p.get('id')==route['pump_id'] and p.get('scrap_cost')==1 and p.get('companion_required') for p in l['interact'])
        assert any(p.get('id')==route['safe_key'] and p['kind']=='brace' for p in l['interact'])
        route_platforms=[l['platforms'][j] for j in route['platform_indices']]
        assert route['entry_x']<=route_platforms[0]['x']
        assert route['exit_x']>=route_platforms[-1]['x']+route_platforms[-1]['w']
        for a,b in zip(route_platforms,route_platforms[1:]):
            assert b['x']-(a['x']+a['w'])<=50
            assert a['y']-b['y']<=60
        upper_gate=next(g for g in l['gates'] if g['key']==route['safe_key'])
        upper_brace=next(p for p in l['interact'] if p.get('id')==route['safe_key'])
        assert upper_brace['y']==upper_gate['y']==route['upper_y']
        assert 40<=upper_gate['x']-upper_brace['x']<=120
        # A standing girl must physically fit below the upper-only crossbar.
        # No keyed wall may make the lower wet route require a resource spend.
        for g in l['gates']:
            if route['entry_x']<=g['x']<=route['exit_x']:
                assert floor_y(l,g['x'])-99>g['y']+20
        water=next(w for w in l['water_zones'] if w['key']==route['pump_id'])
        assert floor_y(l,water['x']+water['w']/2)>water['top']+8
        listeners=[h for h in l['hazard_lanes'] if h['kind']=='listener'
                   and h['x']<route['exit_x'] and h['x']+h['w']>route['entry_x']]
        assert len(listeners)==1
        assert listeners[0]['feet_min_y']>route['upper_y']+50
    for mechanism in l['mechanisms']:
        assert mechanism['kind']=='breakaway_mill'
        assert mechanism['wheel_y']+mechanism['radius']==700
        assert mechanism['travel_required']==240
        assert mechanism['wheel_x']+mechanism['travel_required']+100<mechanism['gate_x']
        assert mechanism['bridge_x']+mechanism['bridge_w']<mechanism['wheel_x']-500
        assert not any(g['x']<=mechanism['bridge_x']+mechanism['bridge_w']/2<=g['x']+g['w'] for g in l['ground'])
        assert floor_y(l,mechanism['wheel_x']-150)==floor_y(l,mechanism['wheel_x']+400)==700
        assert not any(g['key']==mechanism['key'] for g in l['gates'])
        assert not any(b.get('key')==mechanism['key'] for b in l.get('bridges',[]))
    (P/'levels'/f'{number:02}.json').write_text(json.dumps(l,ensure_ascii=False,indent=2),encoding='utf8')
    levels.append(l)

assert sum(p.get('rations',0) for l in levels for p in l['interact'])==26
assert sum(p.get('scrap',0) for l in levels for p in l['interact'])==18
print(json.dumps(dict(build='0.4.0',route_units=sum(l['width'] for l in levels),
    previous_route_units=56000,physical_branch_routes=sum(len(l['branch_routes']) for l in levels),
    listener_lanes=sum(h['kind']=='listener' for l in levels for h in l['hazard_lanes']),
    paid_pumps=sum(p['kind']=='pump' and p.get('scrap_cost')==1 for l in levels for p in l['interact']),
    coupled_native_mechanisms=sum(len(l['mechanisms']) for l in levels),
    total_timed_hazard_lanes=sum(len(l['hazard_lanes']) for l in levels),
    total_held_physical_actions=sum(p['kind'] in ['relay','clear','brace'] for l in levels for p in l['interact']),
    finite_supplies=dict(food=sum(p.get('rations',0) for l in levels for p in l['interact']),
                         salvage=sum(p.get('scrap',0) for l in levels for p in l['interact']),
                         medicine=sum(p.get('medicine',0) for l in levels for p in l['interact'])),
    chapters=[dict(id=l['id'],width=l['width'],branch_routes=l['branch_routes'],
                   food=sum(p.get('rations',0) for p in l['interact'] if p['kind']=='cache')) for l in levels]),indent=2))
