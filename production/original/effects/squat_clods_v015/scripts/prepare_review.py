from pathlib import Path
P=Path(__file__).resolve().parents[1];old=P.parent/'connected_wedge_v014/scripts'
mapping={
 'FXv014 | connected wedge TWO TONE ROUGH':'FXv015 | squat clods SILHOUETTE ROUGH',
 'WTSC_Connected_Soil_Wedge_TWO_TONE_ROUGH_v014':'WTSC_Squat_Clods_SILHOUETTE_ROUGH_v015',
 'WTSC_Connected_Wedge_ROUGH_Keys_v014':'WTSC_Squat_Clods_ROUGH_Keys_v015',
 'WTSC_Connected_Wedge_ROUGH_Shot_Size_v014':'WTSC_Squat_Clods_ROUGH_Shot_Size_v015',
 'CONNECTED_ROUGH_RENDER_DONE':'SQUAT_CLODS_RENDER_DONE'
}
for name in ['render_rough.py','key_sequence.py','finish_preview.py','record_library_xattrs.py']:
    t=(old/name).read_text()
    for a,b in mapping.items():t=t.replace(a,b)
    t=t.replace("'connected_frames':[7,14],'first_separation_frames':[15,16]", "'fixed_size_primary_clods':True,'first_rising_gaps_scene_frame':10")
    t=t.replace('One requested two-tone rough for review before any polish.', 'One requested fixed-size squat-clod silhouette rough for review before polish.')
    (P/'scripts'/name).write_text(t)
(P/'ROUGH_NOTES.txt').write_text('SQUAT CLODS v015 — SILHOUETTE ROUGH ONLY\nSame held shot camera. 1920x1080, 24fps, frames1–32 (1.333 seconds), impact7.\nTwo explicit squat lobed contours have constant area from the start. They emerge\nfrom behind the bank at full bulk and travel upward/outward; size does not inflate.\nShallow matching-tone attached root lobes initially overlap them and track their\nrelease. Irregular gaps open while clods are still rising; root flow recedes before\nclod apex. No monolithic face or clean section cut. One flat tone per primary mass\nand matching base lobe; no faceted light-front/dark-side plate surfaces.\nTwo primary fragments only. No smoke, pigment, contour rounding, opacity remedy,\npuffs, contact polish or pack work. Rough landings use the flat impact-bank level.\nJudge material/silhouette progression and timing before any finish. Actual key\nframes are inspected; continuous playback was not observed. File decode is not\nan artistic normal-speed pass. No acceptance or production integration.\nAll new files under effects/squat_clods_v015; v014 remains unchanged.\n')
print('SQUAT_REVIEW_SCRIPTS_PREPARED')
