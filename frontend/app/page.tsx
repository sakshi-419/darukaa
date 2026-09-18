'use client';

import React, { useState } from 'react';
import { ChatInterface } from '../components/ChatInterface';
import { EnvironmentalMetrics } from '../components/EnvironmentalMetrics';
import { TransparencyModal } from '../components/TransparencyModal';
import { JsonInputModal } from '../components/JsonInputModal';
import { SourcesView } from '../components/SourcesView';
import { EvaluationView } from '../components/EvaluationView';
import { EnvironmentalState, TransparencyTrace, ChatResponse, ChatMessage } from '../lib/types';
import { analyzeEnvironmentJson, sendChatMessage } from '../lib/api';
import {
  Plus, MessageSquare, BookOpen, BarChart3, Code2,
  Leaf, ChevronRight, CheckCircle2, RefreshCw, Layers
} from 'lucide-react';

const INITIAL_MESSAGE: ChatMessage = {
  id: 'welcome_msg',
  role: 'assistant',
  content:
    'Welcome to **Darukaa.Earth — Biodiversity Intelligence**.\n\n' +
    'I am your AI Environmental Scientist. I formulate evidence-backed biodiversity interventions by extracting structured environmental parameters, modeling multi-metric causal pathways, and verifying scientific literature from the FAO, IPBES, IPCC, and UNEP.\n\n' +
    'Describe your farmland or ecosystem problem, or select a preloaded scientific demo scenario from the left sidebar.',
};

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chat' | 'sources' | 'evaluation'>('chat');
  const [conversationId, setConversationId] = useState<string>(`conv_${Date.now()}`);
  const [environmentalState, setEnvironmentalState] = useState<EnvironmentalState>({
    location: {},
    soil: {},
    climate: {},
    land: {},
    biodiversity: {},
    human_impact: {},
  });
  const [messages, setMessages] = useState<ChatMessage[]>([INITIAL_MESSAGE]);
  const [loading, setLoading] = useState<boolean>(false);
  const [transparencyTrace, setTransparencyTrace] = useState<TransparencyTrace | undefined>();
  const [isTransparencyOpen, setIsTransparencyOpen] = useState(false);
  const [isJsonModalOpen, setIsJsonModalOpen] = useState(false);

  // 1. New Analysis Reset
  const startNewAnalysis = () => {
    const newId = `conv_${Date.now()}`;
    setConversationId(newId);
    setEnvironmentalState({
      location: {},
      soil: {},
      climate: {},
      land: {},
      biodiversity: {},
      human_impact: {},
    });
    setMessages([INITIAL_MESSAGE]);
    setTransparencyTrace(undefined);
    setActiveTab('chat');
  };

  // 2. Direct JSON Success Handler
  const handleJsonSuccess = (data: ChatResponse) => {
    setEnvironmentalState(data.environmental_state);
    if (data.transparency) {
      setTransparencyTrace(data.transparency);
    }
    const userMsg: ChatMessage = {
      id: `user_json_${Date.now()}`,
      role: 'user',
      content: 'Analyzed Farm Telemetry via Direct Structured JSON Ingestion (POST /api/environment/analyze).',
    };
    const botMsg: ChatMessage = {
      id: `bot_json_${Date.now()}`,
      role: 'assistant',
      content: data.overall_diagnosis || 'Multi-metric environmental diagnosis complete.',
      status: data.status,
      recommendations: data.recommendations,
      causal_pathways: data.causal_pathways,
      transparency: data.transparency,
    };
    setMessages((prev) => [...prev, userMsg, botMsg]);
    setActiveTab('chat');
  };

  // 3. Demo Scenario 1: Semi-Arid Wheat (Direct JSON)
  const runScenario1 = async () => {
    setActiveTab('chat');
    setLoading(true);
    const scenarioPayload = {
      soil_ph: 7.8,
      organic_carbon: 0.3,
      moisture: 15.0,
      rainfall: 450.0,
      crop: 'wheat',
      land_use: 'monoculture',
      region: 'semi-arid',
      country: 'India',
    };
    try {
      const res = await analyzeEnvironmentJson(scenarioPayload);
      handleJsonSuccess(res);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // 4. Demo Scenario 2: Multi-Turn Farm Diagnostic
  const runScenario2 = async () => {
    setActiveTab('chat');
    setLoading(true);
    const convId = `scenario2_${Date.now()}`;
    setConversationId(convId);

    try {
      // Turn 1
      const res1 = await sendChatMessage('Biodiversity is declining on my farm.', convId);
      const msg1User: ChatMessage = { id: `s2_u1_${Date.now()}`, role: 'user', content: 'Biodiversity is declining on my farm.' };
      const msg1Bot: ChatMessage = {
        id: `s2_b1_${Date.now()}`,
        role: 'assistant',
        content: res1.overall_diagnosis || 'Awaiting critical baseline environmental metrics.',
        status: res1.status,
        clarification_questions: res1.clarification_questions,
      };

      // Turn 2
      const res2 = await sendChatMessage('Carbon is 0.3%, rainfall is low and I grow wheat.', convId);
      const msg2User: ChatMessage = { id: `s2_u2_${Date.now()}`, role: 'user', content: 'Carbon is 0.3%, rainfall is low and I grow wheat.' };
      const msg2Bot: ChatMessage = {
        id: `s2_b2_${Date.now()}`,
        role: 'assistant',
        content: res2.overall_diagnosis || 'Recorded SOC 0.3% and wheat crop. Please provide approximate annual rainfall amount in mm.',
        status: res2.status,
        clarification_questions: res2.clarification_questions,
      };

      // Turn 3
      const res3 = await sendChatMessage('Around 450 mm.', convId);
      const msg3User: ChatMessage = { id: `s2_u3_${Date.now()}`, role: 'user', content: 'Around 450 mm.' };
      const msg3Bot: ChatMessage = {
        id: `s2_b3_${Date.now()}`,
        role: 'assistant',
        content: res3.overall_diagnosis || 'Multi-metric diagnosis complete.',
        status: res3.status,
        recommendations: res3.recommendations,
        causal_pathways: res3.causal_pathways,
        transparency: res3.transparency,
      };

      setMessages([INITIAL_MESSAGE, msg1User, msg1Bot, msg2User, msg2Bot, msg3User, msg3Bot]);
      setEnvironmentalState(res3.environmental_state);
      if (res3.transparency) setTransparencyTrace(res3.transparency);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // 5. Demo Scenario 3: 100 Trees Precision Guardrail
  const runScenario3 = async () => {
    setActiveTab('chat');
    setLoading(true);
    const convId = `scenario3_${Date.now()}`;
    setConversationId(convId);
    const query = 'How much will biodiversity increase if I plant 100 trees?';

    try {
      const res = await sendChatMessage(query, convId);
      const userMsg: ChatMessage = { id: `s3_u_${Date.now()}`, role: 'user', content: query };
      const botMsg: ChatMessage = {
        id: `s3_b_${Date.now()}`,
        role: 'assistant',
        content: res.overall_diagnosis || 'Quantitative claim rejected.',
        status: res.status,
        insufficient_evidence_notice: res.insufficient_evidence_notice,
        causal_pathways: res.causal_pathways,
        transparency: res.transparency,
      };
      setMessages((prev) => [...prev, userMsg, botMsg]);
      setEnvironmentalState(res.environmental_state);
      if (res.transparency) setTransparencyTrace(res.transparency);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#070e0a]">
      {/* Left Sidebar */}
      <aside className="w-72 bg-[#0c1611] border-r border-[#192f22] flex flex-col justify-between p-4 shrink-0 overflow-y-auto">
        <div className="space-y-5">
          {/* Logo & Title */}
          <div className="space-y-1 cursor-pointer" onClick={() => setActiveTab('chat')}>
            <div className="flex items-center gap-2.5 text-emerald-400">
              <div className="p-1.5 rounded-lg bg-emerald-950 border border-emerald-800">
                <Leaf className="w-5 h-5 text-emerald-400" />
              </div>
              <h1 className="font-extrabold text-base tracking-tight text-neutral-100">
                Darukaa.Earth
              </h1>
            </div>
            <p className="text-[11px] text-neutral-400 pl-9">
              Biodiversity Intelligence System
            </p>
          </div>

          {/* New Analysis Button */}
          <button
            onClick={startNewAnalysis}
            className="w-full py-2.5 px-3 rounded-xl bg-emerald-700 hover:bg-emerald-600 text-white font-medium text-xs flex items-center justify-center gap-2 shadow-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Environmental Analysis
          </button>

          {/* Navigation Links */}
          <div className="space-y-1">
            <button
              onClick={() => setActiveTab('chat')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                activeTab === 'chat'
                  ? 'bg-[#152a1e] text-emerald-300 border border-[#21432f]'
                  : 'text-neutral-400 hover:text-neutral-200 hover:bg-[#101e16]'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              Diagnostic Dialogue
            </button>

            <button
              onClick={() => setIsJsonModalOpen(true)}
              className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-neutral-400 hover:text-neutral-200 hover:bg-[#101e16] transition-colors"
            >
              <Code2 className="w-4 h-4 text-cyan-400" />
              Structured JSON Analysis
            </button>

            <button
              onClick={() => setActiveTab('sources')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                activeTab === 'sources'
                  ? 'bg-[#152a1e] text-emerald-300 border border-[#21432f]'
                  : 'text-neutral-400 hover:text-neutral-200 hover:bg-[#101e16]'
              }`}
            >
              <BookOpen className="w-4 h-4 text-emerald-400" />
              Scientific Knowledge Base
            </button>

            <button
              onClick={() => setActiveTab('evaluation')}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                activeTab === 'evaluation'
                  ? 'bg-[#152a1e] text-emerald-300 border border-[#21432f]'
                  : 'text-neutral-400 hover:text-neutral-200 hover:bg-[#101e16]'
              }`}
            >
              <BarChart3 className="w-4 h-4 text-amber-400" />
              Evaluation Dashboard
            </button>
          </div>

          {/* Demo Scenarios Section */}
          <div className="pt-2 border-t border-[#192f22] space-y-2">
            <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-neutral-400">
              <span>Interactive Demo Scenarios:</span>
              <span className="text-emerald-500 font-normal">1-Click</span>
            </div>

            <div className="space-y-1.5 text-xs">
              {/* Scenario 1 */}
              <button
                onClick={runScenario1}
                disabled={loading}
                className="w-full text-left p-2.5 rounded-lg bg-[#0f1b14] border border-[#1b3425] hover:border-emerald-600/70 hover:bg-[#14261c] text-neutral-300 space-y-1 transition-all group"
              >
                <div className="font-semibold text-emerald-400 flex items-center justify-between group-hover:translate-x-0.5 transition-transform">
                  <span>Scenario 1: Semi-Arid Wheat</span>
                  <ChevronRight className="w-3.5 h-3.5 text-emerald-500" />
                </div>
                <div className="text-[11px] text-neutral-400 leading-snug">
                  Direct JSON (450mm rain, 0.3% SOC, pH 7.8, monoculture)
                </div>
              </button>

              {/* Scenario 2 */}
              <button
                onClick={runScenario2}
                disabled={loading}
                className="w-full text-left p-2.5 rounded-lg bg-[#0f1b14] border border-[#1b3425] hover:border-emerald-600/70 hover:bg-[#14261c] text-neutral-300 space-y-1 transition-all group"
              >
                <div className="font-semibold text-emerald-400 flex items-center justify-between group-hover:translate-x-0.5 transition-transform">
                  <span>Scenario 2: Multi-Turn Memory</span>
                  <ChevronRight className="w-3.5 h-3.5 text-emerald-500" />
                </div>
                <div className="text-[11px] text-neutral-400 leading-snug">
                  Interactive dialogue with state retention across 3 turns
                </div>
              </button>

              {/* Scenario 3 */}
              <button
                onClick={runScenario3}
                disabled={loading}
                className="w-full text-left p-2.5 rounded-lg bg-[#0f1b14] border border-[#1b3425] hover:border-emerald-600/70 hover:bg-[#14261c] text-neutral-300 space-y-1 transition-all group"
              >
                <div className="font-semibold text-emerald-400 flex items-center justify-between group-hover:translate-x-0.5 transition-transform">
                  <span>Scenario 3: Precision Guardrail</span>
                  <ChevronRight className="w-3.5 h-3.5 text-emerald-500" />
                </div>
                <div className="text-[11px] text-neutral-400 leading-snug">
                  "100 Trees" query rejects fake precision with Science 2020 citation
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Footer Tagline */}
        <div className="pt-4 border-t border-[#192f22] text-[11px] text-neutral-400 leading-snug">
          <em>"From environmental data to evidence-backed biodiversity action."</em>
        </div>
      </aside>

      {/* Center Main Stage */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Bar */}
        <header className="h-14 border-b border-[#192f22] bg-[#0a130e] flex items-center justify-between px-6 shrink-0">
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-neutral-200">
              {activeTab === 'chat' && 'Environmental Diagnostic Dialogue'}
              {activeTab === 'sources' && 'Authoritative Scientific Knowledge Catalog'}
              {activeTab === 'evaluation' && 'System Telemetry & RAG Precision Dashboard'}
            </span>
            <span className="text-xs text-neutral-500 font-mono">
              Session: {conversationId.slice(0, 12)}
            </span>
          </div>

          <div className="flex items-center gap-2.5 text-xs">
            {loading && (
              <span className="flex items-center gap-1.5 text-amber-400 text-xs animate-pulse bg-amber-950/60 border border-amber-800/60 px-2.5 py-1 rounded-full">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Reasoning in progress...
              </span>
            )}
            <span className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#102017] border border-[#1c3928] text-neutral-300 font-mono text-[11px]">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              AI: Gemini 3.5 Flash Lite
            </span>
            <span className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#102017] border border-[#1c3928] text-cyan-300 font-mono text-[11px]">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
              Vector DB: ChromaDB
            </span>
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#102017] border border-[#1c3928] text-emerald-400 font-mono text-[11px]">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Reasoning Engine: Active
            </span>
          </div>
        </header>

        {/* Dynamic Main Workspace */}
        <div className="flex-1 overflow-hidden p-6">
          {activeTab === 'chat' && (
            <div className="h-full flex gap-6">
              {/* Chat Stream */}
              <div className="flex-1 h-full min-w-0">
                <ChatInterface
                  conversationId={conversationId}
                  messages={messages}
                  setMessages={setMessages}
                  loading={loading}
                  setLoading={setLoading}
                  onStateUpdate={(state) => setEnvironmentalState(state)}
                  onOpenTransparency={(trace) => {
                    setTransparencyTrace(trace);
                    setIsTransparencyOpen(true);
                  }}
                />
              </div>

              {/* Right Side: Live Environmental Metrics Panel */}
              <div className="w-80 h-full overflow-y-auto shrink-0 hidden lg:block">
                <EnvironmentalMetrics state={environmentalState} />
              </div>
            </div>
          )}

          {activeTab === 'sources' && (
            <div className="h-full overflow-y-auto">
              <SourcesView />
            </div>
          )}

          {activeTab === 'evaluation' && (
            <div className="h-full overflow-y-auto">
              <EvaluationView />
            </div>
          )}
        </div>
      </main>

      {/* RAG Transparency Modal */}
      <TransparencyModal
        isOpen={isTransparencyOpen}
        onClose={() => setIsTransparencyOpen(false)}
        trace={transparencyTrace}
      />

      {/* Direct Structured JSON Modal */}
      <JsonInputModal
        isOpen={isJsonModalOpen}
        onClose={() => setIsJsonModalOpen(false)}
        onSuccess={handleJsonSuccess}
      />
    </div>
  );
}
