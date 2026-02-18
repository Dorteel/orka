"""SWRL rule utilities for ORKA builds.

Rules are read from a text file in ``swrl/`` and instantiated with Owlready2
``Imp.set_as_rule(...)``.
"""

from __future__ import annotations

from pathlib import Path

from owlready2 import Imp

DEFAULT_SWRL_RULES_PATH = Path("swrl/legacy_rules.swrl")


def _parse_swrl_rules_file(rules_path: str | Path) -> list[tuple[str, str]]:
    """Parse SWRL rule definitions from a simple ``Label: Rule`` text file."""
    path = Path(rules_path)
    if not path.exists():
        raise FileNotFoundError(f"SWRL rules file not found: {path}")

    parsed: list[tuple[str, str]] = []
    for line_no, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(
                f"Invalid SWRL rule line at {path}:{line_no} (missing ':')."
            )
        label, rule = line.split(":", 1)
        label = label.strip()
        rule = rule.strip()
        if not label or not rule:
            raise ValueError(
                f"Invalid SWRL rule line at {path}:{line_no} (empty label/rule)."
            )
        parsed.append((label, rule))

    if not parsed:
        raise ValueError(f"No SWRL rules found in: {path}")

    return parsed


def apply_swrl_rules(
    onto,
    rules_path: str | Path = DEFAULT_SWRL_RULES_PATH,
    *,
    update_existing: bool = False,
) -> list[Imp]:
    """Apply SWRL rules to an ontology using Owlready2 ``Imp``.

    Args:
        onto: Target ontology.
        rules_path: Path to SWRL rule text file.
        update_existing: If ``True``, replace rule bodies when a matching
            label already exists. If ``False``, existing labels are left as-is.
    """
    rules = _parse_swrl_rules_file(rules_path)

    existing_by_label: dict[str, Imp] = {}
    for existing in onto.rules():
        label = str(existing.label.first()) if getattr(existing, "label", None) else None
        if label:
            existing_by_label[label] = existing

    applied: list[Imp] = []
    with onto:
        for label, rule_text in rules:
            existing = existing_by_label.get(label)
            if existing is not None:
                if update_existing:
                    existing.set_as_rule(rule_text)
                applied.append(existing)
                continue

            imp = Imp(namespace=onto)
            imp.label = [label]
            imp.set_as_rule(rule_text)
            applied.append(imp)

    return applied
