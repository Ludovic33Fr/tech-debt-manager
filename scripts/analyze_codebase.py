#!/usr/bin/env python3
"""
Analyse statique d'un codebase : complexite cyclomatique, duplication, LOC,
profondeur d'imbrication, densite de TODO/FIXME.

Usage:
    python analyze_codebase.py <chemin_du_projet> [--json] [--lang python|javascript|typescript|java|go]

Sortie: JSON avec metriques par fichier et metriques globales.
"""

import argparse
import ast
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Extensions supportees par langage
LANG_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".jsx", ".mjs", ".cjs"],
    "typescript": [".ts", ".tsx", ".mts", ".cts"],
    "java": [".java"],
    "go": [".go"],
    "rust": [".rs"],
    "ruby": [".rb"],
    "csharp": [".cs"],
    "cpp": [".cpp", ".cc", ".cxx", ".h", ".hpp"],
    "php": [".php"],
}

ALL_EXTENSIONS = set()
for exts in LANG_EXTENSIONS.values():
    ALL_EXTENSIONS.update(exts)

# Patterns a ignorer
IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "env",
    "dist", "build", ".next", ".nuxt", "target", "bin", "obj",
    ".tox", ".mypy_cache", ".pytest_cache", "vendor", "packages",
    ".cargo", "coverage", ".nyc_output", ".turbo",
}

DEBT_MARKERS = re.compile(r"\b(TODO|FIXME|HACK|XXX|WORKAROUND|KLUDGE|TEMP|DEPRECATED)\b", re.IGNORECASE)

# Patterns de decision pour la complexite cyclomatique (heuristique regex)
DECISION_PATTERNS = {
    "python": re.compile(r"^\s*(if |elif |for |while |except |with |and |or |\band\b|\bor\b)", re.MULTILINE),
    "javascript": re.compile(r"\b(if|else if|for|while|do|catch|case|\?\?|&&|\|\||\?)\b"),
    "typescript": re.compile(r"\b(if|else if|for|while|do|catch|case|\?\?|&&|\|\||\?)\b"),
    "java": re.compile(r"\b(if|else if|for|while|do|catch|case|&&|\|\||\?)\b"),
    "go": re.compile(r"\b(if|else if|for|select|case|&&|\|\|)\b"),
    "rust": re.compile(r"\b(if|else if|for|while|loop|match|=>|&&|\|\||\?)\b"),
    "default": re.compile(r"\b(if|else if|elif|for|while|do|catch|except|case|&&|\|\|)\b"),
}


def detect_language(filepath):
    """Detecte le langage a partir de l'extension du fichier."""
    ext = Path(filepath).suffix.lower()
    for lang, exts in LANG_EXTENSIONS.items():
        if ext in exts:
            return lang
    return "unknown"


def should_ignore(path):
    """Verifie si un chemin doit etre ignore."""
    parts = Path(path).parts
    return any(part in IGNORE_DIRS for part in parts)


def collect_source_files(root_path, lang_filter=None):
    """Collecte tous les fichiers source du projet."""
    files = []
    root = Path(root_path)

    if lang_filter and lang_filter in LANG_EXTENSIONS:
        valid_exts = set(LANG_EXTENSIONS[lang_filter])
    else:
        valid_exts = ALL_EXTENSIONS

    for dirpath, dirnames, filenames in os.walk(root):
        # Filtrer les repertoires a ignorer
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if Path(filename).suffix.lower() in valid_exts and not should_ignore(filepath):
                files.append(filepath)

    return files


def count_lines(content):
    """Compte les lignes de code, commentaires, et vides."""
    lines = content.split("\n")
    total = len(lines)
    blank = sum(1 for l in lines if not l.strip())
    # Heuristique simple pour les commentaires
    comment = sum(1 for l in lines if l.strip().startswith(("#", "//", "*", "/*", "---")))
    code = total - blank - comment
    return {"total": total, "code": code, "blank": blank, "comment": comment}


