'use client';

import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../lib/api';
import { ChatResponse, EnvironmentalState, BiodiversityRecommendation, TransparencyTrace, ChatMessage } from '../lib/types';
import { RecommendationCard } from './RecommendationCard';
import { Send, Sparkles, HelpCircle, ArrowRight, ShieldAlert, Cpu, Network } from 'lucide-react';

interface ChatInterfaceProps {
  conversationId: string;
  messages: ChatMessage[];
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  onStateUpdate: (state: EnvironmentalState) => void;
  onOpenTransparency: (trace: TransparencyTrace) => void;
  loading: boolean;
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  conversationId,
  messages,
  setMessages,
  onStateUpdate,
  onOpenTransparency,
  loading,
  setLoading,
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (textToSend?: string) => {
    const message = textToSend || input;
    if (!message.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: message,
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const res: ChatResponse = await sendChatMessage(message, conversationId);
      onStateUpdate(res.environmental_state);

      const botMsg: ChatMessage = {
        id: `bot_${Date.now()}`,
        role: 'assistant',
        content: res.overall_diagnosis || 'Analysis completed.',
        status: res.status,
        clarification_questions: res.clarification_questions,
        recommendations: res.recommendations,
        causal_pathways: res.causal_pathways,
        transparency: res.transparency,
        insufficient_evidence_notice: res.insufficient_evidence_notice,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          role: 'assistant',
          content: `Connection error: ${err.message}. Please ensure the FastAPI backend is running on port 8000.`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl p-4 shadow-md leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-emerald-800 text-white rounded-tr-none'
                  : 'bg-[#0f1b14] border border-[#1d3326] text-neutral-200 rounded-tl-none space-y-4'
              }`}
            >
              {/* Message Header / Badge */}
              <div className="flex items-center justify-between gap-2 text-xs opacity-70 mb-1">
                <span className="font-semibold uppercase tracking-wider">
                  {msg.role === 'user' ? 'Environmental Manager' : 'Darukaa AI Scientist'}
                </span>
                {msg.status === 'needs_information' && (
                  <span className="px-2 py-0.5 rounded-full bg-amber-950 border border-amber-800 text-amber-300 font-mono text-[10px]">
                    Needs Information
                  </span>
                )}
                {msg.status === 'diagnosed' && (
                  <span className="px-2 py-0.5 rounded-full bg-emerald-950 border border-emerald-800 text-emerald-300 font-mono text-[10px]">
                    Diagnosed
                  </span>
                )}
              </div>

              {/* Insufficient Evidence Warning Notice */}
              {msg.insufficient_evidence_notice && (
                <div className="p-3 rounded-lg bg-rose-950/70 border border-rose-800 text-rose-300 text-xs flex items-start gap-2">
                  <ShieldAlert className="w-4 h-4 shrink-0 text-rose-400 mt-0.5" />
                  <div>
                    <strong className="block font-semibold">Guardrail Notice:</strong>
                    {msg.insufficient_evidence_notice}
                  </div>
                </div>
              )}

              {/* Text Body */}
              <div className="text-sm whitespace-pre-wrap leading-relaxed">
                {msg.content}
              </div>

              {/* Clarification Questions with quick-fill chips */}
              {msg.clarification_questions && msg.clarification_questions.length > 0 && (
                <div className="p-3.5 rounded-xl bg-[#14261c] border border-[#213e2d] space-y-2.5">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-300 uppercase">
                    <HelpCircle className="w-3.5 h-3.5" /> Required Diagnostic Details:
                  </div>
                  <ul className="space-y-1.5 text-xs text-neutral-300">
                    {msg.clarification_questions.map((q, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-emerald-400 font-mono">{idx + 1}.</span>
                        <span>{q}</span>
                      </li>
                    ))}
                  </ul>
                  <div className="pt-2 flex flex-wrap gap-2">
                    <button
                      onClick={() => handleSend('Soil carbon is 0.3%, rainfall is 450 mm, crop is wheat in monoculture.')}
                      className="text-[11px] px-2.5 py-1 rounded-lg bg-[#1a3325] border border-[#274f38] text-emerald-300 hover:bg-[#204230] transition-colors flex items-center gap-1"
                    >
                      <Sparkles className="w-3 h-3" /> Quick Provide: SOC 0.3%, 450mm, Wheat Monoculture
                    </button>
                    <button
                      onClick={() => handleSend('Soil pH is 7.8 and moisture is around 15%.')}
                      className="text-[11px] px-2.5 py-1 rounded-lg bg-[#1a3325] border border-[#274f38] text-emerald-300 hover:bg-[#204230] transition-colors"
                    >
                      Quick Provide: pH 7.8, Moisture 15%
                    </button>
                    <button
                      onClick={() => handleSend('Location is Rajasthan semi-arid dryland, growing wheat.')}
                      className="text-[11px] px-2.5 py-1 rounded-lg bg-[#1a3325] border border-[#274f38] text-emerald-300 hover:bg-[#204230] transition-colors"
                    >
                      Quick Provide: Rajasthan Semi-Arid
                    </button>
                  </div>
                </div>
              )}

              {/* Causal Pathways Diagram */}
              {msg.causal_pathways && msg.causal_pathways.length > 0 && (
                <div className="p-3.5 rounded-xl bg-[#13241b] border border-[#203c2b] space-y-2">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400 uppercase">
                    <Network className="w-3.5 h-3.5" /> Key Environmental Relationships (≥3 Variables)
                  </div>
                  <div className="space-y-2 text-xs font-mono text-neutral-300">
                    {msg.causal_pathways.map((path, idx) => (
                      <div key={idx} className="p-2 rounded bg-[#0b1710] border border-[#182f21] whitespace-pre-wrap">
                        {path}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations Cards */}
              {msg.recommendations && msg.recommendations.length > 0 && (
                <div className="space-y-3 pt-2">
                  <div className="flex items-center justify-between border-t border-[#1d3527] pt-3">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                      Evidence-Backed Interventions ({msg.recommendations.length})
                    </h4>
                    {msg.transparency && (
                      <button
                        onClick={() => onOpenTransparency(msg.transparency!)}
                        className="text-xs font-medium text-emerald-400 hover:text-emerald-300 flex items-center gap-1 bg-emerald-950/70 border border-emerald-800/60 px-2.5 py-1 rounded-lg transition-colors"
                      >
                        <Sparkles className="w-3.5 h-3.5" />
                        How this was generated
                      </button>
                    )}
                  </div>

                  <div className="space-y-3">
                    {msg.recommendations.map((rec, idx) => (
                      <RecommendationCard key={rec.id} recommendation={rec} index={idx} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-[#0f1b14] border border-[#1d3326] rounded-2xl rounded-tl-none p-4 text-xs text-emerald-400 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              Reasoning across environmental variables and querying knowledge base...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="pt-2 border-t border-[#1d3326]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe your farmland, soil conditions, or query (e.g. 'Carbon is 0.3%, rainfall is 450 mm')..."
            className="flex-1 p-3 rounded-xl bg-[#0f1b14] border border-[#1d3326] text-neutral-100 text-sm focus:outline-none focus:border-emerald-500 placeholder-neutral-500"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="p-3 rounded-xl bg-emerald-700 hover:bg-emerald-600 disabled:opacity-40 text-white transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
