"""Author the v0.3 journey from the immutable v0.2 chapter snapshot.

Old encounter coordinates and test-sensitive interaction ordering are retained.
The additional route is authored data, not procedural endless terrain.
"""
from pathlib import Path
import json
import math

P = Path(__file__).resolve().parents[1]
BASE = P / 'previous/v0.2.0/levels'
WIDTHS = [10800, 11200, 11800, 11400, 10800]


def terrain(level, start, width, profile, kind='earth'):
    level['ground'].append(dict(x=start, y=700, w=width, h=600,
                                kind=kind, profile=profile))


def floor_y(level, x):
    for g in reversed(level['ground']):
        if g['x'] <= x <= g['x'] + g['w']:
            points = g.get('profile', [[0, 0], [g['w'], 0]])
            local = x - g['x']
            for (ax, ay), (bx, by) in zip(points, points[1:]):
                if ax <= local <= bx:
                    return round(g['y'] + ay + (by-ay)*(local-ax)/(bx-ax), 2)
            return g['y']
    raise ValueError(f'No walkable floor at {x}')


def item(level, kind, x, label, ident=None, **extra):
    p = dict(kind=kind, x=x, y=floor_y(level, x), label=label,
             hold_seconds={'cache':1.2, 'fire':4.0, 'clear':2.8,
                           'relay':3.2, 'brace':3.5}.get(kind, 2.0))
    if ident:
        p['id'] = ident
    if kind == 'relay':
        p['companion_required'] = True
    p.update(extra)
    # Keep test-sensitive pump/end terminal entries in their original slots.
    index = -1 if level['id'] in ['04', '05'] else len(level['interact'])
    level['interact'].insert(index, p)
    return p


def gate(level, x, key, kind='barrier'):
    level['gates'].append(dict(x=x, y=floor_y(level, x), h=190,
                               key=key, kind=kind))


def cover(level, x, width=280, kind='wall'):
    level['covers'].append(dict(x=x, w=width, kind=kind,
                                y=floor_y(level, x)))


def station(level, x, ident, label, rations=1, scrap=0, medicine=0):
    item(level, 'cache', x-110, label, ident, rations=rations,
         scrap=scrap, medicine=medicine)
    item(level, 'fire', x+70, 'Share a little warmth')
    level['safe_zones'].append(dict(x=x+35, w=400))
    cover(level, x+35, 400, 'tent')
    level['checkpoints'].append(x+35)


def lane(level, x, width, kind, period, active, offset, key=None):
    h = dict(x=x, w=width, kind=kind, period=period,
             active=active, offset=offset)
    if key:
        h['key'] = key
    level['hazard_lanes'].append(h)
    # Both children can fit in shelter before committing to the open lane.
    cover(level, x-150, 300)
    cover(level, x+width+150, 300)


def side_cache(level, x, ident, label, rations=1, medicine=0, scrap=0):
    y = floor_y(level, x)
    level['platforms'] += [dict(x=x-240,y=y-60,w=150,h=22,kind='stone'),
                           dict(x=x-50,y=y-120,w=220,h=22,kind='stone')]
    p = item(level, 'cache', x+50, label, ident, optional=True,
             route='raised_supply_spur', rations=rations,
             medicine=medicine, scrap=scrap)
    p['y'] = y-120


def clue(level, x, text):
    level['tutorials'].append(dict(x=x, text=text))


def memory(level, x, ident, text):
    level['memories'].append(dict(x=x,y=floor_y(level,x)-70,
                                   id=ident,text=text))


def prop(level, kind, x, label=''):
    level['props'].append(dict(kind=kind,x=x,y=floor_y(level,x),label=label))


