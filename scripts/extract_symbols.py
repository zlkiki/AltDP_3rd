import os
import struct
import ctypes
import json

dbghelp = ctypes.windll.dbghelp
UnDecorateSymbolName = dbghelp.UnDecorateSymbolName
UnDecorateSymbolName.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint]
UnDecorateSymbolName.restype = ctypes.c_uint

def demangle(mangled: str) -> str:
    buf = ctypes.create_string_buffer(4096)
    res = UnDecorateSymbolName(mangled.encode('latin1'), buf, 4096, 0)
    if res:
        return buf.value.decode('latin1', errors='ignore')
    return mangled

def get_all_exports(path: str):
    with open(path, 'rb') as f:
        data = f.read()
    if len(data) < 0x40:
        return []
    if data[:2] != b'MZ':
        return []
    e_lfanew = struct.unpack('<I', data[0x3C:0x40])[0]
    if e_lfanew + 24 > len(data):
        return []
    if data[e_lfanew:e_lfanew+4] != b'PE\x00\x00':
        return []
    
    num_sections = struct.unpack('<H', data[e_lfanew+6:e_lfanew+8])[0]
    opt_magic = struct.unpack('<H', data[e_lfanew+24:e_lfanew+26])[0]
    is_64 = (opt_magic == 0x20b)
    opt_size = struct.unpack('<H', data[e_lfanew+20:e_lfanew+22])[0]
    sec_header_start = e_lfanew + 24 + opt_size
    
    dd_start = e_lfanew + 24 + (112 if is_64 else 96)
    export_rva, export_size = struct.unpack('<II', data[dd_start:dd_start+8])
    if export_rva == 0:
        return []
    
    for i in range(num_sections):
        s_offset = sec_header_start + i * 40
        v_size, v_addr, r_size, r_offset = struct.unpack('<IIII', data[s_offset+8:s_offset+24])
        if v_addr <= export_rva < v_addr + max(v_size, r_size):
            exp_file_offset = r_offset + (export_rva - v_addr)
            if exp_file_offset + 40 > len(data):
                return []
            num_funcs, num_names = struct.unpack('<II', data[exp_file_offset+20:exp_file_offset+28])
            addr_names_rva = struct.unpack('<I', data[exp_file_offset+32:exp_file_offset+36])[0]
            names_offset = r_offset + (addr_names_rva - v_addr)
            exports = []
            for n_idx in range(num_names):
                name_rva = struct.unpack('<I', data[names_offset + n_idx*4 : names_offset + (n_idx+1)*4])[0]
                name_file_offset = r_offset + (name_rva - v_addr)
                end_pos = data.find(b'\x00', name_file_offset)
                if end_pos != -1:
                    exports.append(data[name_file_offset:end_pos].decode('latin1', errors='ignore'))
            return exports
    return []

def main():
    base_dir = r'f:\PyProject\re-DP\original_src\Midas Design+'
    out_dir = r'f:\PyProject\re-DP\decompiled_src'
    os.makedirs(out_dir, exist_ok=True)

    inventory = {}
    total_syms = 0

    target_dlls = [
        'DPLUS_DB.dll', 'DPLUS_RCS.dll', 'DPLUS_STEEL.dll', 'DPLUS_SRC.dll',
        'DPLUS_ALU.dll', 'DPLUS_EC.dll', 'DPLUS_IS.dll', 'DPLUS_Main.dll',
        'DPLUS_DGN.dll', 'DPLUS_Draw.dll', 'DPLUS_DWG.dll', 'DPLUS_RFM.dll',
        'DPLUS_VDraw.dll', 'IDGN_core.dll', 'IDGN_db.dll', 'IDGN_lib.dll',
        'MIDAS_base.dll', 'MIDAS_lib.dll', 'MIDAS_util.dll', 'DGN_lib.dll'
    ]

    for dll in target_dlls:
        p = os.path.join(base_dir, dll)
        if os.path.exists(p):
            exps = get_all_exports(p)
            total_syms += len(exps)
            sym_list = []
            classes_map = {}
            for e in exps:
                dem = demangle(e)
                sym_list.append((e, dem))
                if '::' in dem:
                    cls_part = dem.split('::')[0].split()[-1]
                    if cls_part.startswith('C') and len(cls_part) > 2:
                        if cls_part not in classes_map:
                            classes_map[cls_part] = []
                        classes_map[cls_part].append(dem)
                        
            txt_path = os.path.join(out_dir, f'{dll}_symbols.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                for mangled, demangled in sym_list:
                    f.write(f'{mangled} -> {demangled}\n')
                    
            inventory[dll] = {
                'total_exports': len(exps),
                'unique_classes': len(classes_map),
                'top_classes': sorted(list(classes_map.keys()))[:30]
            }
            print(f'Processed {dll:20} : {len(exps):5} symbols, {len(classes_map):3} classes -> {txt_path}')

    json_path = os.path.join(out_dir, 'dll_inventory.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)

    print(f'\nTotal extracted symbols: {total_syms}')

if __name__ == '__main__':
    main()
