import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from settings import Settings

# Data class representing a mod
@dataclass
class Mod:
	id: str
	name: str
	description: Optional[str]
	image: Optional[str]
	download_files: List[str] # Files to be placed in Downloads/{mod_id}
	override_files: List[Tuple[str, str]]  # Override files (source_rel, target_rel)

# ModLoader class to manage mods
class ModLoader:
	def __init__(self, settings: Optional[Settings] = None):
        # Validate and set up paths
		self.settings = settings or Settings()
		game_path_str = self.settings.get_game_path()
		if not game_path_str:
			raise ValueError("Game path is not configured")

		self.game_path = Path(game_path_str)
		if not self.game_path.exists():
			raise FileNotFoundError(f"Game path does not exist: {self.game_path}")

        # Load mod manifest
		self.cache_dir = self.game_path / "mod_cache"
		self.cache_dir.mkdir(parents=True, exist_ok=True)

		self.manifest_path = self.cache_dir / "manifest.json"
		self.mods: Dict[str, Mod] = {}
		self._load_manifest()

    # Loads mod manifest from file
	def _load_manifest(self) -> None:
		# Prepare file if it doesn't exist
		if not self.manifest_path.exists():
			self.manifest_path.write_text(json.dumps({"mods": []}, indent=4))
			return

		with self.manifest_path.open("r", encoding="utf-8") as f:
			data = json.load(f)

        # Parse mods from manifest
		for mod_data in data.get("mods", []):
			overrides_raw = mod_data.get("overrides", [])
			overrides: List[Tuple[str, str]] = []
			for item in overrides_raw:
				src = item.get("source")
				dst = item.get("target")
				if not src or not dst:
					continue
				overrides.append((src, dst))

            # Assign mod data to Mod instance
			mod = Mod(
				id=mod_data["id"],
				name=mod_data.get("name", mod_data["id"]),
				description=mod_data.get("description"),
				image=mod_data.get("image"),
				download_files=mod_data.get("downloads", []),
				override_files=overrides,
			)
			self.mods[mod.id] = mod

    # Installs a mod by its ID
	def install_mod(self, mod_id: str) -> None:
		# Validate mod existence
		if mod_id not in self.mods:
			raise KeyError(f"Mod not found: {mod_id}")

        # Install the mod
		mod = self.mods[mod_id]
		downloads_dir = self.game_path / "Downloads" / mod.id
		downloads_dir.mkdir(parents=True, exist_ok=True)

		# Copy files into Downloads/{mod_id}, preserving relative structure
		for rel_path in mod.download_files:
			src = self.cache_dir / rel_path
			dest = downloads_dir / Path(rel_path)
			dest.parent.mkdir(parents=True, exist_ok=True)
			print(f"[DOWNLOAD] Would copy {src} -> {dest}")
			# shutil.copy2(src, dest)

		# Copy override files to their target locations relative to game root
		for src_rel, dest_rel in mod.override_files:
			src = self.cache_dir / src_rel
			dest = self.game_path / dest_rel
			dest.parent.mkdir(parents=True, exist_ok=True)
			print(f"[OVERRIDE] Would copy {src} -> {dest}")
			# shutil.copy2(src, dest)

    # Installs all mods in the manifest
	def install_all(self) -> None:
		for mod_id in self.mods:
			self.install_mod(mod_id)


