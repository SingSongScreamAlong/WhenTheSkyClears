"""Use the authorized fallback: original foreground, only restrained background art."""
from pathlib import Path
R=Path(__file__).resolve().parents[1];text=(R/'scripts/build_art_study_v045a.py').read_text().replace('v045a','v045c')
start=text.index('# Selectively quiet the repeated large lower path plants');end=text.index('# Verify ALL protected scene/performance/FX bytes',start)
text=text[:start]+"# Foreground suppression failed three frame tests. Original v044 road/bank retained exactly; component unfinished.\n"+text[end:]
text=text.replace("protected=set([root,", "protected=set([s.objects['v020 | Walking path | continuous blended paint'],s.objects['v020 | Foreground bank | continuous blended paint'],root,")
anchor="for image in (R/'renders/world_v016/art_v045').glob('Art_v045_*_4K.png'):preserved[str(image)]=hashlib.sha256(image.read_bytes()).hexdigest()"
extra=anchor+"\nfor version,sha in [('v045a','7dc52ab80047ab3b7d7ae3f8ca61414b4763a04ecf6784b23afb34219b2630fa'),('v045b','b1de051977efd68c7871de638df55f9dd7505dc1c04bdc8124a79ee6ba430f64')]:\n failed_copy=R/f'shots/world/WTSC_Open_Battlefield_Art_Study_{version}.blend';assert hashlib.sha256(failed_copy.read_bytes()).hexdigest()==sha;preserved[str(failed_copy)]=sha\n for image in (R/f'renders/world_v016/art_{version}').glob('*4K.png'):preserved[str(image)]=hashlib.sha256(image.read_bytes()).hexdigest()"
assert anchor in text;text=text.replace(anchor,extra)
text=text.replace("'protected_definition':'All new-pair geometry", "'foreground_status':'Originalv044material/geometry/alpha retained exactly. Repeatedplantclusters remain an unfinishedartcomponent; v045/v045a/v045b failedsamples preserved.','protected_definition':'Originalroadandbank geometry/material/actions plus all new-pair geometry")
text=text.replace("'rejected_predecessor':'v045actualsource/PNGs retained: UVstrip sampling failed visualreview; broadgrade over-fogged. This separatev045c uses uniform-density underpaint and restrained world-fixed corridor grade.'", "'rejected_predecessor':'v045 UVstrip comb; v045a bright soil band; v045b dark blocky patches. Sources/actualframes retained. Authorized fallback c retains originalforeground exactly; only restrained45a-style backgroundgrade remains.'")
out=R/'scripts/build_art_study_v045c.py';assert not out.exists();compile(text,str(out),'exec');out.write_text(text)
renderer=R/'scripts/render_art_frames_v045c.py';assert not renderer.exists();renderer.write_text((R/'scripts/render_art_frames_v045b.py').read_text().replace('v045b','v045c'))
compare=R/'scripts/compare_art_frames_v045c.py';assert not compare.exists();compare.write_text((R/'scripts/compare_art_frames_v045b.py').read_text().replace('v045b','v045c'));print('V045C_FOREGROUND_FALLBACK_RECIPES_WRITTEN')
