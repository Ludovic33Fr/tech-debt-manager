#!/usr/bin/env python3
"""
Scan des dependances d'un projet : versions obsoletes, vulnerabilites, libs abandonnees.

Usage:
    python scan_dependencies.py <chemin_du_projet> [--json]

Detecte automatiquement : package.json, requirements.txt, Pipfile, pyproject.toml,
Cargo.toml, go.mod, pom.xml, build.gradle, Gemfile, composer.json
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


# Fichiers de dependances reconnus et leur ecosysteme
DEPENDENCY_FILES = {
    "package.json": "npm",
    "package-lock.json": "npm-lock",
    "yarn.lock": "yarn-lock",
    "pnpm-lock.yaml": "pnpm-lock",
    "requirements.txt": "pip",
    "requirements-dev.txt": "pip",
    "requirements_dev.txt": "pip",
    "Pipfile": "pipenv",
    "Pipfile.lock": "pipenv-lock",
    "pyproject.toml": "python-pyproject",
    "setup.py": "python-setup",
    "setup.cfg": "python-setup",
    "poetry.lock": "poetry-lock",
    "Cargo.toml": "cargo",
    "Cargo.lock": "cargo-lock",
    "go.mod": "go",
    "go.sum": "go-sum",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle-kts",
    "Gemfile": "bundler",
    "Gemfile.lock": "bundler-lock",
    "composer.json": "composer",
    "composer.lock": "composer-lock",
    "pubspec.yaml": "dart",
    "mix.exs": "elixir",
    "project.clj": "leiningen",
}

IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "env",
    "dist", "build", ".next", "target", "vendor",
}


def find_dependency_files(root_path):
    """Trouve tous les fichiers de dependances dans le projet."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            if filename in DEPENDENCY_FILES:
                filepath = os.path.join(dirpath, filename)
                found.append({
                    "file": os.path.relpath(filepath, root_path),
                    "absolute_path": filepath,
                    "ecosystem": DEPENDENCY_FILES[filename],
                    "filename": filename,
                })
    return found


