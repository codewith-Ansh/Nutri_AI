from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Dict, Any, Optional
from app.services.tool_router import tool_router
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def verify_tools_access(x_tools_key: Optional[str] = Header(None)):
    """Verify access to tools API"""
    # Allow in DEBUG mode or with correct key
    if settings.DEBUG:
        return True
    
    tools_key = getattr(settings, 'TOOLS_API_KEY', None)
    if tools_key and x_tools_key == tools_key:
        return True
    
    raise HTTPException(
        status_code=403,
        detail="Tools API access denied. Requires X-TOOLS-KEY header or DEBUG mode."
    )

@router.post("/run")
async def run_tool(
    request: Dict[str, Any],
    _: bool = Depends(verify_tools_access)
):
    """
    Execute a tool for debugging purposes
    
    Body:
    {
        "tool_name": "openfoodfacts.fetch_product_by_barcode",
        "args": {"barcode": "1234567890"}
    }
    """
    try:
        tool_name = request.get("tool_name")
        args = request.get("args", {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="tool_name is required")
        
        result = await tool_router.run_tool(tool_name, args)
        
        logger.info(f"Debug tool execution: {tool_name} -> {result['ok']}")
        return result
        
    except Exception as e:
        logger.error(f"Tools API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available")
async def get_available_tools(_: bool = Depends(verify_tools_access)):
    """Get list of available tools"""
    return {
        "tools": tool_router.get_available_tools(),
        "debug_mode": settings.DEBUG
    }