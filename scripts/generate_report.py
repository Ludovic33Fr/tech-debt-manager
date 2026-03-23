#!/usr/bin/env python3
"""
Generation de rapports de dette technique en differents formats.

Usage:
    python generate_report.py <analysis.json> [--deps deps.json] [--format markdown|html|csv] [--output report.md]
    python generate_report.py <analysis.json> --health-score score.json --format html --output dashboard.html

Formats supportes : markdown, html, csv
"""

import argparse
import csv
import io
import json
import os
import sys
from datetime import datetime


def load_json(filepath):
    """Charge un fichier JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_markdown_report(analysis, deps=None, health=None, project_name=None):
    """Genere un rapport au format Markdown."""
    now = datetime.now().strftime("%Y-%m-%d")
    name = project_name or os.path.basename(analysis.get("summary", {}).get("project_root", "Projet"))
    hs = health.get("health_score", "N/A") if health else "N/A"
    interp = health.get("interpretation", "") if health else ""

    report = []
    report.append(f"# Rapport de dette technique — {name}")
    report.append(f"**Date** : {now}  |  **Health Score** : {hs}/100  |  **Statut** : {interp}")
    report.append("")

    # Resume executif
    s = analysis.get("summary", {})
    report.append("## Resume executif")
    report.append("")

    total_issues = s.get("issues", {}).get("total", 0)
    critical = s.get("issues", {}).get("by_severity", {}).get("critical", 0)
    high = s.get("issues", {}).get("by_severity", {}).get("high", 0)

    if critical > 0:
        report.append(f"Le projet presente **{critical} problemes critiques** et **{high} problemes de severite elevee** "
                      f"qui necessitent une attention immediate. ")
    elif high > 0:
        report.append(f"Le projet presente **{high} problemes de severite elevee** a traiter en priorite. ")
    elif total_issues > 0:
        report.append(f"Le projet presente **{total_issues} points d'amelioration** identifies. ")
    else:
        report.append("Le projet est en bonne sante technique. ")

    report.append(f"Le codebase contient **{s.get('total_loc', 'N/A'):,} lignes de code** "
                  f"reparties dans **{s.get('source_files', 'N/A')} fichiers source**.")
    report.append("")

    # Metriques cles
    report.append("## Metriques cles")
    report.append("")
    report.append("| Metrique | Valeur | Seuil recommande | Statut |")
    report.append("|----------|--------|-----------------|--------|")

    cc = s.get("avg_cyclomatic_complexity", 0)
    report.append(f"| Complexite cyclomatique moyenne | {cc:.1f} | < 10 | {'OK' if cc < 10 else 'ATTENTION' if cc < 20 else 'CRITIQUE'} |")

    dup = s.get("duplication", {}).get("ratio_percent", 0)
    report.append(f"| Duplication | {dup:.1f}% | < 5% | {'OK' if dup < 5 else 'ATTENTION' if dup < 10 else 'CRITIQUE'} |")

    tr = s.get("test_ratio", 0)
    report.append(f"| Ratio tests/source | {tr:.2f} | > 0.5 | {'OK' if tr > 0.5 else 'ATTENTION' if tr > 0.3 else 'CRITIQUE'} |")

    markers = s.get("debt_markers", {}).get("per_kloc", 0)
    report.append(f"| Marqueurs dette/KLOC | {markers:.1f} | < 5 | {'OK' if markers < 5 else 'ATTENTION' if markers < 10 else 'CRITIQUE'} |")

    report.append("")

    # Health Score par categorie
    if health and "category_scores" in health:
        report.append("## Scores par categorie")
        report.append("")
        report.append("| Categorie | Score | Poids | Statut |")
        report.append("|-----------|-------|-------|--------|")
        for cat, score in health["category_scores"].items():
            weight = health.get("weights", {}).get(cat, 0)
            status = "OK" if score >= 60 else "ATTENTION" if score >= 40 else "CRITIQUE"
            report.append(f"| {cat.capitalize()} | {score}/100 | {weight:.0%} | {status} |")
        report.append("")

    # Top problemes
    files = analysis.get("files", [])
    problematic_files = [f for f in files if f.get("issues")]

    if problematic_files:
        report.append("## Top problemes prioritaires")
        report.append("")

        # Collecter toutes les issues et les trier par severite
        all_issues = []
        severity_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3}

        for f in problematic_files:
            for issue in f.get("issues", []):
                all_issues.append({
                    "file": f["file"],
                    "severity": issue["severity"],
                    "type": issue["type"],
                    "detail": issue["detail"],
                })

        all_issues.sort(key=lambda x: severity_order.get(x["severity"], 99))

        for i, issue in enumerate(all_issues[:15], 1):
            sev_label = {"critical": "CRITIQUE", "high": "ELEVE", "moderate": "MODERE", "low": "FAIBLE"}
            report.append(f"{i}. **[{sev_label.get(issue['severity'], issue['severity'])}]** "
                         f"`{issue['file']}` — {issue['type']}: {issue['detail']}")
        report.append("")

    # Dependances
    if deps:
        dep_findings = deps.get("dependency_findings", [])
        lock_findings = deps.get("lock_file_findings", [])

        if dep_findings or lock_findings:
            report.append("## Dependances")
            report.append("")
            ds = deps.get("summary", {})
            report.append(f"- **{ds.get('total_dependencies', 0)}** dependances totales")
            report.append(f"- **{ds.get('findings_count', 0)}** problemes detectes")
            report.append("")

            for finding in lock_findings:
                report.append(f"- **[{finding['severity'].upper()}]** {finding['detail']}")

            for finding in dep_findings[:10]:
                for issue in finding["issues"]:
                    report.append(f"- **[{issue['severity'].upper()}]** `{finding['dependency']}` : {issue['detail']}")
            report.append("")

    # Marqueurs de dette
    debt_markers = analysis.get("all_debt_markers", [])
    if debt_markers:
        report.append("## Marqueurs de dette (TODO/FIXME/HACK)")
        report.append("")
        report.append(f"**{len(debt_markers)} marqueurs** trouves dans le codebase :")
        report.append("")
        for marker in debt_markers[:20]:
            report.append(f"- `{marker['file']}:{marker['line']}` [{marker['type']}] {marker['text'][:80]}")
        if len(debt_markers) > 20:
            report.append(f"- ... et {len(debt_markers) - 20} autres")
        report.append("")

    # Plan d'action
    report.append("## Plan d'action recommande")
    report.append("")

    report.append("### Court terme (0-2 sprints) — Quick Wins")
    report.append("")
    quick_wins = [i for i in all_issues[:15] if i["severity"] in ("critical", "high")] if problematic_files else []
    if quick_wins:
        for qw in quick_wins[:5]:
            report.append(f"- [ ] Corriger {qw['type']} dans `{qw['file']}`")
    else:
        report.append("- Pas de quick win urgent identifie")
    report.append("")

    report.append("### Moyen terme (1-3 mois)")
    report.append("")
    report.append("- [ ] Ameliorer la couverture de tests sur les modules critiques")
    report.append("- [ ] Reduire la duplication de code")
    report.append("- [ ] Mettre a jour les dependances obsoletes")
    report.append("")

    report.append("### Long terme (3-6 mois)")
    report.append("")
    report.append("- [ ] Refactorer les modules a complexite elevee")
    report.append("- [ ] Ameliorer l'architecture (reduire le couplage)")
    report.append("- [ ] Mettre en place un suivi continu de la dette")
    report.append("")

    # Annexe metriques
    report.append("## Annexe : Metriques brutes")
    report.append("")
    report.append(f"- Fichiers source : {s.get('source_files', 'N/A')}")
    report.append(f"- Fichiers de tests : {s.get('test_files', 'N/A')}")
    report.append(f"- Total LOC : {s.get('total_loc', 'N/A'):,}")
    report.append(f"- CC moyenne : {s.get('avg_cyclomatic_complexity', 'N/A')}")
    report.append(f"- CC max : {s.get('max_cyclomatic_complexity', 'N/A')}")
    report.append(f"- Duplication : {s.get('duplication', {}).get('ratio_percent', 'N/A')}%")
    report.append(f"- Langages : {s.get('languages', {})}")
    report.append("")
    report.append("---")
    report.append(f"*Rapport genere automatiquement le {now} par tech-debt-manager*")

    return "\n".join(report)


def generate_html_report(analysis, deps=None, health=None, project_name=None):
    """Genere un dashboard HTML interactif."""
    now = datetime.now().strftime("%Y-%m-%d")
    name = project_name or os.path.basename(analysis.get("summary", {}).get("project_root", "Projet"))
    hs = health.get("health_score", 50) if health else 50
    cat_scores = health.get("category_scores", {}) if health else {}
    interp = health.get("interpretation", "N/A") if health else "N/A"
    s = analysis.get("summary", {})

    # Couleur selon le score
    if hs >= 80:
        color = "#22c55e"
    elif hs >= 60:
        color = "#eab308"
    elif hs >= 40:
        color = "#f97316"
    else:
        color = "#ef4444"

    # Collecter les issues
    all_issues = []
    for f in analysis.get("files", []):
        for issue in f.get("issues", []):
            all_issues.append({
                "file": f["file"],
                "severity": issue["severity"],
                "type": issue["type"],
                "detail": issue["detail"],
                "language": f.get("language", ""),
            })

    issues_json = json.dumps(all_issues, ensure_ascii=False)
    cat_scores_json = json.dumps(cat_scores, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Dette Technique — {name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }}
        .header {{ text-align: center; margin-bottom: 2rem; }}
        .header h1 {{ font-size: 1.8rem; color: #f8fafc; margin-bottom: 0.5rem; }}
        .header .meta {{ color: #94a3b8; font-size: 0.9rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 1.5rem; border: 1px solid #334155; }}
        .card h2 {{ font-size: 1.1rem; color: #94a3b8; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.85rem; }}
        .score-gauge {{ text-align: center; padding: 2rem 0; }}
        .score-value {{ font-size: 4rem; font-weight: 800; color: {color}; line-height: 1; }}
        .score-label {{ font-size: 1.2rem; color: #94a3b8; margin-top: 0.5rem; }}
        .score-bar {{ display: flex; align-items: center; margin: 0.5rem 0; }}
        .score-bar .label {{ width: 120px; font-size: 0.85rem; color: #94a3b8; }}
        .score-bar .bar-bg {{ flex: 1; height: 8px; background: #334155; border-radius: 4px; overflow: hidden; }}
        .score-bar .bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.5s; }}
        .metric-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
        .metric {{ text-align: center; padding: 1rem; background: #0f172a; border-radius: 8px; }}
        .metric .value {{ font-size: 1.8rem; font-weight: 700; }}
        .metric .label {{ font-size: 0.8rem; color: #94a3b8; margin-top: 0.25rem; }}
        .ok {{ color: #22c55e; }}
        .warn {{ color: #eab308; }}
        .crit {{ color: #ef4444; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ text-align: left; padding: 0.75rem; border-bottom: 2px solid #334155; color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; cursor: pointer; }}
        th:hover {{ color: #f8fafc; }}
        td {{ padding: 0.75rem; border-bottom: 1px solid #1e293b; font-size: 0.9rem; }}
        tr:hover {{ background: #1e293b; }}
        .badge {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }}
        .badge-critical {{ background: #7f1d1d; color: #fca5a5; }}
        .badge-high {{ background: #78350f; color: #fcd34d; }}
        .badge-moderate {{ background: #1e3a5f; color: #93c5fd; }}
        .badge-low {{ background: #1c3829; color: #86efac; }}
        .filters {{ display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }}
        .filter-btn {{ padding: 0.4rem 0.8rem; border-radius: 6px; border: 1px solid #334155; background: #1e293b; color: #e2e8f0; cursor: pointer; font-size: 0.8rem; }}
        .filter-btn:hover, .filter-btn.active {{ background: #334155; border-color: #60a5fa; }}
        footer {{ text-align: center; color: #475569; font-size: 0.8rem; margin-top: 2rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Dashboard dette technique — {name}</h1>
        <div class="meta">Genere le {now} | {s.get('source_files', 'N/A')} fichiers | {s.get('total_loc', 0):,} LOC</div>
    </div>

    <div class="grid">
        <div class="card">
            <h2>Health Score</h2>
            <div class="score-gauge">
                <div class="score-value">{hs}</div>
                <div class="score-label">{interp}</div>
            </div>
        </div>

        <div class="card">
            <h2>Scores par categorie</h2>
            <div id="category-bars"></div>
        </div>

        <div class="card">
            <h2>Metriques cles</h2>
            <div class="metric-grid">
                <div class="metric">
                    <div class="value {'ok' if s.get('avg_cyclomatic_complexity', 0) < 10 else 'warn' if s.get('avg_cyclomatic_complexity', 0) < 20 else 'crit'}">{s.get('avg_cyclomatic_complexity', 0):.1f}</div>
                    <div class="label">CC Moyenne</div>
                </div>
                <div class="metric">
                    <div class="value {'ok' if s.get('duplication', {{}}).get('ratio_percent', 0) < 5 else 'warn' if s.get('duplication', {{}}).get('ratio_percent', 0) < 10 else 'crit'}">{s.get('duplication', {{}}).get('ratio_percent', 0):.1f}%</div>
                    <div class="label">Duplication</div>
                </div>
                <div class="metric">
                    <div class="value {'ok' if s.get('test_ratio', 0) > 0.5 else 'warn' if s.get('test_ratio', 0) > 0.3 else 'crit'}">{s.get('test_ratio', 0):.2f}</div>
                    <div class="label">Ratio Tests</div>
                </div>
                <div class="metric">
                    <div class="value {'ok' if s.get('debt_markers', {{}}).get('per_kloc', 0) < 5 else 'warn' if s.get('debt_markers', {{}}).get('per_kloc', 0) < 10 else 'crit'}">{s.get('debt_markers', {{}}).get('per_kloc', 0):.1f}</div>
                    <div class="label">Marqueurs/KLOC</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>Resume</h2>
            <div class="metric-grid">
                <div class="metric">
                    <div class="value" style="color: #f8fafc">{s.get('source_files', 0)}</div>
                    <div class="label">Fichiers source</div>
                </div>
                <div class="metric">
                    <div class="value" style="color: #f8fafc">{s.get('test_files', 0)}</div>
                    <div class="label">Fichiers de tests</div>
                </div>
                <div class="metric">
                    <div class="value" style="color: #f8fafc">{s.get('issues', {{}}).get('total', 0)}</div>
                    <div class="label">Issues detectees</div>
                </div>
                <div class="metric">
                    <div class="value crit">{s.get('issues', {{}}).get('by_severity', {{}}).get('critical', 0)}</div>
                    <div class="label">Issues critiques</div>
                </div>
            </div>
        </div>
    </div>

    <div class="card" style="margin-bottom: 2rem;">
        <h2>Issues detectees</h2>
        <div class="filters">
            <button class="filter-btn active" onclick="filterIssues('all')">Toutes</button>
            <button class="filter-btn" onclick="filterIssues('critical')">Critiques</button>
            <button class="filter-btn" onclick="filterIssues('high')">Elevees</button>
            <button class="filter-btn" onclick="filterIssues('moderate')">Moderees</button>
            <button class="filter-btn" onclick="filterIssues('low')">Faibles</button>
        </div>
        <table>
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Severite</th>
                    <th onclick="sortTable(1)">Fichier</th>
                    <th onclick="sortTable(2)">Type</th>
                    <th onclick="sortTable(3)">Detail</th>
                </tr>
            </thead>
            <tbody id="issues-table"></tbody>
        </table>
    </div>

    <footer>
        Rapport genere par tech-debt-manager | {now}
    </footer>

    <script>
        const issues = {issues_json};
        const catScores = {cat_scores_json};

        // Render category bars
        const barsDiv = document.getElementById('category-bars');
        Object.entries(catScores).forEach(([cat, score]) => {{
            const color = score >= 60 ? '#22c55e' : score >= 40 ? '#eab308' : '#ef4444';
            barsDiv.innerHTML += `
                <div class="score-bar">
                    <span class="label">${{cat}}</span>
                    <div class="bar-bg"><div class="bar-fill" style="width:${{score}}%;background:${{color}}"></div></div>
                    <span style="width:50px;text-align:right;font-size:0.85rem;font-weight:600;color:${{color}}">${{score}}</span>
                </div>`;
        }});

        // Render issues table
        function renderIssues(data) {{
            const tbody = document.getElementById('issues-table');
            tbody.innerHTML = data.map(i => `
                <tr data-severity="${{i.severity}}">
                    <td><span class="badge badge-${{i.severity}}">${{i.severity}}</span></td>
                    <td><code>${{i.file}}</code></td>
                    <td>${{i.type}}</td>
                    <td>${{i.detail}}</td>
                </tr>`).join('');
        }}

        function filterIssues(severity) {{
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            const filtered = severity === 'all' ? issues : issues.filter(i => i.severity === severity);
            renderIssues(filtered);
        }}

        let sortDir = 1;
        function sortTable(col) {{
            const keys = ['severity', 'file', 'type', 'detail'];
            issues.sort((a, b) => {{
                const va = a[keys[col]] || '';
                const vb = b[keys[col]] || '';
                return va.localeCompare(vb) * sortDir;
            }});
            sortDir *= -1;
            renderIssues(issues);
        }}

        renderIssues(issues);
    </script>
</body>
</html>"""

    return html