def parse_package_json(filepath):
    """Parse un package.json et extrait les dependances."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    deps = []

    for dep_type in ["dependencies", "devDependencies", "peerDependencies", "optionalDependencies"]:
        if dep_type in data:
            for name, version in data[dep_type].items():
                deps.append({
                    "name": name,
                    "version_spec": version,
                    "type": dep_type,
                    "ecosystem": "npm",
                })

    # Detecter les engines
    if "engines" in data:
        for engine, version in data["engines"].items():
            deps.append({
                "name": f"engine:{engine}",
                "version_spec": version,
                "type": "engines",
                "ecosystem": "npm",
            })

    return deps


def parse_requirements_txt(filepath):
    """Parse un requirements.txt."""
    deps = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("-"):
                    continue
                # Patterns: package==1.0, package>=1.0, package~=1.0, package
                match = re.match(r"^([a-zA-Z0-9_.-]+)\s*([>=<~!]+\s*[\d.]+(?:\s*,\s*[>=<~!]+\s*[\d.]+)*)?", line)
                if match:
                    deps.append({
                        "name": match.group(1),
                        "version_spec": match.group(2).strip() if match.group(2) else "unpinned",
                        "type": "dependencies",
                        "ecosystem": "pip",
                    })
    except OSError:
        pass
    return deps


def parse_pyproject_toml(filepath):
    """Parse un pyproject.toml (basique, sans lib toml)."""
    deps = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return deps

    # Extraction basique des dependances
    in_deps = False
    in_dev_deps = False

    for line in content.split("\n"):
        stripped = line.strip()
        if stripped in ("[project.dependencies]", "[tool.poetry.dependencies]"):
            in_deps = True
            in_dev_deps = False
            continue
        elif stripped in ("[project.optional-dependencies]", "[tool.poetry.dev-dependencies]", "[tool.poetry.group.dev.dependencies]"):
            in_deps = False
            in_dev_deps = True
            continue
        elif stripped.startswith("["):
            in_deps = False
            in_dev_deps = False
            continue

        if in_deps or in_dev_deps:
            # Format poetry: name = "^1.0" ou name = {version = "^1.0"}
            match = re.match(r'^([a-zA-Z0-9_.-]+)\s*=\s*["\']([^"\']+)["\']', stripped)
            if match:
                deps.append({
                    "name": match.group(1),
                    "version_spec": match.group(2),
                    "type": "devDependencies" if in_dev_deps else "dependencies",
                    "ecosystem": "python",
                })
            # Format PEP 621: "name>=1.0"
            match2 = re.match(r'^["\']([a-zA-Z0-9_.-]+)\s*([>=<~!]+[\d.]+)?["\']', stripped)
            if match2:
                deps.append({
                    "name": match2.group(1),
                    "version_spec": match2.group(2) or "unpinned",
                    "type": "devDependencies" if in_dev_deps else "dependencies",
                    "ecosystem": "python",
                })

    return deps


def parse_go_mod(filepath):
    """Parse un go.mod."""
    deps = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return deps

    in_require = False
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("require ("):
            in_require = True
            continue
        elif stripped == ")":
            in_require = False
            continue

        if in_require or stripped.startswith("require "):
            match = re.match(r"(?:require\s+)?([^\s]+)\s+(v[\d.]+(?:-[^\s]+)?)", stripped)
            if match:
                deps.append({
                    "name": match.group(1),
                    "version_spec": match.group(2),
                    "type": "dependencies",
                    "ecosystem": "go",
                })

    return deps


def parse_cargo_toml(filepath):
    """Parse un Cargo.toml (basique)."""
    deps = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return deps

    in_deps = False
    in_dev_deps = False

    for line in content.split("\n"):
        stripped = line.strip()
        if stripped == "[dependencies]":
            in_deps = True
            in_dev_deps = False
            continue
        elif stripped == "[dev-dependencies]":
            in_deps = False
            in_dev_deps = True
            continue
        elif stripped.startswith("["):
            in_deps = False
            in_dev_deps = False
            continue

        if in_deps or in_dev_deps:
            match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*["\']([^"\']+)["\']', stripped)
            if match:
                deps.append({
                    "name": match.group(1),
                    "version_spec": match.group(2),
                    "type": "devDependencies" if in_dev_deps else "dependencies",
                    "ecosystem": "cargo",
                })

    return deps


def parse_dependency_file(dep_file):
    """Parse un fichier de dependances selon son type."""
    filepath = dep_file["absolute_path"]
    ecosystem = dep_file["ecosystem"]

    parsers = {
        "npm": parse_package_json,
        "pip": parse_requirements_txt,
        "python-pyproject": parse_pyproject_toml,
        "go": parse_go_mod,
        "cargo": parse_cargo_toml,
    }

    parser = parsers.get(ecosystem)
    if parser:
        return parser(filepath)

    # Pour les ecosystemes sans parser, retourner une info basique
    return [{"name": f"<{ecosystem} deps>", "version_spec": "non parse", "type": "dependencies", "ecosystem": ecosystem}]


def analyze_dependency_health(deps):
    """Analyse la sante des dependances (heuristiques locales sans appel reseau)."""
    findings = []

    for dep in deps:
        issues = []

        # Detecter les versions non pinees
        if dep["version_spec"] in ("*", "latest", "unpinned", ""):
            issues.append({
                "type": "unpinned",
                "severity": "high",
                "detail": "Version non pinee — risque de breaking changes inattendus",
            })

        # Detecter les ranges trop larges (npm)
        if dep["ecosystem"] == "npm":
            spec = dep["version_spec"]
            if spec.startswith(">=") or spec == "*":
                issues.append({
                    "type": "wide_range",
                    "severity": "moderate",
                    "detail": f"Range trop large : {spec}",
                })

        # Detecter les prefixes de version potentiellement dangereux
        spec = dep["version_spec"]
        if spec.startswith("^0.") or spec.startswith("~0."):
            issues.append({
                "type": "pre_v1",
                "severity": "moderate",
                "detail": "Dependance pre-v1 — API potentiellement instable",
            })

        # Detecter les URLs git directes
        if "git" in spec or "github" in spec:
            issues.append({
                "type": "git_dependency",
                "severity": "moderate",
                "detail": "Dependance pointant vers un repo git — pas de version semantique",
            })

        # Detecter les chemins locaux
        if spec.startswith("file:") or spec.startswith("./") or spec.startswith("../"):
            issues.append({
                "type": "local_path",
                "severity": "low",
                "detail": "Dependance locale — non portable",
            })

        if issues:
            findings.append({
                "dependency": dep["name"],
                "version_spec": dep["version_spec"],
                "type": dep["type"],
                "ecosystem": dep["ecosystem"],
                "issues": issues,
            })

    return findings


def check_lock_files(dep_files):
    """Verifie la presence de lock files."""
    ecosystems = set(df["ecosystem"] for df in dep_files)
    findings = []

    lock_mapping = {
        "npm": ["npm-lock", "yarn-lock", "pnpm-lock"],
        "pip": ["pipenv-lock", "poetry-lock"],
        "pipenv": ["pipenv-lock"],
        "python-pyproject": ["poetry-lock"],
        "cargo": ["cargo-lock"],
        "go": ["go-sum"],
        "bundler": ["bundler-lock"],
        "composer": ["composer-lock"],
    }

    for ecosystem in ecosystems:
        if ecosystem in lock_mapping:
            expected_locks = lock_mapping[ecosystem]
            has_lock = any(df["ecosystem"] in expected_locks for df in dep_files)
            if not has_lock:
                findings.append({
                    "type": "missing_lock_file",
                    "severity": "high",
                    "ecosystem": ecosystem,
                    "detail": f"Pas de lock file pour l'ecosysteme {ecosystem} — builds non reproductibles",
                })

    return findings


def scan_project(root_path):
    """Scan complet des dependances du projet."""
    root_path = os.path.abspath(root_path)
    dep_files = find_dependency_files(root_path)

    if not dep_files:
        return {
            "project_root": root_path,
            "warning": "Aucun fichier de dependances trouve",
            "dependency_files": [],
            "dependencies": [],
            "findings": [],
        }

    all_deps = []
    for df in dep_files:
        deps = parse_dependency_file(df)
        for dep in deps:
            dep["source_file"] = df["file"]
        all_deps.extend(deps)

    # Analyser la sante
    dep_findings = analyze_dependency_health(all_deps)
    lock_findings = check_lock_files(dep_files)

    # Resume
    ecosystems = set(df["ecosystem"] for df in dep_files)

    summary = {
        "project_root": root_path,
        "ecosystems": list(ecosystems),
        "dependency_files_count": len(dep_files),
        "total_dependencies": len(all_deps),
        "production_deps": len([d for d in all_deps if d["type"] == "dependencies"]),
        "dev_deps": len([d for d in all_deps if d["type"] == "devDependencies"]),
        "findings_count": len(dep_findings) + len(lock_findings),
        "high_severity": len([f for f in dep_findings if any(i["severity"] == "high" for i in f["issues"])]) + len([f for f in lock_findings if f["severity"] == "high"]),
    }

    return {
        "summary": summary,
        "dependency_files": dep_files,
        "dependencies": all_deps,
        "dependency_findings": dep_findings,
        "lock_file_findings": lock_findings,
        "recommendations": generate_recommendations(dep_findings, lock_findings, all_deps),
    }


def generate_recommendations(dep_findings, lock_findings, all_deps):
    """Genere des recommandations basees sur les findings."""
    recs = []

    if lock_findings:
        recs.append({
            "priority": "high",
            "action": "Ajouter les lock files manquants pour garantir des builds reproductibles",
            "detail": [f["detail"] for f in lock_findings],
        })

    unpinned = [f for f in dep_findings if any(i["type"] == "unpinned" for i in f["issues"])]
    if unpinned:
        recs.append({
            "priority": "high",
            "action": f"Piner les {len(unpinned)} dependances non pinees",
            "detail": [f["dependency"] for f in unpinned],
        })

    pre_v1 = [f for f in dep_findings if any(i["type"] == "pre_v1" for i in f["issues"])]
    if pre_v1:
        recs.append({
            "priority": "moderate",
            "action": f"Evaluer les {len(pre_v1)} dependances pre-v1 pour des alternatives stables",
            "detail": [f["dependency"] for f in pre_v1],
        })

    git_deps = [f for f in dep_findings if any(i["type"] == "git_dependency" for i in f["issues"])]
    if git_deps:
        recs.append({
            "priority": "moderate",
            "action": f"Remplacer les {len(git_deps)} dependances git par des versions publiees",
            "detail": [f["dependency"] for f in git_deps],
        })

    # Recommandation d'audit de securite
    ecosystems = set(d["ecosystem"] for d in all_deps)
    audit_commands = []
    if "npm" in ecosystems:
        audit_commands.append("npm audit")
    if "pip" in ecosystems:
        audit_commands.append("pip-audit (pip install pip-audit)")
    if "cargo" in ecosystems:
        audit_commands.append("cargo audit")
    if "go" in ecosystems:
        audit_commands.append("govulncheck ./...")

    if audit_commands:
        recs.append({
            "priority": "high",
            "action": "Lancer un audit de securite avec les outils natifs",
            "detail": audit_commands,
        })

    return recs


def main():
    parser = argparse.ArgumentParser(description="Scan des dependances d'un projet")
    parser.add_argument("path", help="Chemin vers le projet a scanner")
    parser.add_argument("--json", action="store_true", help="Sortie en JSON")

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Erreur: {args.path} n'est pas un repertoire valide", file=sys.stderr)
        sys.exit(1)

    result = scan_project(args.path)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        s = result["summary"]
        print(f"\n{'='*60}")
        print(f"  SCAN DES DEPENDANCES : {s['project_root']}")
        print(f"{'='*60}\n")
        print(f"  Ecosystemes         : {', '.join(s['ecosystems'])}")
        print(f"  Fichiers de deps    : {s['dependency_files_count']}")
        print(f"  Dependances totales : {s['total_dependencies']}")
        print(f"    Production        : {s['production_deps']}")
        print(f"    Dev               : {s['dev_deps']}")
        print(f"  Problemes detectes  : {s['findings_count']}")
        print(f"    Haute severite    : {s['high_severity']}")

        if result.get("dependency_findings"):
            print(f"\n{'='*60}")
            print(f"  PROBLEMES DETECTES")
            print(f"{'='*60}\n")
            for finding in result["dependency_findings"]:
                for issue in finding["issues"]:
                    print(f"  [{issue['severity'].upper()}] {finding['dependency']}")
                    print(f"    {issue['detail']}")
                    print()

        if result.get("lock_file_findings"):
            for finding in result["lock_file_findings"]:
                print(f"  [{finding['severity'].upper()}] {finding['detail']}")
                print()

        if result.get("recommendations"):
            print(f"\n{'='*60}")
            print(f"  RECOMMANDATIONS")
            print(f"{'='*60}\n")
            for rec in result["recommendations"]:
                print(f"  [{rec['priority'].upper()}] {rec['action']}")
                if isinstance(rec["detail"], list):
                    for d in rec["detail"][:5]:
                        print(f"    - {d}")
                    if len(rec["detail"]) > 5:
                        print(f"    ... et {len(rec['detail']) - 5} autres")
                print()


if __name__ == "__main__":
    main()
