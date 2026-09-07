import os
import re

menu_ini = 'original_src/Midas Design+/Language/Korean/Menu.ini'
dlg_files = [
    'original_src/Midas Design+/Language/Korean/DLG_DPLUS_RCS.ini',
    'original_src/Midas Design+/Language/Korean/DLG_DPLUS_Steel.ini',
    'original_src/Midas Design+/Language/Korean/DLG_DPLUS_SRC.ini',
    'original_src/Midas Design+/Language/Korean/DLG_DPLUS_ALU.ini',
    'original_src/Midas Design+/Language/Korean/DLG_DPLUS_RFM.ini',
    'original_src/Midas Design+/Language/Korean/DLG_DPLUS_DGN.ini',
    'original_src/Midas Design+/Language/Korean/DLG_DPLUS_DB.ini',
]

with open(menu_ini, 'r', encoding='utf-16') as f:
    text = f.read()

lines = text.splitlines()
current_sec = ''
menu_items = []

for line in lines:
    line = line.strip()
    if line.startswith('//'):
        current_sec = line[2:].strip()
    elif '=' in line:
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"')
        menu_items.append((current_sec, k, v))

# Find all Member and Design modules
design_members = []
for sec, k, v in menu_items:
    if any(tag in k for tag in ['_MENU_RCS_', '_MENU_STEEL_', '_MENU_SRC_', '_MENU_ALU_', '_MENU_RFM_', '_MENU_PBD_', '_MENU_FES_']):
        design_members.append((sec, k, v))

with open('scanned_midas_catalog.txt', 'w', encoding='utf-8') as out:
    out.write(f'=== Total Design Members Found in Menu.ini: {len(design_members)} ===\n\n')
    for sec, k, v in design_members:
        out.write(f'{sec:35} | {k:35} | {v}\n')

print(f'Successfully wrote {len(design_members)} design members to scanned_midas_catalog.txt')
