"""autopop: Auto Populate GDoc tables using LLMs."""

__version__ = '2.3'

from .aspect_factory import AspectFactory, DDBPromptWrapper, dynamic_init, get_instances
from .google_util_wrapper import GoogleUtilWrapper, call_post_sheet
from .ddb_util_wrapper import DDBUtilWrapper
from .knowledge_base import knowledge_base

__all__ = [
    'AspectFactory',
    'DDBPromptWrapper',
    'GoogleUtilWrapper',
    'DDBUtilWrapper',
    'KnowledgeBase',
    'call_post_sheet',
    'dynamic_init', 
    'get_instances'
]
