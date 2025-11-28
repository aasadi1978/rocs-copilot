from collections import defaultdict
import logging
from typing import Dict, List
from langgraph.prebuilt import ToolNode, tools_condition


class Tools():
    """Singleton class to manage registered tools."""
    _instance = None
    __tools: Dict = defaultdict(List[ToolNode])

    def __new__(cls):
        
        if cls._instance is None:
            cls._instance = super(Tools, cls).__new__(cls)
            cls._instance.__tools = defaultdict(List[ToolNode])
        return cls._instance

    def __init__(self):
        pass

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance
    
    @property
    def tools(self) -> Dict[str, List[ToolNode]]:
        """A dictionary of registered tools categorized by type. E.g., 'universal', 'rag', 'outlook', etc."""
        return self.__tools

    def register_tool(self, tool, category: str = "universal"):
        try:
            existing_tools: List[ToolNode] = self.__tools.setdefault(category, [])
            for t in existing_tools:
                if t.__name__ == tool.__name__:
                    return
            
            existing_tools.append(tool)
            self.__tools[category] = existing_tools
            logging.info(f"Registered tool: {tool.__name__} under category: {category}")

        except Exception:
            logging.warning("Tool has no name attribute during registration check.")
    
    def register_tools(self, tools: list, category: str = "universal"):
        for tool in tools:
            self.register_tool(tool, category=category)

TOOLS = Tools.get_instance()