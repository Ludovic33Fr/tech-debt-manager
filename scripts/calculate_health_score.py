#!/usr/bin/env python3
"""
Calcul du Health Score d'un projet a partir des metriques d'analyse.

Usage:
    python calculate_health_score.py <metrics.json> [--weights code=25,arch=20,tests=20,deps=15,docs=10,infra=10]
    python calculate_health_score.py --from-analysis <chemin_projet>

Sortie: Health Score (0-100) avec breakdown par categorie.
"""

import argparse
import json
import os
import sys


DEFAULT_WEIGHTS = {
    "code": 0.25,
    "architecture": 0.20,
    "tests": 0.20,
    "dependencies": 0.15,
    "documentation": 0.10,
    "infrastructure": 0.10,
}


def normalize_metric(value, good, bad):
    """Normalise une metrique sur 0-100 (100 = bon)."""
    if good == bad:
        return 50
    # Si good < bad (ex: complexite : bon=5, mauvais=30)
    if good < bad:
        if value <= good:
            return 100
        elif value >= bad:
            return 0
        else:
            return round(100 * (bad - value) / (bad - good))
    else:
        # Si good > bad (ex: couverture : bon=80%, mauvais=20%)
        if value >= good:
            return 100
        elif value <= bad:
            return 0
        else:
            return round(100 * (value - bad) / (good - bad))


def score_code(metrics):
    """Calcule le score de la categorie Code (0-100)."""
    scores = []

    # Complexite cyclomatique moyenne
    if "avg_cyclomatic_complexity" in metrics:
        scores.append(normalize_metric(metrics["avg_cyclomatic_complexity"], good=5, bad=25))

    # Complexite cyclomatique max
    if "max_cyclomatic_complexity" in metrics:
        scores.append(normalize_metric(metrics["max_cyclomatic_complexity"], good=10, bad=50))

    # Duplication
    if "duplication_ratio" in metrics:
        scores.append(normalize_metric(metrics["duplication_ratio"], good=3, bad=20))

    # Taille moyenne des fichiers
    if "avg_file_size" in metrics:
        scores.append(normalize_metric(metrics["avg_file_size"], good=150, bad=800))

    # Densite de marqueurs de dette
    if "debt_markers_per_kloc" in metrics:
        scores.append(normalize_metric(metrics["debt_markers_per_kloc"], good=2, bad=15))

    # Nombre d'issues critiques/elevees
    if "critical_issues" in metrics:
        scores.append(normalize_metric(metrics["critical_issues"], good=0, bad=10))

    if "high_issues" in metrics:
        scores.append(normalize_metric(metrics["high_issues"], good=0, bad=20))

    return round(sum(scores) / len(scores)) if scores else 50


def score_architecture(metrics):
    """Calcule le score de la categorie Architecture (0-100)."""
    scores = []

    if "circular_dependencies" in metrics:
        scores.append(normalize_metric(metrics["circular_dependencies"], good=0, bad=5))

    if "god_modules" in metrics:
        scores.append(normalize_metric(metrics["god_modules"], good=0, bad=3))

    if "layering_violations" in metrics:
        scores.append(normalize_metric(metrics["layering_violations"], good=0, bad=10))

    if "max_coupling" in metrics:
        scores.append(normalize_metric(metrics["max_coupling"], good=5, bad=30))

    return round(sum(scores) / len(scores)) if scores else 50


def score_tests(metrics):
    """Calcule le score de la categorie Tests (0-100)."""
    scores = []

    if "test_ratio" in metrics:
        scores.append(normalize_metric(metrics["test_ratio"], good=0.8, bad=0.1))

    if "test_coverage" in metrics:
        scores.append(normalize_metric(metrics["test_coverage"], good=80, bad=20))

    if "flaky_tests" in metrics:
        scores.append(normalize_metric(metrics["flaky_tests"], good=0, bad=10))

    if "ci_test_duration_minutes" in metrics:
        scores.append(normalize_metric(metrics["ci_test_duration_minutes"], good=5, bad=30))

    return round(sum(scores) / len(scores)) if scores else 50


