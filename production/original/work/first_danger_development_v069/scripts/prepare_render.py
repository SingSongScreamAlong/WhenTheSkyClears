from pathlib import Path
O=Path(__file__).resolve().parents[1];A=O.parent/'first_danger_rough_v068'
t=(A/'scripts/render_review.py').read_text().replace('V068','V069')
t=t.replace("base=O/'renders'/('keys_E' if mode=='keys' else mode+'_E')","tag=N.stem.split('_')[-1]\nbase=O/'renders'/(mode+'_'+tag)")
t=t.replace("O/f'evidence/RENDER_{mode}_E_{frames[0]}_{frames[-1]}.json'","O/f'evidence/RENDER_{mode}_{tag}_{frames[0]}_{frames[-1]}.json'")
t=t.replace("B['hidden_original_objects']","B.get('hidden_original_objects',[])")
t=t.replace("assert len(visible)==2","assert len(visible)==2\n heads=[o for o in W.objects if o.name in B['head_objects'] and not o.hide_render];assert len(heads)==2")
(O/'scripts/render_review.py').write_text(t)
t=(A/'scripts/render_batches.py').read_text().replace('V068','V069')
t=t.replace("jobs=[", "B=json.loads((O/'evidence/BUILD.json').read_text());tag=Path(B['native']).stem.split('_')[-1]\njobs=[")
t=t.replace('render_movie_E_','render_movie_{tag}_').replace('RENDER_movie_E_','RENDER_movie_{tag}_')
t=t.replace('max_workers=3','max_workers=2').replace("O/'evidence/MOVIE_BATCHES_E.json'","O/f'evidence/MOVIE_BATCHES_{tag}.json'")
(O/'scripts/render_batches.py').write_text(t)
print('V069_RENDER_PIPELINE_READY')
