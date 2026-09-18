'use client';

import React from 'react';
import { TransparencyTrace } from '../lib/types';
import { X, Network, Database, ShieldCheck, ArrowDown, Cpu, Sparkles } from 'lucide-react';

interface TransparencyModalProps {
  isOpen: boolean;
  onClose: () => void;
  trace?: TransparencyTrace;
}

export const TransparencyModal: React.FC<TransparencyModalProps> = ({ isOpen, onClose, trace }) => {
  if (!isOpen || !trace) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#0e1b13] border border-[#1f3b2a] rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-2xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#1f3b2a]">
          <div className="flex items-center gap-2.5">
            <Sparkles className="w-5 h-5 text-emerald-400" />
            <div>
              <h3 className="text-lg font-bold text-neutral-100">
                How this Recommendation Was Generated
              </h3>
              <p className="text-xs text-neutral-400">
                Transparent RAG audit trail & multi-metric scientific causal deduction
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-neutral-400 hover:text-neutral-200 hover:bg-[#182e22] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Step 1: User Inputs & Extracted Variables */}
        <div className="p-4 rounded-xl bg-[#14261c] border border-[#22402f] space-y-2.5">
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase tracking-wider">
            <Cpu className="w-4 h-4" /> 1. Input Signals & Profile Extraction
          </div>
          <p className="text-xs text-neutral-300">
            Natural language and structured telemetry parsed into verified ecological variables:
          </p>
          <div className="flex flex-wrap gap-2 pt-1">
            {trace.variables_considered.map((v, i) => (
              <span key={i} className="text-xs px-2.5 py-1 rounded-md bg-[#1a3325] border border-[#264b36] text-emerald-300 font-mono">
                {v}
              </span>
            ))}
          </div>
        </div>

        <div className="flex justify-center -my-2 text-emerald-600">
          <ArrowDown className="w-5 h-5" />
        </div>

        {/* Step 2: Multi-Metric Causal Deduction */}
        <div className="p-4 rounded-xl bg-[#14261c] border border-[#22402f] space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase tracking-wider">
            <Network className="w-4 h-4" /> 2. Multi-Metric Reasoning Engine
          </div>
          <p className="text-xs text-neutral-300">
            Causal graph models feedback loops across Soil, Climate, and Land Cover (<strong className="text-emerald-400">≥3 variables linked</strong>):
          </p>
          <div className="space-y-2">
            {trace.causal_chains.map((chain, i) => (
              <div key={i} className="p-3 rounded-lg bg-[#0e1a13] border border-[#1b3425] text-xs font-mono text-neutral-300 space-y-1">
                <div className="text-emerald-400 font-semibold mb-1">
                  Pathway {i + 1}:
                </div>
                <div className="flex flex-wrap items-center gap-1.5 leading-relaxed">
                  {chain.map((step, idx) => (
                    <React.Fragment key={idx}>
                      <span className="text-neutral-200">{step}</span>
                      {idx < chain.length - 1 && (
                        <span className="text-emerald-500 font-bold">→</span>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-center -my-2 text-emerald-600">
          <ArrowDown className="w-5 h-5" />
        </div>

        {/* Step 3: Scientific RAG Retrieval & Validation */}
        <div className="p-4 rounded-xl bg-[#14261c] border border-[#22402f] space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400 uppercase tracking-wider">
            <Database className="w-4 h-4" /> 3. Scientific RAG Retrieval & Validation
          </div>
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-[#0e1a13] border border-[#1b3425]">
              <span className="text-neutral-400 block mb-1">Knowledge Chunks Retrieved:</span>
              <span className="text-xl font-bold font-mono text-emerald-400">
                {trace.retrieved_sources_count}
              </span>
            </div>
            <div className="p-3 rounded-lg bg-[#0e1a13] border border-[#1b3425]">
              <span className="text-neutral-400 block mb-1">Relevant Sources Substantiated:</span>
              <span className="text-xl font-bold font-mono text-emerald-400">
                {trace.relevant_sources_used}
              </span>
            </div>
          </div>
          <div className="p-3 rounded-lg bg-[#0e1a13] border border-[#1b3425] text-xs space-y-1">
            <div className="flex items-center gap-1.5 text-emerald-400 font-semibold">
              <ShieldCheck className="w-4 h-4" /> Verification Guardrails
            </div>
            <p className="text-neutral-300">
              {trace.evidence_validation_summary}
            </p>
          </div>
        </div>

        {/* Close button */}
        <button
          onClick={onClose}
          className="w-full py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-600 text-white font-medium text-sm transition-colors shadow-lg"
        >
          Close Transparency Audit
        </button>
      </div>
    </div>
  );
};
