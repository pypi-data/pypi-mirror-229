"""autopop: Auto Populate GDoc tables using LLMs."""

__version__ = '2.6'

from .aspect_factory import AspectFactory
from .aspect_factory import dynamic_init, get_instances
from .ddb_util_wrapper import DDBUtilWrapper
from .google_util_wrapper import GoogleUtilWrapper
from .google_util_wrapper import call_post_sheet, get_bsme_interview
from .google_util_wrapper import get_tsme_interview, get_related_docs
from .knowledge_base import knowledge_base

__all__ = [
    'AspectFactory',
    'GoogleUtilWrapper',
    'DDBUtilWrapper',
    'knowledge_base',
    'call_post_sheet',
    'get_bsme_interview',
    'get_tsme_interview',
    'get_related_docs',
    'dynamic_init', 
    'get_instances'
]