def score_dependencies(metrics):
    """Calcule le score de la categorie Dependances (0-100)."""
    scores = []

    if "outdated_deps_ratio" in metrics:
        scores.append(normalize_metric(metrics["outdated_deps_ratio"], good=0.05, bad=0.5))

    if "known_vulnerabilities" in metrics:
        scores.append(normalize_metric(metrics["known_vulnerabilities"], good=0, bad=5))

    if "abandoned_deps" in metrics:
        scores.append(normalize_metric(metrics["abandoned_deps"], good=0, bad=3))

    if "unpinned_deps" in metrics:
        scores.append(normalize_metric(metrics["unpinned_deps"], good=0, bad=10))

    if "missing_lock_files" in metrics:
        scores.append(0 if metrics["missing_lock_files"] > 0 else 100)

    return round(sum(scores) / len(scores)) if scores else 50


def score_documentation(metrics):
    """Calcule le score de la categorie Documentation (0-100)."""
    scores = []

    if "has_readme" in metrics:
        scores.append(100 if metrics["has_readme"] else 0)

    if "docstring_ratio" in metrics:
        scores.append(normalize_metric(metrics["docstring_ratio"], good=0.6, bad=0.1))

    if "api_documented" in metrics:
        scores.append(100 if metrics["api_documented"] else 30)

    if "has_contributing" in metrics:
        scores.append(100 if metrics["has_contributing"] else 50)

    if "has_changelog" in metrics:
        scores.append(100 if metrics["has_changelog"] else 40)

    return round(sum(scores) / len(scores)) if scores else 50


def score_infrastructure(metrics):
    """Calcule le score de la categorie Infrastructure (0-100)."""
    scores = []

    if "has_ci_cd" in metrics:
        scores.append(100 if metrics["has_ci_cd"] else 0)

    if "has_linting" in metrics:
        scores.append(100 if metrics["has_linting"] else 20)

    if "has_formatting" in metrics:
        scores.append(100 if metrics["has_formatting"] else 30)

    if "has_docker" in metrics:
        scores.append(100 if metrics["has_docker"] else 50)

    if "has_monitoring" in metrics:
        scores.append(100 if metrics["has_monitoring"] else 40)

    if "hardcoded_configs" in metrics:
        scores.append(normalize_metric(metrics["hardcoded_configs"], good=0, bad=10))

    return round(sum(scores) / len(scores)) if scores else 50


def extract_metrics_from_analysis(analysis_result, dep_result=None):
    """Extrait les metriques a partir des resultats d'analyse bruts."""
    metrics = {}

    if "summary" in analysis_result:
        s = analysis_result["summary"]
        metrics["avg_cyclomatic_complexity"] = s.get("avg_cyclomatic_complexity", 0)
        metrics["max_cyclomatic_complexity"] = s.get("max_cyclomatic_complexity", 0)
        metrics["avg_file_size"] = s.get("avg_file_size", 0)
        metrics["test_ratio"] = s.get("test_ratio", 0)

        if "duplication" in s:
            metrics["duplication_ratio"] = s["duplication"].get("ratio_percent", 0)

        if "debt_markers" in s:
            metrics["debt_markers_per_kloc"] = s["debt_markers"].get("per_kloc", 0)

        if "issues" in s:
            by_sev = s["issues"].get("by_severity", {})
            metrics["critical_issues"] = by_sev.get("critical", 0)
            metrics["high_issues"] = by_sev.get("high", 0)

    if dep_result and "summary" in dep_result:
        ds = dep_result["summary"]
        total = ds.get("total_dependencies", 1)
        metrics["unpinned_deps"] = len([
            f for f in dep_result.get("dependency_findings", [])
            if any(i["type"] == "unpinned" for i in f.get("issues", []))
        ])
        metrics["missing_lock_files"] = len(dep_result.get("lock_file_findings", []))

    return metrics


