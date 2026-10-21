from pathlib import Path
O=Path(__file__).resolve().parents[1];A=O.parent/'first_danger_rough_v068'
t=(A/'scripts/package_review.py').read_text()
t=t.replace("records=json.loads((O/'evidence/MOVIE_BATCHES_E.json').read_text())", "tag=Path(B['native']).stem.split('_')[-1]\nrecords=json.loads((O/f'evidence/MOVIE_BATCHES_{tag}.json').read_text())")
t=t.replace("R/'work/first_danger_acting_v067/previews/WTSC_First_Danger_Acting_v067_Unmasked_24fps.mp4'", "R/'work/first_danger_rough_v068/previews/WTSC_First_Danger_Rough_v068e_24fps.mp4'")
t=t.replace("R/'work/first_danger_acting_v067/previews/WTSC_First_Danger_Acting_v067_Title_24fps.mp4'", "R/'work/first_danger_rough_v068/previews/WTSC_First_Danger_Rough_v068e_Title_24fps.mp4'")
t=t.replace('v068e','v069').replace('BEFORE | v067','BEFORE | v068 rough').replace('BEFORE v067','BEFORE v068')
# The prior replacement must not rewrite the before source filenames.
t=t.replace("R/'work/first_danger_rough_v068/previews/WTSC_First_Danger_Rough_v069_24fps.mp4'", "R/'work/first_danger_rough_v068/previews/WTSC_First_Danger_Rough_v068e_24fps.mp4'")
t=t.replace("R/'work/first_danger_rough_v068/previews/WTSC_First_Danger_Rough_v069_Title_24fps.mp4'", "R/'work/first_danger_rough_v068/previews/WTSC_First_Danger_Rough_v068e_Title_24fps.mp4'")
t=t.replace("renders/movie_E/", "renders/movie_{tag}/")
t=t.replace('AFTER | v068 ROUGH ACTING DRAWINGS','AFTER | v069 PAINTED DEVELOPMENT').replace('AFTER | v068 ROUGH DRAWINGS','AFTER | v069 DEVELOPMENT').replace('AFTER v068 ROUGH','AFTER v069 DEVELOPMENT')
t=t.replace('V068_REVIEW_READY','V069_REVIEW_READY').replace('DELIVERY_E.json','DELIVERY.json')
t=t.replace('84 drawn exposures per child on twos.','168 native drawing exposures per child, one per production frame.')
t=t.replace('New drawings intentionally show rough construction/ink-wash color rather than final painted cleanup.','Painted head-angle studies and retained original pigments on developed contours. Likeness and animation remain provisional pending review.')
(O/'scripts/package_review.py').write_text(t)
print('V069_PACKAGE_PIPELINE_READY')
