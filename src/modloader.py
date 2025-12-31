import json
from operator import mod
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
    download_files: List[str]  # Files to be placed in Downloads/{mod_id}
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
        self._load_manifest()

    # Loads mod manifest from file
    def _load_manifest(self) -> None:
        # Starting variables
        self.cache_dir = self.game_path / "mod_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.manifest_path = self.cache_dir / "manifest.json"
        self.duplicate_ids_found = False
        self.mods: Dict[str, Mod] = {}

        # Prepare file if it doesn't exist
        if not self.manifest_path.exists():
            self.manifest_path.write_text(json.dumps({"mods": []}, indent=4))
            return

        with self.manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Parse mods from manifest
        self.duplicate_ids_found = False
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

            # Edge case: Duplicate mod IDs
            if mod.id in self.mods:
                print(f"[WARNING] Duplicate mod ID in manifest: {mod.id}. Overwriting previous entry.")
                self.duplicate_ids_found = True
            self.mods[mod.id] = mod
        print(f"Loaded {len(self.mods)} mods from manifest")

    # Validates the mod installation for conflicts
    def validate_installation(self) -> bool:
        # Validate: No duplicate IDs
        if self.duplicate_ids_found:
            print("[ERROR] Duplicate mod IDs found.")
            return False
        
        # Validate: No conflicting overrides
        overridden_files = set()
        for mod in self.mods.values():
            for _, target_rel in mod.override_files:
                if target_rel in overridden_files:
                    print(f"[ERROR] Conflict detected: {target_rel} is overridden by multiple mods.")
                    return False
                overridden_files.add(target_rel)
        return True

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
            print(f"[CUSTOM FILE] copy {src} -> {dest}")
            # shutil.copy2(src, dest)

        # Copy override files to their target locations relative to game root
        for src_rel, dest_rel in mod.override_files:
            src = self.cache_dir / src_rel
            dest = self.game_path / dest_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            print(f"[OVERRIDE FILE] copy {src} -> {dest}")
            # shutil.copy2(src, dest)

    # Installs all mods in the manifest
    def install_all(self) -> None:
        for mod_id in self.mods:
            self.install_mod(mod_id)

    # Adds a new mod to the manifest and copies files to cache
    def add_mod(
        self,
        mod_id: str,
        name: str,
        description: Optional[str],
        image: Optional[str],
        download_files: List[Tuple[str, str]],  # List of (source_path, filename)
        override_files: List[Tuple[str, str, str]],  # List of (source_path, filename, target_rel)
    ) -> None:
        # Validate mod ID doesn't already exist
        if mod_id in self.mods:
            raise ValueError(f"Mod with ID '{mod_id}' already exists")

        # Create mod directory in cache
        mod_cache_dir = self.cache_dir / mod_id
        mod_cache_dir.mkdir(parents=True, exist_ok=True)

        # Copy download files and build relative paths
        download_rel_paths: List[str] = []
        for src_path, filename in download_files:
            dest = mod_cache_dir / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest)
            # Store relative path from cache_dir: {mod_id}/{filename}
            download_rel_paths.append(f"{mod_id}/{filename}")

        # Copy override files and build override entries
        override_entries: List[Tuple[str, str]] = []
        for src_path, filename, target_rel in override_files:
            dest = mod_cache_dir / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest)
            # Store relative path from cache_dir and target
            source_rel = f"{mod_id}/{filename}"
            override_entries.append((source_rel, target_rel))

        # Create Mod instance
        mod = Mod(
            id=mod_id,
            name=name,
            description=description,
            image=image,
            download_files=download_rel_paths,
            override_files=override_entries,
        )
        self.mods[mod_id] = mod

        # Update manifest.json
        self._save_manifest()
        print(f"Added mod: {mod_id}")

    # Removes a mod from the manifest and deletes its cached files
    def remove_mod(self, mod_id: str) -> None:
        if mod_id not in self.mods:
            raise KeyError(f"Mod not found: {mod_id}")

        # Remove mod directory from cache
        mod_cache_dir = self.cache_dir / mod_id
        if mod_cache_dir.exists():
            shutil.rmtree(mod_cache_dir)

        # Remove from mods dict
        del self.mods[mod_id]

        # Update manifest.json
        self._save_manifest()
        print(f"Removed mod: {mod_id}")

    # Saves the current mods to manifest.json
    def _save_manifest(self) -> None:
        mods_data = []
        for mod in self.mods.values():
            mod_entry = {
                "id": mod.id,
                "name": mod.name,
                "description": mod.description,
                "image": mod.image,
                "downloads": mod.download_files,
                "overrides": [
                    {"source": src, "target": dst}
                    for src, dst in mod.override_files
                ],
            }
            mods_data.append(mod_entry)

        with self.manifest_path.open("w", encoding="utf-8") as f:
            json.dump({"mods": mods_data}, f, indent=2)


