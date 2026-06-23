from .contexts import WORKFLOW_CONTEXTS
from .system_templates import SYSTEM_TEMPLATES
from .user_prompts import USER_PROMPTS


def get_prompt_bundle() -> dict[str, dict[str, str]]:
    return {
        "contexts": WORKFLOW_CONTEXTS,
        "system_templates": SYSTEM_TEMPLATES,
        "user_prompts": USER_PROMPTS,
    }
