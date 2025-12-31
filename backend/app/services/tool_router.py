import logging
from typing import Dict, Any, Callable
from app.tools.openfoodfacts_tool import openfoodfacts_tool
from app.tools.ingredient_kb_tool import ingredient_kb_tool

logger = logging.getLogger(__name__)

class ToolRouter:
    def __init__(self):
        self.tools: Dict[str, Callable] = {
            "openfoodfacts.fetch_product_by_barcode": openfoodfacts_tool.fetch_product_by_barcode,
            "ingredient_kb.lookup_ingredient": ingredient_kb_tool.lookup_ingredient,
            "ingredient_kb.bulk_lookup": ingredient_kb_tool.bulk_lookup,
        }
    
    async def run_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given arguments
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments to pass to the tool
            
        Returns:
            Structured result with ok, tool, data, error fields
        """
        try:
            if tool_name not in self.tools:
                return {
                    "ok": False,
                    "tool": tool_name,
                    "data": None,
                    "error": f"Tool '{tool_name}' not found"
                }
            
            tool_func = self.tools[tool_name]
            
            # Execute tool (handle both sync and async)
            if hasattr(tool_func, '__call__'):
                if tool_name.startswith("openfoodfacts"):
                    # OpenFoodFacts tools are async
                    result = await tool_func(**args)
                else:
                    # KB tools are sync
                    result = tool_func(**args)
            else:
                raise ValueError(f"Tool '{tool_name}' is not callable")
            
            logger.info(f"Tool '{tool_name}' executed successfully")
            return {
                "ok": True,
                "tool": tool_name,
                "data": result,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Tool '{tool_name}' execution failed: {str(e)}")
            return {
                "ok": False,
                "tool": tool_name,
                "data": None,
                "error": str(e)
            }
    
    def get_available_tools(self) -> Dict[str, str]:
        """Get list of available tools with descriptions"""
        return {
            "openfoodfacts.fetch_product_by_barcode": "Fetch product data from OpenFoodFacts by barcode",
            "ingredient_kb.lookup_ingredient": "Lookup single ingredient in knowledge base",
            "ingredient_kb.bulk_lookup": "Lookup multiple ingredients in knowledge base"
        }

# Singleton instance
tool_router = ToolRouter()