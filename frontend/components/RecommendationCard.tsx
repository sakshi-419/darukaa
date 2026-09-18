'use client';

import React, { useState } from 'react';
import { BiodiversityRecommendation } from '../lib/types';
import { ExternalLink, CheckCircle2, TrendingUp, TrendingDown, Clock, ShieldCheck, ChevronDown, ChevronUp, Link as LinkIcon } from 'lucide-react';

interface RecommendationCardProps {
  recommendation: BiodiversityRecommendation;
  index: number;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation, index }) => {
  const [expanded, setExpanded] = useState(false);

  const confColors = {
    high: 'bg-emerald-950 border-emerald-700 text-emerald-300',
    medium: 'bg-amber-950 border-amber-700 text-amber-300',
    low: 'bg-rose-950 border-rose-700 text-rose-300'
  };

  return (
    <div className="bg-[#111f17] border border-[#1e382a] rounded-xl p-5 shadow-lg space-y-4 transition-all duration-200 hover:border-emerald-700/50">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-900/60 text-emerald-300 border border-emerald-700/40">
              Intervention #{index + 1}
            </span>
            <span className={`text-[11px] font-medium px-2 py-0.5 rounded border capitalize ${confColors[recommendation.confidence] || confColors.medium}`}>
              Confidence: {recommendation.confidence}
            </span>
          </div>
          <h4 className="text-base font-semibold text-neutral-100 pt-1">
            {recommendation.title}
          </h4>
        </div>
      </div>

      {/* Action Statement */}
      <div className="p-3.5 rounded-lg bg-[#16291f] border border-[#234232] text-sm text-neutral-200 leading-relaxed">
        <div className="font-medium text-emerald-400 text-xs uppercase tracking-wider mb-1 flex items-center gap-1.5">
          <CheckCircle2 className="w-3.5 h-3.5" /> Recommended Action
        </div>
        {recommendation.action}
      </div>

      {/* Why It Works (Scientific Reasoning) */}
      <div className="space-y-1.5 text-xs">
        <div className="font-semibold text-neutral-300 uppercase tracking-wider flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Scientific Reasoning (Mechanisms)
        </div>
        <p className="text-neutral-400 leading-relaxed">
          {recommendation.why_it_works}
        </p>
      </div>

      {/* Impacted Metrics Chips */}
      <div className="space-y-2 pt-1 border-t border-[#1d3326]">
        <span className="text-[11px] font-medium text-neutral-400 uppercase tracking-wider">
          Expected Metric Trajectories:
        </span>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
          {recommendation.impacted_metrics.map((m, i) => (
            <div key={i} className="flex items-center justify-between p-2 rounded bg-[#13241b] border border-[#203a2c]">
              <span className="text-neutral-300 capitalize">
                {m.metric.replace(/_/g, ' ')}
              </span>
              <span className={`flex items-center text-[11px] font-bold ${m.direction === 'increase' ? 'text-emerald-400' : 'text-cyan-400'}`}>
                {m.direction === 'increase' ? (
                  <>↑ Increase</>
                ) : (
                  <>↓ Decrease</>
                )}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Time Horizon Dropdown / Expand */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between pt-2 border-t border-[#1d3326] text-xs font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
      >
        <span>Ecological Time Horizon & Scientific Evidence ({recommendation.evidence.length} sources)</span>
        {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {expanded && (
        <div className="space-y-4 pt-2 text-xs animate-fadeIn">
          {/* Time Horizon */}
          <div className="p-3 rounded-lg bg-[#0d1a12] border border-[#1d3326] space-y-2">
            <div className="flex items-center gap-1.5 text-amber-300 font-semibold uppercase text-[11px]">
              <Clock className="w-3.5 h-3.5" /> Progression Horizon
            </div>
            <div className="space-y-1.5 text-neutral-300">
              <div><strong className="text-neutral-200">Short-term:</strong> {recommendation.time_horizon.short_term}</div>
              <div><strong className="text-neutral-200">Medium-term:</strong> {recommendation.time_horizon.medium_term}</div>
              <div><strong className="text-neutral-200">Long-term:</strong> {recommendation.time_horizon.long_term}</div>
            </div>
          </div>

          {/* Scientific Evidence Citations */}
          <div className="space-y-2">
            <div className="font-semibold text-neutral-300 uppercase tracking-wider flex items-center gap-1.5 text-[11px]">
              <LinkIcon className="w-3.5 h-3.5 text-emerald-400" /> Peer-Reviewed Citations & Authorities
            </div>
            <div className="space-y-2">
              {recommendation.evidence.map((ev, i) => (
                <div key={i} className="p-2.5 rounded-lg bg-[#0d1a12] border border-[#1b3425] space-y-1">
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-medium text-neutral-200">
                      [{i + 1}] {ev.title}
                    </span>
                    <a
                      href={ev.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-emerald-400 hover:text-emerald-300 flex items-center gap-1 text-[11px] shrink-0"
                    >
                      <span>{ev.organization} ({ev.year})</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                  <p className="text-[11px] text-neutral-400 italic">
                    "{ev.relevance}"
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Connected Variables */}
          {recommendation.connected_variables && (
            <div className="flex items-center gap-2 pt-1">
              <span className="text-neutral-500 text-[10px] uppercase font-semibold">Variables Linked:</span>
              <div className="flex flex-wrap gap-1">
                {recommendation.connected_variables.map((v, i) => (
                  <span key={i} className="text-[10px] px-2 py-0.5 rounded-full bg-[#182e21] text-emerald-300 border border-[#244733]">
                    {v}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
