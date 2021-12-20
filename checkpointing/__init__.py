from pathlib import Path

save_path = Path(".cache", "checkpoints")

if not save_path.exists():
    save_path.mkdir(parents=True)
