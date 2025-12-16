# Simple knowledge module
# Re-export from parent module
import sys
import os

# Import from the .py file (not this folder)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Manually load the file
import importlib.util
spec = importlib.util.spec_from_file_location("simple_knowledge_file", 
    os.path.join(parent_dir, "simple_knowledge.py"))
if spec and spec.loader:
    _module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_module)
    augment_prompt_with_facts = _module.augment_prompt_with_facts
    get_relevant_facts = _module.get_relevant_facts
else:
    # Fallback - define empty function
    def augment_prompt_with_facts(question, base_prompt):
        return base_prompt
    def get_relevant_facts(question, max_facts=3):
        return []
    SIMPLE_FACTS = {}
