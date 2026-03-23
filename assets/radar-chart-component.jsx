/**
 * Composant React pour le graphique radar des categories de dette technique.
 *
 * Usage:
 *   <TechDebtRadar scores={{ code: 75, architecture: 60, tests: 45, dependencies: 80, documentation: 30, infrastructure: 55 }} />
 *
 * Props:
 *   - scores: objet { categorie: score (0-100) }
 *   - size: taille du SVG (defaut: 400)
 *   - showLabels: afficher les labels (defaut: true)
 *   - showValues: afficher les valeurs numeriques (defaut: true)
 *   - color: couleur de remplissage (defaut: auto selon score)
 */

import React, { useMemo } from 'react';

const DEFAULT_CATEGORIES = [
  { key: 'code', label: 'Code' },
  { key: 'architecture', label: 'Architecture' },
  { key: 'tests', label: 'Tests' },
  { key: 'dependencies', label: 'Dépendances' },
  { key: 'documentation', label: 'Documentation' },
  { key: 'infrastructure', label: 'Infrastructure' },
];

function getColor(score) {
  if (score >= 80) return '#22c55e';
  if (score >= 60) return '#eab308';
  if (score >= 40) return '#f97316';
  return '#ef4444';
}

function polarToCartesian(cx, cy, radius, angleDeg) {
  const angleRad = ((angleDeg - 90) * Math.PI) / 180;
  return {
    x: cx + radius * Math.cos(angleRad),
    y: cy + radius * Math.sin(angleRad),
  };
}

export function TechDebtRadar({
  scores = {},
  size = 400,
  showLabels = true,
  showValues = true,
  color,
  categories = DEFAULT_CATEGORIES,
}) {
  const cx = size / 2;
  const cy = size / 2;
  const maxRadius = size * 0.35;
  const levels = [20, 40, 60, 80, 100];
  const n = categories.length;
  const angleStep = 360 / n;

  const avgScore = useMemo(() => {
    const vals = categories.map(c => scores[c.key] || 0);
    return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length);
  }, [scores, categories]);

  const fillColor = color || getColor(avgScore);

  // Points du polygone de donnees
  const dataPoints = categories.map((cat, i) => {
    const score = scores[cat.key] || 0;
    const radius = (score / 100) * maxRadius;
    return polarToCartesian(cx, cy, radius, i * angleStep);
  });

  const dataPath = dataPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} xmlns="http://www.w3.org/2000/svg">
      {/* Background */}
      <rect width={size} height={size} fill="#0f172a" rx="12" />

      {/* Grid levels */}
      {levels.map(level => {
        const r = (level / 100) * maxRadius;
        const points = Array.from({ length: n }, (_, i) => {
          const p = polarToCartesian(cx, cy, r, i * angleStep);
          return `${p.x},${p.y}`;
        }).join(' ');
        return (
          <polygon
            key={level}
            points={points}
            fill="none"
            stroke="#334155"
            strokeWidth="1"
            opacity={0.5}
          />
        );
      })}

      {/* Axis lines */}
      {categories.map((_, i) => {
        const end = polarToCartesian(cx, cy, maxRadius, i * angleStep);
        return (
          <line
            key={`axis-${i}`}
            x1={cx}
            y1={cy}
            x2={end.x}
            y2={end.y}
            stroke="#334155"
            strokeWidth="1"
            opacity={0.5}
          />
        );
      })}

      {/* Data polygon */}
      <path
        d={dataPath}
        fill={fillColor}
        fillOpacity={0.2}
        stroke={fillColor}
        strokeWidth={2}
      />

      {/* Data points */}
      {dataPoints.map((p, i) => (
        <circle
          key={`point-${i}`}
          cx={p.x}
          cy={p.y}
          r={4}
          fill={fillColor}
          stroke="#0f172a"
          strokeWidth={2}
        />
      ))}

      {/* Labels */}
      {showLabels && categories.map((cat, i) => {
        const labelRadius = maxRadius + 30;
        const p = polarToCartesian(cx, cy, labelRadius, i * angleStep);
        const score = scores[cat.key] || 0;
        const scoreColor = getColor(score);

        return (
          <g key={`label-${i}`}>
            <text
              x={p.x}
              y={p.y}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#94a3b8"
              fontSize="12"
              fontFamily="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
            >
              {cat.label}
            </text>
            {showValues && (
              <text
                x={p.x}
                y={p.y + 16}
                textAnchor="middle"
                dominantBaseline="middle"
                fill={scoreColor}
                fontSize="13"
                fontWeight="700"
                fontFamily="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
              >
                {score}
              </text>
            )}
          </g>
        );
      })}

      {/* Center score */}
      <text
        x={cx}
        y={cy - 8}
        textAnchor="middle"
        dominantBaseline="middle"
        fill={fillColor}
        fontSize="28"
        fontWeight="800"
        fontFamily="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
      >
        {avgScore}
      </text>
      <text
        x={cx}
        y={cy + 14}
        textAnchor="middle"
        dominantBaseline="middle"
        fill="#94a3b8"
        fontSize="10"
        fontFamily="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
      >
        HEALTH SCORE
      </text>
    </svg>
  );
}

export default TechDebtRadar;
