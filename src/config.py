import os
from pathlib import Path
from dotenv import load_dotenv

#Define the root of the project
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

#Load env vars from .env file
load_dotenv(PROJECT_ROOT / '.env')

GEMINI_API_KEY: str =  os.getenv("GEMINI_API_KEY")

def resolve_path(env_var: str, default_val: str) ->Path:
    """ Resolve the config path to absolute paths relative to project root

    Args:
        env_var: The name of the env var to resolve 
        default_val: The default value to use if the env var is not set
    """
    val = os.getenv(env_var, default_val)
    path: Path = Path(val)
    if not path.is_absolute():
        path = (PROJECT_ROOT/path).resolve()
    return path

OBSIDIAN_VAULT_PATH: Path = resolve_path("OBSIDIAN_VAULT_PATH", "obsidian_vault") 
PROCESSED_DIR: Path = resolve_path("PROCESSED_DIR", "processed")
INPUT_DIR: Path = resolve_path("INPUT_DIR", "input")

def ensure_directories() -> None:
    """Ensure all directories exist, creating them if necessary"""
    for path in [OBSIDIAN_VAULT_PATH, PROCESSED_DIR, INPUT_DIR]:
        path.mkdir(parents=True, exist_ok=True)

ensure_directories()