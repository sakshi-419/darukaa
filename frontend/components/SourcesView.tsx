'use client';

import React, { useEffect, useState } from 'react';
import { getSources } from '../lib/api';
import { SourceItem } from '../lib/types';
import { BookOpen, ExternalLink, ShieldCheck, Tag } from 'lucide-react';

export const SourcesView: React.FC = () => {
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSources()
      .then((res) => {
        setSources(res.sources);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="space-y-6 max-w-4xl mx-auto p-4 animate-fadeIn">
      <div className="border-b border-[#1f3b2a] pb-4">
        <div className="flex items-center gap-2.5 text-emerald-400 mb-1">
          <BookOpen className="w-6 h-6" />
          <h2 className="text-xl font-bold text-neutral-100">
            Scientific Knowledge Base & Authoritative Sources
          </h2>
        </div>
        <p className="text-xs text-neutral-400">
          Zero hallucinations policy: All environmental recommendations are strictly bound to peer-reviewed literature and UN scientific assessments.
        </p>
      </div>

      {loading ? (
        <div className="text-center py-12 text-neutral-500 text-sm">
          Loading scientific repository...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sources.map((src) => (
            <div
              key={src.id}
              className="bg-[#0f1b14] border border-[#1d3326] rounded-xl p-5 shadow-lg space-y-3 flex flex-col justify-between hover:border-emerald-700/60 transition-colors"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-400 uppercase">
                    {src.organization} • {src.year}
                  </span>
                  <span className="text-[11px] text-neutral-400 capitalize">
                    {src.topic.replace('_', ' ')}
                  </span>
                </div>
                <h4 className="text-sm font-semibold text-neutral-100 leading-snug">
                  {src.title}
                </h4>
                {src.authors && (
                  <p className="text-xs text-neutral-400 italic">
                    Authors: {src.authors}
                  </p>
                )}
              </div>

              <div className="space-y-3 pt-3 border-t border-[#1a3023]">
                <div className="flex flex-wrap gap-1.5">
                  {src.metrics.map((m, idx) => (
                    <span
                      key={idx}
                      className="text-[10px] px-2 py-0.5 rounded-full bg-[#15271d] border border-[#213d2e] text-neutral-300 flex items-center gap-1"
                    >
                      <Tag className="w-2.5 h-2.5 text-emerald-500" />
                      {m.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>

                <a
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
                >
                  <span>Verify Scientific Publication</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