def calculate_cyclomatic_complexity_python(content):
    """Calcule la CC pour Python via l'AST."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return _cc_heuristic(content, "python")

    functions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cc = 1
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                    cc += 1
                elif isinstance(child, ast.BoolOp):
                    cc += len(child.values) - 1
                elif isinstance(child, ast.comprehension):
                    cc += 1 + len(child.ifs)
            functions.append({
                "name": node.name,
                "line": node.lineno,
                "complexity": cc,
                "lines": (node.end_lineno or node.lineno) - node.lineno + 1,
                "args": len(node.args.args),
            })

    return functions


def _cc_heuristic(content, lang):
    """Calcule la CC par heuristique regex (pour les langages sans parser AST)."""
    pattern = DECISION_PATTERNS.get(lang, DECISION_PATTERNS["default"])

    # Decouper par fonctions si possible
    # Heuristique simple : compter les decisions globales
    lines = content.split("\n")
    decisions = sum(1 for line in lines if pattern.search(line))
    cc = 1 + decisions

    return [{"name": "<module>", "line": 1, "complexity": cc, "lines": len(lines), "args": 0}]


def calculate_cyclomatic_complexity(content, lang):
    """Calcule la complexite cyclomatique selon le langage."""
    if lang == "python":
        return calculate_cyclomatic_complexity_python(content)
    return _cc_heuristic(content, lang)


def calculate_nesting_depth(content):
    """Calcule la profondeur maximale d'imbrication."""
    max_depth = 0
    for line in content.split("\n"):
        if not line.strip():
            continue
        # Compter les niveaux d'indentation
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        # Estimer la profondeur (4 espaces ou 1 tab = 1 niveau)
        depth = indent // 4 if "\t" not in line else line.count("\t")
        # Ajuster pour les accolades
        depth += line.count("{") - line.count("}")
        max_depth = max(max_depth, depth)
    return max_depth


def detect_duplication(files_content, block_size=6):
    """Detecte la duplication de code par hashing de blocs."""
    block_hashes = defaultdict(list)
    total_blocks = 0

    for filepath, content in files_content.items():
        lines = [l.strip() for l in content.split("\n") if l.strip() and not l.strip().startswith(("#", "//", "*", "/*"))]

        for i in range(len(lines) - block_size + 1):
            block = "\n".join(lines[i:i + block_size])
            block_hash = hashlib.md5(block.encode()).hexdigest()
            block_hashes[block_hash].append({"file": filepath, "line": i + 1})
            total_blocks += 1

    duplicates = []
    duplicate_blocks = 0
    for h, locations in block_hashes.items():
        if len(locations) > 1:
            duplicate_blocks += len(locations) - 1
            duplicates.append({
                "occurrences": len(locations),
                "locations": locations[:5],  # Limiter pour la sortie
            })

    duplication_ratio = (duplicate_blocks / total_blocks * 100) if total_blocks > 0 else 0

    return {
        "ratio_percent": round(duplication_ratio, 2),
        "duplicate_blocks": duplicate_blocks,
        "total_blocks": total_blocks,
        "top_duplicates": sorted(duplicates, key=lambda x: x["occurrences"], reverse=True)[:10],
    }


def count_debt_markers(content, filepath):
    """Compte les marqueurs de dette (TODO, FIXME, etc.)."""
    markers = []
    for i, line in enumerate(content.split("\n"), 1):
        for match in DEBT_MARKERS.finditer(line):
            markers.append({
                "type": match.group(1).upper(),
                "file": filepath,
                "line": i,
                "text": line.strip()[:120],
            })
    return markers


def detect_long_parameter_lists(content, lang):
    """Detecte les fonctions avec trop de parametres."""
    findings = []

    if lang == "python":
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Exclure self/cls
                    args = [a.arg for a in node.args.args if a.arg not in ("self", "cls")]
                    if len(args) > 5:
                        findings.append({
                            "name": node.name,
                            "line": node.lineno,
                            "param_count": len(args),
                        })
        except SyntaxError:
            pass
    else:
        # Heuristique regex pour les autres langages
        func_pattern = re.compile(r"(?:function|def|func|fn)\s+(\w+)\s*\(([^)]*)\)")
        for i, line in enumerate(content.split("\n"), 1):
            m = func_pattern.search(line)
            if m:
                params = [p.strip() for p in m.group(2).split(",") if p.strip()]
                if len(params) > 5:
                    findings.append({
                        "name": m.group(1),
                        "line": i,
                        "param_count": len(params),
                    })

    return findings


