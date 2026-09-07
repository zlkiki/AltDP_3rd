# app/engines/__init__.py
"""Auto-Discovery Registry for 54 Member Design Modules."""
import importlib
import os
import pkgutil
from typing import Dict, Any, Optional
from pydantic import BaseModel

REGISTRY: Dict[str, Any] = {}
MODULE_LIST: list = []


def auto_discover_modules():
    """Scans subdirectories in engines/ and registers modules having MODULE_INFO and calculate."""
    global REGISTRY, MODULE_LIST
    REGISTRY.clear()
    MODULE_LIST.clear()
    
    current_dir = os.path.dirname(__file__)
    
    # Categories: rc, steel, pc, misc
    for category in ["rc", "steel", "pc", "misc"]:
        cat_dir = os.path.join(current_dir, category)
        if not os.path.isdir(cat_dir):
            continue
            
        for root, dirs, files in os.walk(cat_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    rel_path = os.path.relpath(os.path.join(root, file), current_dir)
                    # Convert to module path: rc.beam.base
                    mod_parts = rel_path[:-3].replace(os.sep, ".")
                    full_mod_name = f"app.engines.{mod_parts}"
                    
                    try:
                        mod = importlib.import_module(full_mod_name)
                        if hasattr(mod, "MODULE_INFO") and hasattr(mod, "calculate"):
                            info = getattr(mod, "MODULE_INFO")
                            cat = info.get("category", category)
                            grp = info.get("group", "")
                            mod_id = info.get("submodule", file[:-3])
                            
                            key = f"{cat}/{grp}/{mod_id}"
                            
                            # Find InputSchema if exists (or any BaseModel subclass)
                            schema_cls = None
                            for attr_name in dir(mod):
                                attr = getattr(mod, attr_name)
                                if isinstance(attr, type) and issubclass(attr, BaseModel) and attr is not BaseModel:
                                    schema_cls = attr
                                    break
                                    
                            schema_json = {}
                            if schema_cls:
                                if hasattr(schema_cls, "model_json_schema"):
                                    schema_json = schema_cls.model_json_schema()
                                elif hasattr(schema_cls, "schema"):
                                    schema_json = schema_cls.schema()
                                    
                            module_entry = {
                                "key": key,
                                "category": cat,
                                "group": grp,
                                "id": mod_id,
                                "info": info,
                                "schema_cls": schema_cls,
                                "schema_json": schema_json,
                                "calculate": getattr(mod, "calculate")
                            }
                            
                            REGISTRY[key] = module_entry
                            MODULE_LIST.append({
                                "key": key,
                                "category": cat,
                                "group": grp,
                                "id": mod_id,
                                "name": info.get("name", mod_id),
                                "geomType": info.get("geomType", "rc_rect"),
                                "description": info.get("description", "")
                            })
                    except Exception as e:
                        print(f"[Auto-Discovery] Failed to load module {full_mod_name}: {e}")


def get_module(category: str, group: str, module_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves registered module entry by category/group/id."""
    key = f"{category}/{group}/{module_id}"
    if key in REGISTRY:
        return REGISTRY[key]
        
    # Check by primary ID or aliases
    for reg_key, mod in REGISTRY.items():
        if mod.get("id") == module_id or reg_key.endswith(f"/{module_id}"):
            return mod

    # Fallback to 61-module catalog if unintegrated or WIP
    from src.api.models.wip import get_wip_module_detail
    detail = get_wip_module_detail(category, group, module_id)
    if detail:
        return {
            "key": detail.key,
            "category": detail.category,
            "group": detail.group,
            "id": module_id,
            "info": {
                "name": detail.name,
                "category": detail.category,
                "group": detail.group,
                "submodule": module_id,
                "midas_dlg": detail.midas_dlg,
                "tier": detail.tier,
                "standard": detail.standard,
                "engine_status": detail.engine_status,
                "notice": detail.notice
            },
            "schema_cls": None,
            "schema_json": {
                "title": detail.name,
                "type": "object",
                "properties": {},
                "description": f"[{detail.tier}] {detail.name} ({detail.standard}) - {detail.engine_status}"
            },
            "calculate": None
        }

    return None


def get_all_modules_meta() -> list:
    """Returns metadata of all 61 original app member modules with 3-tier classifications."""
    from src.api.models.wip import MODULE_CATALOG_61
    
    full_catalog_list = []
    for mod_id, meta in MODULE_CATALOG_61.items():
        entry = {
            "key": meta["key"],
            "category": meta["category"],
            "group": meta["group"],
            "id": meta.get("id", mod_id),
            "name": meta["name"],
            "midas_dlg": meta["midas_dlg"],
            "tier": meta["tier"],
            "standard": meta["standard"],
            "engine_status": meta["engine_status"],
            "domain": meta.get("domain", "RC"),
            "geomType": meta.get("geomType", "rc_rect"),
            "description": meta.get("description", f"{meta['name']} ({meta['standard']})"),
            "aliases": meta.get("aliases", [])
        }
        full_catalog_list.append(entry)
    return full_catalog_list


# Initial scan on module import
auto_discover_modules()