levels=[]
for index, width in enumerate(WIDTHS, 1):
    l=json.loads((BASE/f'{index:02}.json').read_text(encoding='utf8'))
    old_width=l['width']
    l.update(build='0.3.0',width=width,hazard_lanes=[],zones=[],
             route_length_units=width,original_route_end=old_width)

    if index==1:
        l['objective']='Find the orchard road. Keep him close when the branches begin to move.'
        terrain(l,5200,1500,[[0,0],[100,0],[500,-60],[850,-60],[1200,0],[1500,0]])
        terrain(l,6700,1800,[[0,0],[1800,0]])
        terrain(l,8500,2300,[[0,0],[500,0],[820,-68],[1150,-68],[1480,0],[2300,0]])
        l['zones']=[dict(x=0,w=5200,theme='orchard'),dict(x=5200,w=1500,theme='ridge'),
                    dict(x=6700,w=1800,theme='orchard'),dict(x=8500,w=2300,theme='rain_gully')]
        station(l,6500,'orchard_basket','A basket beneath the hedge',rations=2,scrap=1)
        item(l,'relay',6900,'Lift the crooked orchard bar together','orchard_bar')
        gate(l,7140,'orchard_bar','timber_bar')
        clue(l,6760,'Some things need four hands. Bring him close, then hold E at the bar.')
        lane(l,7560,460,'wind',10.5,2.2,1.0)
        clue(l,7380,'Listen to the branches. Wait in the wall’s lee until the gust passes.')
        side_cache(l,8170,'orchard_terrace','Under the orchard keeper’s coat',medicine=1)
        item(l,'clear',8820,'Move the fallen boughs','orchard_boughs')
        gate(l,9050,'orchard_boughs','fallen_bough')
        station(l,10030,'orchard_shed_food','A flour tin in the empty shed',rations=1,scrap=1)
        item(l,'brace',10200,'Secure the loose shed roof · 1 salvage','orchard_shed_brace',optional=True)
        lane(l,10320,260,'debris',11.0,2.3,4.3,'orchard_shed_brace')
        clue(l,10100,'The roof creaks before it falls. Brace it with salvage, or wait for a quiet moment.')
        memory(l,5800,'orchard_names','Their names were cut in the bark. Smaller letters, a summer ago.')
        memory(l,9700,'empty_swing','The swing moved once. Neither of them had touched it.')
        prop(l,'washing',5530); prop(l,'cart',6840); prop(l,'stump',8730)
        prop(l,'well',9860); prop(l,'sign',10680,'THE WOODS')
        l['checkpoints'] += [7250,8500,10700]

    elif index==2:
        l['objective']='Follow the ridge to the old rail path. Wait for him at every crossing.'
        terrain(l,5500,1500,[[0,0],[150,0],[580,-98],[990,-98],[1370,0],[1500,0]])
        terrain(l,7000,1700,[[0,0],[1700,0]])
        terrain(l,8700,2500,[[0,0],[450,0],[800,54],[1110,54],[1450,0],[2500,0]])
        l['zones']=[dict(x=0,w=5500,theme='ridge'),dict(x=5500,w=1500,theme='ridge'),
                    dict(x=7000,w=1700,theme='rail_yard'),dict(x=8700,w=2500,theme='rain_gully')]
        side_cache(l,6260,'ridge_scarf','A scarf wrapped around a tin',rations=1,scrap=1)
        station(l,7040,'ridge_lunch','The workers’ lunch pail',rations=2,scrap=1)
        item(l,'brace',7330,'Wedge the hanging loading roof · 1 salvage','woods_loading_roof',optional=True)
        lane(l,7540,400,'debris',12.0,2.4,3.8,'woods_loading_roof')
        clue(l,7350,'The loading roof can be made safe. Or watch the dust and time your way through.')
        item(l,'relay',8440,'Raise the rusted rail fence together','rail_fence')
        gate(l,8620,'rail_fence','timber_bar')
        station(l,8900,'woods_keeper_tin','A tin in the keeper’s hut',rations=1,scrap=1,medicine=1)
        lane(l,9750,460,'wind',12.5,2.6,6.0)
        clue(l,9560,'The gully carries every gust. There is room for both of you behind the fallen trunk.')
        item(l,'clear',10500,'Pull the branches out of the culvert','woods_culvert')
        gate(l,10700,'woods_culvert','fallen_bough')
        side_cache(l,10970,'woods_high_sack','The high shelf in a ruined hut',rations=1)
        memory(l,6550,'white_threads','White threads on the thorns. Someone else had come this way.')
        memory(l,9370,'half_map','The paper showed a road. The water had taken the names.')
        prop(l,'stump',6010); prop(l,'cart',7460); prop(l,'barricade',8460)
        prop(l,'washing',9100); prop(l,'sign',11000,'THE CAMP')
        l['checkpoints'] += [6980,8200,9140,10400,11000]

    elif index==3:
        l['objective']='Leave the shelter by the freight yard. Make the roofs safe or cross between the warnings.'
        terrain(l,5700,2100,[[0,0],[250,0],[600,-46],[940,-46],[1280,0],[2100,0]],'stone')
        terrain(l,7800,1800,[[0,0],[1800,0]],'stone')
        terrain(l,9600,2200,[[0,0],[300,0],[650,38],[940,38],[1250,0],[2200,0]])
        l['zones']=[dict(x=0,w=5700,theme='rail_yard'),dict(x=5700,w=2100,theme='rail_yard'),
                    dict(x=7800,w=1800,theme='rain_gully'),dict(x=9600,w=2200,theme='rail_yard')]
        item(l,'clear',5930,'Pull the sacks from the loading door','camp_sacks')
        gate(l,6150,'camp_sacks','sack_wall')
        station(l,7220,'freight_kitchen','The freight kitchen’s last pot',rations=2,scrap=2)
        item(l,'brace',7630,'Shore up the waiting-room beam · 1 salvage','camp_waiting_roof',optional=True)
        lane(l,7970,430,'debris',12.0,2.5,1.0,'camp_waiting_roof')
        clue(l,7710,'The beams give a warning. Keep him under cover while you decide how to cross.')
        item(l,'relay',8760,'Slide the jammed carriage door together','camp_carriage')
        gate(l,8990,'camp_carriage','carriage_door')
        side_cache(l,9230,'freight_first_aid','A first-aid case above the luggage rack',rations=0,medicine=1,scrap=1)
        station(l,9590,'freight_bread','Bread wrapped in a station timetable',rations=2,scrap=1)
        lane(l,10200,520,'sweep',13.0,2.4,5.0)
        clue(l,9990,'The light returns to the same place. Let it pass, then take him with you.')
        item(l,'clear',11200,'Clear the stones from the station passage','camp_station_passage')
        gate(l,11400,'camp_station_passage','rubble')
        memory(l,6470,'chalk_numbers','Numbers on the carriage walls. The children did not ask what they counted.')
        memory(l,9310,'waiting_bench','A folded coat on a bench. It still held the shape of waiting.')
        prop(l,'cart',5880); prop(l,'bench',6820); prop(l,'washing',7350)
        prop(l,'barricade',8630); prop(l,'sign',11620,'SCHOOL ROAD')
        l['checkpoints'] += [7040,7480,8630,9840,10980,11600]

    elif index==4:
        l['objective']='Drain the yard. Find the classrooms beyond it, then the road through the broken library.'
        terrain(l,5500,1800,[[0,0],[1800,0]],'stone')
        terrain(l,7300,2200,[[0,0],[450,0],[800,52],[1150,52],[1500,0],[2200,0]],'stone')
        terrain(l,9500,1900,[[0,0],[320,0],[650,-54],[1010,-54],[1380,0],[1900,0]],'stone')
        l['zones']=[dict(x=0,w=5500,theme='school_courtyard'),dict(x=5500,w=1800,theme='school_courtyard'),
                    dict(x=7300,w=2200,theme='rain_gully'),dict(x=9500,w=1900,theme='school_courtyard')]
        station(l,5780,'school_kitchen_tin','The school kitchen’s biscuit tin',rations=2,scrap=2)
        item(l,'relay',6330,'Lift the fallen classroom shelf together','school_shelf')
        gate(l,6570,'school_shelf','fallen_shelf')
        side_cache(l,6880,'school_sports_cupboard','A blanket in the sports cupboard',rations=1,medicine=1)
        item(l,'brace',7350,'Prop up the library awning · 1 salvage','school_library_awning',optional=True)
        lane(l,7570,420,'debris',11.5,2.1,3.0,'school_library_awning')
        clue(l,7390,'The books are wet. The roof is loose. One piece of salvage makes a dry way through.')
        station(l,9000,'school_staff_flask','A flask and bread in the staff room',rations=2,scrap=1)
        item(l,'clear',9510,'Stack the fallen desks out of the way','school_desks')
        gate(l,9720,'school_desks','fallen_desks')
        lane(l,10420,420,'sweep',12.0,2.0,7.0)
        clue(l,10220,'The wall is long enough for two. Wait for the light to turn away.')
        memory(l,6110,'coathooks','Small coats hung from the hooks. The sleeves waited for hands.')
        memory(l,8810,'small_chair','He straightened a chair. Then another. She waited by the door.')
        memory(l,10000,'lesson_after_rain','On a dry scrap: after the rain, draw what you see.')
        prop(l,'bench',6190); prop(l,'washing',6780); prop(l,'cart',8480)
        prop(l,'bench',9280); prop(l,'sign',11160,'THE FIELDS')
        l['checkpoints'] += [6080,6800,8860,9300,10900,11000]

    elif index==5:
        l['objective']='Stay together. Follow the gardens beyond the ash. There is still a doorway ahead.'
        terrain(l,5700,1700,[[0,0],[180,0],[520,-72],[860,-72],[1240,0],[1700,0]])
        terrain(l,7400,1800,[[0,0],[1800,0]])
        terrain(l,9200,1600,[[0,0],[180,0],[480,-44],[760,-44],[1060,0],[1600,0]])
        l['zones']=[dict(x=0,w=5700,theme='ash_garden'),dict(x=5700,w=1700,theme='ridge'),
                    dict(x=7400,w=1800,theme='ash_garden'),dict(x=9200,w=1600,theme='ash_garden')]
        # The previous ending becomes a rest before the final garden journey.
        l['interact'][-1]['x']=10500
        station(l,5810,'ash_garden_tin','A seed tin with bread beneath it',rations=2,scrap=1)
        item(l,'clear',7230,'Unwind the wire from the garden gate','ash_wire')
        gate(l,7440,'ash_wire','wire_gate')
        lane(l,7780,460,'wind',13.0,2.7,4.0)
        clue(l,7570,'Ash lifts before the wind reaches you. Bring him behind the wall and wait.')
        side_cache(l,8470,'garden_ledge','A parcel beneath a dry flowerpot',rations=1,medicine=1)
        item(l,'relay',8920,'Lift the storm-fallen branch together','ash_branch')
        gate(l,9150,'ash_branch','fallen_bough')
        station(l,9340,'garden_table','A place set for someone who did not return',rations=1,scrap=1)
        item(l,'brace',10100,'Tie the broken garden awning · 1 salvage','ash_awning',optional=True)
        lane(l,10200,200,'debris',12.5,2.0,2.0,'ash_awning')
        clue(l,10060,'The last few steps can still hurt. Secure the awning, or wait beneath the wall.')
        memory(l,6610,'garden_seedlings','There were green things under the ash. He knelt to make sure.')
        memory(l,8670,'two_cups','Two cups on a sill. One much smaller than the other.')
        memory(l,9890,'blue_thread','The ribbon was almost grey. She tied it twice again.')
        prop(l,'stump',6360); prop(l,'well',7580); prop(l,'bench',8500)
        prop(l,'washing',9600); prop(l,'bench',10680)
        # Move the previous finale tutorial to the new final approach.
        for t in l['tutorials']:
            if t['x']==5100:t['x']=10400
        l['checkpoints'] += [7000,7520,8540,9280,10600]

    # Avoid a floating authored prop when a hillside passes beneath it.
    # Legacy positions are deliberately untouched.
    l['checkpoints']=sorted(set(l['checkpoints']))
    assert l['interact'][-1]['kind']=='end' if index==5 else True
    assert l['interact'][-1]['kind']=='pump' if index==4 else True
    assert l['interact'][1]['kind']=='bridge' if index==2 else True
    for g in l['ground']:
        points=g.get('profile',[])
        if points:
            assert points[0]==[0,0] and points[-1]==[g['w'],0]
            for a,b in zip(points,points[1:]):
                assert 0 < b[0]-a[0]
                assert abs(math.degrees(math.atan2(b[1]-a[1],b[0]-a[0])))<=18
    for h in l['hazard_lanes']:
        # Walking pace, plus room for the trailing child, must fit the lull.
        assert (h['w']+150)/166.0 < h['period']-h['active']-1.0
    for checkpoint in l['checkpoints']:
        if checkpoint > old_width:
            assert floor_y(l, checkpoint)==700, ('checkpoint inside shaped ground',checkpoint)
    new_ids=[p['id'] for p in l['interact'] if p.get('id')]
    assert len(new_ids)==len(set(new_ids))
    (P/'levels'/f'{index:02}.json').write_text(json.dumps(l,ensure_ascii=False,indent=2),encoding='utf8')
    levels.append(l)

print(json.dumps(dict(build='0.3.0',route_units=sum(l['width'] for l in levels),
    previous_route_units=sum(l['original_route_end'] for l in levels),
    chapters=[dict(id=l['id'],width=l['width'],new_hazard_lanes=len(l['hazard_lanes']),
                   new_actions=sum(p['kind'] in ['clear','relay','brace'] for p in l['interact']),
                   optional_supply_spurs=sum(p.get('route')=='raised_supply_spur' for p in l['interact']),
                   fires=sum(p['kind']=='fire' for p in l['interact'])) for l in levels]),indent=2))
