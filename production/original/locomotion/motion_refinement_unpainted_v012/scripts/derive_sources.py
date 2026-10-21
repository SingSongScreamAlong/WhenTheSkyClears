from pathlib import Path
P=Path(__file__).resolve().parents[1];source=P.parent/'motion_rebuild_unpainted_v011'
for folder in ['native','evidence','previews']:(P/folder).mkdir(exist_ok=True)
for name in ['motion_design.py','build_unpainted.py','render_test.py','encode_review.py','validate_motion.py','verify_append.py']:
 text=(source/'scripts'/name).read_text().replace('v011','v012').replace('V011','V012')
 (P/'scripts'/name).write_text(text)
print('V012_ISOLATED_SOURCES_DERIVED')