def generate_csv_report(analysis, deps=None, health=None):
    """Genere un rapport CSV pour import dans un tableur."""
    output = io.StringIO()
    writer = csv.writer(output)

    # En-tete
    writer.writerow([
        "ID", "Categorie", "Description", "Fichier/Module", "Severite",
        "Impact", "Effort", "Score", "Statut", "Assigne", "Sprint cible"
    ])

    idx = 1
    severity_impact = {"critical": 5, "high": 4, "moderate": 3, "low": 2}
    severity_effort = {"critical": 2, "high": 3, "moderate": 2, "low": 1}

    for f in analysis.get("files", []):
        for issue in f.get("issues", []):
            impact = severity_impact.get(issue["severity"], 3)
            effort = severity_effort.get(issue["severity"], 2)
            score = round(impact * 3 * (1 / effort), 1)
            writer.writerow([
                f"TD-{idx:04d}",
                issue["type"],
                issue["detail"],
                f["file"],
                issue["severity"].upper(),
                impact,
                effort,
                score,
                "Open",
                "",
                "",
            ])
            idx += 1

    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description="Generation de rapport de dette technique")
    parser.add_argument("analysis", help="Fichier JSON d'analyse (sortie de analyze_codebase.py)")
    parser.add_argument("--deps", help="Fichier JSON de dependances (sortie de scan_dependencies.py)")
    parser.add_argument("--health-score", dest="health", help="Fichier JSON de Health Score (sortie de calculate_health_score.py)")
    parser.add_argument("--format", choices=["markdown", "html", "csv"], default="markdown", help="Format de sortie")
    parser.add_argument("--output", "-o", help="Fichier de sortie (par defaut : stdout)")
    parser.add_argument("--name", help="Nom du projet")

    args = parser.parse_args()

    analysis = load_json(args.analysis)
    deps = load_json(args.deps) if args.deps else None
    health = load_json(args.health) if args.health else None

    generators = {
        "markdown": lambda: generate_markdown_report(analysis, deps, health, args.name),
        "html": lambda: generate_html_report(analysis, deps, health, args.name),
        "csv": lambda: generate_csv_report(analysis, deps, health),
    }

    content = generators[args.format]()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Rapport genere : {args.output}", file=sys.stderr)
    else:
        print(content)


if __name__ == "__main__":
    main()
