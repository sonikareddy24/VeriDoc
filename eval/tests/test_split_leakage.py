"""Split leakage test: ensures no entity or layout overlap between seen and unseen splits."""

from eval.generator.generate_dataset import generate_dataset
import json
from pathlib import Path


def test_no_split_leakage(tmp_path):
    manifest_path = Path("data/sample/manifest.json")
    if not manifest_path.exists():
        generate_dataset(profile="quick")

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    seen_entities = set()
    unseen_entities = set()
    seen_layouts = set()
    unseen_layouts = set()

    for doc in manifest:
        split = doc["split"]
        entity = doc["entity_id"]
        layout = doc["layout_id"]

        if split == "seen":
            seen_entities.add(entity)
            seen_layouts.add(layout)
        elif split == "unseen":
            unseen_entities.add(entity)
            unseen_layouts.add(layout)

    # 1. Zero entity leakage
    entity_intersection = seen_entities.intersection(unseen_entities)
    assert len(entity_intersection) == 0, f"Entity leakage detected: {entity_intersection}"

    # 2. Zero layout leakage: seen must be {1, 2}, unseen must be {3, 4}
    layout_intersection = seen_layouts.intersection(unseen_layouts)
    assert len(layout_intersection) == 0, f"Layout leakage detected: {layout_intersection}"
    assert seen_layouts.issubset({1, 2})
    assert unseen_layouts.issubset({3, 4})
