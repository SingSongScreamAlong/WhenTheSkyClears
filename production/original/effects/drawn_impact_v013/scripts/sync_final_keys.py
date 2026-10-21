from pathlib import Path
import shutil
P=Path(__file__).resolve().parents[1]
for fr in list(range(6,16))+[18,22,26,30,36,72]:
    source=P/f'previews/painted_motion/{fr:04d}.png';assert source.read_bytes()[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82';shutil.copyfile(source,P/f'previews/painted_keys/{fr:04d}.png')
print('FINAL_KEYS_COPIED_FROM_ACTUAL_MOTION')
