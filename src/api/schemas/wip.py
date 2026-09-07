"""Re-export WIP models for schema compatibility."""
from src.api.models.wip import WIPModuleDetail, WIPResponse, get_wip_module_detail, is_wip_module, MODULE_CATALOG_61

__all__ = [
    "WIPModuleDetail",
    "WIPResponse",
    "get_wip_module_detail",
    "is_wip_module",
    "MODULE_CATALOG_61"
]