def analyze_file(filepath, root_path):
    """Analyse un fichier individuel."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (OSError, IOError):
        return None

    lang = detect_language(filepath)
    rel_path = os.path.relpath(filepath, root_path)
    line_counts = count_lines(content)

    # Complexite cyclomatique
    cc_results = calculate_cyclomatic_complexity(content, lang)
    max_cc = max((f["complexity"] for f in cc_results), default=0)
    avg_cc = sum(f["complexity"] for f in cc_results) / len(cc_results) if cc_results else 0

    # Fonctions longues
    long_functions = [f for f in cc_results if f.get("lines", 0) > 50]

    # Profondeur d'imbrication
    max_nesting = calculate_nesting_depth(content)

    # Marqueurs de dette
    markers = count_debt_markers(content, rel_path)

    # Parametres excessifs
    long_params = detect_long_parameter_lists(content, lang)

    # Determiner le niveau de severite du fichier
    issues = []
    if line_counts["code"] > 500:
        issues.append({"type": "file_too_long", "severity": "high" if line_counts["code"] > 1000 else "moderate", "detail": f"{line_counts['code']} LOC"})
    if max_cc > 20:
        issues.append({"type": "high_complexity", "severity": "critical", "detail": f"CC max = {max_cc}"})
    elif max_cc > 10:
        issues.append({"type": "moderate_complexity", "severity": "moderate", "detail": f"CC max = {max_cc}"})
    if max_nesting > 4:
        issues.append({"type": "deep_nesting", "severity": "high" if max_nesting > 6 else "moderate", "detail": f"Profondeur max = {max_nesting}"})
    if long_functions:
        issues.append({"type": "long_functions", "severity": "moderate", "detail": f"{len(long_functions)} fonctions > 50 lignes"})
    if long_params:
        issues.append({"type": "excessive_params", "severity": "moderate", "detail": f"{len(long_params)} fonctions avec > 5 params"})
    if len(markers) > 5:
        issues.append({"type": "debt_markers", "severity": "low", "detail": f"{len(markers)} marqueurs TODO/FIXME"})

    return {
        "file": rel_path,
        "language": lang,
        "lines": line_counts,
        "complexity": {
            "max": max_cc,
            "average": round(avg_cc, 2),
            "functions": cc_results[:20],  # Limiter la sortie
        },
        "max_nesting_depth": max_nesting,
        "long_functions": long_functions,
        "long_parameter_lists": long_params,
        "debt_markers": markers,
        "issues": issues,
    }


def analyze_project(root_path, lang_filter=None):
    """Analyse complete du projet."""
    root_path = os.path.abspath(root_path)
    files = collect_source_files(root_path, lang_filter)

    if not files:
        return {"error": f"Aucun fichier source trouve dans {root_path}"}

    # Analyser chaque fichier
    file_results = []
    files_content = {}
    total_loc = 0
    all_markers = []
    all_issues = []
    cc_values = []

    for filepath in files:
        result = analyze_file(filepath, root_path)
        if result:
            file_results.append(result)
            total_loc += result["lines"]["code"]
            all_markers.extend(result["debt_markers"])
            all_issues.extend([(result["file"], issue) for issue in result["issues"]])
            cc_values.append(result["complexity"]["max"])

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    files_content[os.path.relpath(filepath, root_path)] = f.read()
            except (OSError, IOError):
                pass

    # Duplication
    duplication = detect_duplication(files_content)

    # Compter les fichiers de tests
    test_patterns = re.compile(r"(test_|_test\.|\.test\.|\.spec\.|Test\.|Spec\.|_spec\.)")
    test_files = [f for f in files if test_patterns.search(os.path.basename(f))]
    src_files = [f for f in files if not test_patterns.search(os.path.basename(f))]
    test_ratio = len(test_files) / len(src_files) if src_files else 0

    # Marqueurs par type
    marker_counts = Counter(m["type"] for m in all_markers)

    # Severite des issues
    severity_counts = Counter()
    for _, issue in all_issues:
        severity_counts[issue["severity"]] += 1

    # Trier les fichiers par nombre d'issues (les plus problematiques en premier)
    file_results.sort(key=lambda x: len(x["issues"]), reverse=True)

    # Resume
    summary = {
        "project_root": root_path,
        "total_files": len(files),
        "source_files": len(src_files),
        "test_files": len(test_files),
        "test_ratio": round(test_ratio, 2),
        "total_loc": total_loc,
        "avg_file_size": round(total_loc / len(files), 1) if files else 0,
        "avg_cyclomatic_complexity": round(sum(cc_values) / len(cc_values), 2) if cc_values else 0,
        "max_cyclomatic_complexity": max(cc_values, default=0),
        "duplication": duplication,
        "debt_markers": {
            "total": len(all_markers),
            "per_kloc": round(len(all_markers) / (total_loc / 1000), 2) if total_loc > 0 else 0,
            "by_type": dict(marker_counts),
        },
        "issues": {
            "total": len(all_issues),
            "by_severity": dict(severity_counts),
        },
        "languages": dict(Counter(detect_language(f) for f in files)),
    }

    return {
        "summary": summary,
        "files": file_results[:50],  # Top 50 fichiers les plus problematiques
        "all_debt_markers": all_markers[:100],  # Top 100 marqueurs
    }


def main():
    parser = argparse.ArgumentParser(description="Analyse statique d'un codebase")
    parser.add_argument("path", help="Chemin vers le projet a analyser")
    parser.add_argument("--json", action="store_true", help="Sortie en JSON")
    parser.add_argument("--lang", choices=list(LANG_EXTENSIONS.keys()), help="Filtrer par langage")
    parser.add_argument("--top", type=int, default=20, help="Nombre de fichiers a afficher (defaut: 20)")

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Erreur: {args.path} n'est pas un repertoire valide", file=sys.stderr)
        sys.exit(1)

    result = analyze_project(args.path, args.lang)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        # Affichage textuel
        s = result["summary"]
        print(f"\n{'='*60}")
        print(f"  ANALYSE DU CODEBASE : {s['project_root']}")
        print(f"{'='*60}\n")
        print(f"  Fichiers source     : {s['source_files']}")
        print(f"  Fichiers de tests   : {s['test_files']} (ratio: {s['test_ratio']:.2f})")
        print(f"  Total LOC           : {s['total_loc']:,}")
        print(f"  Taille moyenne      : {s['avg_file_size']:.0f} LOC/fichier")
        print(f"  Langages            : {s['languages']}")
        print(f"\n  CC moyenne          : {s['avg_cyclomatic_complexity']:.1f}")
        print(f"  CC max              : {s['max_cyclomatic_complexity']}")
        print(f"  Duplication         : {s['duplication']['ratio_percent']:.1f}%")
        print(f"  Marqueurs de dette  : {s['debt_markers']['total']} ({s['debt_markers']['per_kloc']:.1f}/KLOC)")
        print(f"  Issues detectees    : {s['issues']['total']}")
        print(f"    Critiques         : {s['issues']['by_severity'].get('critical', 0)}")
        print(f"    Elevees           : {s['issues']['by_severity'].get('high', 0)}")
        print(f"    Moderees          : {s['issues']['by_severity'].get('moderate', 0)}")
        print(f"    Faibles           : {s['issues']['by_severity'].get('low', 0)}")

        print(f"\n{'='*60}")
        print(f"  TOP {args.top} FICHIERS LES PLUS PROBLEMATIQUES")
        print(f"{'='*60}\n")

        for f in result["files"][:args.top]:
            if f["issues"]:
                print(f"  {f['file']}")
                print(f"    LOC: {f['lines']['code']} | CC max: {f['complexity']['max']} | Nesting: {f['max_nesting_depth']}")
                for issue in f["issues"]:
                    print(f"    [{issue['severity'].upper()}] {issue['type']}: {issue['detail']}")
                print()


if __name__ == "__main__":
    main()
