import os
import glob
import re

menu_ini = 'original_src/Midas Design+/Language/Korean/Menu.ini'

with open(menu_ini, 'r', encoding='utf-16') as f:
    text = f.read()

lines = text.splitlines()
current_sec = ''
all_menus = []

for line in lines:
    line = line.strip()
    if line.startswith('//'):
        current_sec = line[2:].strip()
    elif '=' in line:
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"')
        all_menus.append((current_sec, k, v))

# Categorize into Domains
domains = {
    "RC": [],
    "STEEL": [],
    "SRC": [],
    "ALU": [],
    "RFM": [],
    "FEM_ETC": [],
    "PBD": [],
}

for sec, k, v in all_menus:
    # Filter out pure toolbar/file/general utility buttons
    if any(ignore in k for ignore in ['FILE', 'NEW', 'OPEN', 'SAVE', 'UNDO', 'REDO', 'OPTION', 'TOOL', 'QAT', 'LINK_MIDAS']):
        continue
    
    if 'RCS' in k or 'RC' in sec:
        domains["RC"].append((sec, k, v))
    elif 'STEEL' in k or 'STL' in k or 'STEEL' in sec:
        domains["STEEL"].append((sec, k, v))
    elif 'SRC' in k or 'SRC' in sec:
        domains["SRC"].append((sec, k, v))
    elif 'ALU' in k or 'ALUMINUM' in sec:
        domains["ALU"].append((sec, k, v))
    elif 'RFM' in k or 'REINFORCEMENT' in sec:
        domains["RFM"].append((sec, k, v))
    elif 'PBD' in k or 'PBD' in sec:
        domains["PBD"].append((sec, k, v))
    elif any(tag in k for tag in ['FEM', 'PLATE', 'MESH', 'SOLVER', 'FES']):
        domains["FEM_ETC"].append((sec, k, v))

with open('scanned_all_domains.txt', 'w', encoding='utf-8') as out:
    for dom, items in domains.items():
        out.write(f'=== Domain: {dom} (Count: {len(items)}) ===\n')
        for sec, k, v in items:
            out.write(f'  [{sec}] {k:40} = {v}\n')
        out.write('\n')

print('Scanned all domains successfully.')