def calculate_health_score(metrics, weights=None):
    """Calcule le Health Score global."""
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()

    # Calculer le score par categorie
    category_scores = {
        "code": score_code(metrics),
        "architecture": score_architecture(metrics),
        "tests": score_tests(metrics),
        "dependencies": score_dependencies(metrics),
        "documentation": score_documentation(metrics),
        "infrastructure": score_infrastructure(metrics),
    }

    # Score global pondere
    total_weight = sum(weights.get(cat, 0) for cat in category_scores)
    if total_weight == 0:
        total_weight = 1

    health_score = sum(
        weights.get(cat, 0) * score
        for cat, score in category_scores.items()
    ) / total_weight

    health_score = round(health_score)

    # Interpretation
    if health_score >= 80:
        interpretation = "Excellent"
        description = "Dette maitrisee, maintenance aisee"
    elif health_score >= 60:
        interpretation = "Bon"
        description = "Quelques points d'attention, globalement sain"
    elif health_score >= 40:
        interpretation = "Attention"
        description = "Dette significative, plan de remediation necessaire"
    elif health_score >= 20:
        interpretation = "Critique"
        description = "Dette importante, impact sur la productivite"
    else:
        interpretation = "Urgence"
        description = "Risque eleve, action immediate requise"

    return {
        "health_score": health_score,
        "interpretation": interpretation,
        "description": description,
        "category_scores": category_scores,
        "weights": weights,
        "metrics_used": metrics,
    }


def parse_weights(weights_str):
    """Parse une chaine de poids 'code=25,arch=20,...'."""
    weights = DEFAULT_WEIGHTS.copy()
    aliases = {
        "arch": "architecture",
        "test": "tests",
        "deps": "dependencies",
        "doc": "documentation",
        "docs": "documentation",
        "infra": "infrastructure",
    }

    if weights_str:
        for pair in weights_str.split(","):
            key, val = pair.split("=")
            key = key.strip()
            key = aliases.get(key, key)
            weights[key] = float(val.strip()) / 100

    return weights


def main():
    parser = argparse.ArgumentParser(description="Calcul du Health Score")
    parser.add_argument("metrics_file", nargs="?", help="Fichier JSON de metriques")
    parser.add_argument("--from-analysis", help="Fichier JSON de resultats d'analyse (sortie de analyze_codebase.py)")
    parser.add_argument("--deps", help="Fichier JSON de resultats de scan de dependances (sortie de scan_dependencies.py)")
    parser.add_argument("--weights", help="Poids personnalises : code=25,arch=20,tests=20,deps=15,docs=10,infra=10")
    parser.add_argument("--json", action="store_true", help="Sortie en JSON")

    args = parser.parse_args()

    weights = parse_weights(args.weights)

    if args.from_analysis:
        with open(args.from_analysis, "r") as f:
            analysis = json.load(f)
        dep_result = None
        if args.deps:
            with open(args.deps, "r") as f:
                dep_result = json.load(f)
        metrics = extract_metrics_from_analysis(analysis, dep_result)
    elif args.metrics_file:
        with open(args.metrics_file, "r") as f:
            metrics = json.load(f)
    else:
        # Lire depuis stdin
        metrics = json.load(sys.stdin)

    result = calculate_health_score(metrics, weights)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        hs = result["health_score"]
        print(f"\n{'='*60}")
        print(f"  HEALTH SCORE : {hs}/100 — {result['interpretation']}")
        print(f"  {result['description']}")
        print(f"{'='*60}\n")

        print("  Scores par categorie :")
        for cat, score in result["category_scores"].items():
            weight = result["weights"].get(cat, 0)
            bar = "#" * (score // 5) + "." * (20 - score // 5)
            label = "OK" if score >= 60 else "ATTENTION" if score >= 40 else "CRITIQUE"
            print(f"    {cat:20s} [{bar}] {score:3d}/100 (poids: {weight:.0%}) {label}")

        print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
