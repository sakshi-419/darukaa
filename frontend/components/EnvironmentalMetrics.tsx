'use client';

import React from 'react';
import { EnvironmentalState } from '../lib/types';
import { Activity, Droplets, Thermometer, Wind, Sprout, ShieldAlert, Compass, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface EnvironmentalMetricsProps {
  state?: EnvironmentalState;
}

export const EnvironmentalMetrics: React.FC<EnvironmentalMetricsProps> = ({ state }) => {
  const soc = state?.soil?.organic_carbon_percent;
  const ph = state?.soil?.ph;
  const moisture = state?.soil?.moisture_percent;
  const rainfall = state?.climate?.annual_rainfall_mm;
  const temp = state?.climate?.temperature_c;
  const crop = state?.land?.crop || 'Not specified';
  const cropping = state?.land?.cropping_system || state?.land?.land_use || 'Not specified';
  const region = state?.location?.region || state?.location?.country || 'Global/Unspecified';

  // SOC status badge & percentage (scale: 0 to 2.5%)
  const getSocStatus = (val?: number) => {
    if (val === undefined || val === null) return { label: 'Awaiting data', color: 'text-neutral-400', bg: 'bg-neutral-800', barColor: 'bg-neutral-700', pct: 0 };
    const pct = Math.min(100, Math.max(5, (val / 2.0) * 100));
    if (val < 0.5) return { label: 'Critical (<0.5%)', color: 'text-rose-400', bg: 'bg-rose-950/70 border border-rose-800/80', barColor: 'bg-rose-500', pct };
    if (val <= 1.2) return { label: 'Sub-optimal', color: 'text-amber-400', bg: 'bg-amber-950/70 border border-amber-800/80', barColor: 'bg-amber-500', pct };
    return { label: 'Optimal', color: 'text-emerald-400', bg: 'bg-emerald-950/70 border border-emerald-800/80', barColor: 'bg-emerald-500', pct };
  };

  const socStatus = getSocStatus(soc);

  // Rainfall percentage (scale: 0 to 1000 mm)
  const rainfallPct = rainfall !== undefined && rainfall !== null ? Math.min(100, Math.max(8, (rainfall / 1000) * 100)) : 0;

  // Moisture percentage (scale: 0 to 40%)
  const moisturePct = moisture !== undefined && moisture !== null ? Math.min(100, Math.max(8, (moisture / 40) * 100)) : 0;

  // pH percentage (scale: 4 to 10)
  const phPct = ph !== undefined && ph !== null ? Math.min(100, Math.max(5, ((ph - 4) / 6) * 100)) : 0;

  // Vulnerability assessment
  const isHighRisk = (soc !== undefined && soc < 0.5) || (rainfall !== undefined && rainfall < 500);

  return (
    <div className="bg-[#0f1b14] border border-[#1d3326] rounded-2xl p-5 shadow-xl space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-[#1d3326]">
        <div className="flex items-center space-x-2">
          <Activity className="w-5 h-5 text-emerald-400" />
          <h3 className="font-bold text-xs tracking-wider text-neutral-200 uppercase">
            Live Environmental Profile
          </h3>
        </div>
        <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-800/80 text-emerald-300 font-mono flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Live Telemetry
        </span>
      </div>

      {/* Main Gauges Grid */}
      <div className="space-y-3">
        {/* 1. Soil Organic Carbon with Gauge */}
        <div className="p-3.5 rounded-xl bg-[#13241b] border border-[#203a2c] space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-neutral-400 flex items-center gap-1.5">
              <Sprout className="w-3.5 h-3.5 text-emerald-400" /> Soil Organic Carbon
            </span>
            <span className="text-sm font-bold text-neutral-100 font-mono">
              {soc !== undefined && soc !== null ? `${soc}%` : '—'}
            </span>
          </div>

          {/* Progress Gauge Bar */}
          <div className="w-full bg-[#0a140e] h-2 rounded-full overflow-hidden p-0.5 border border-[#1b3424]">
            <div
              className={`h-full rounded-full transition-all duration-500 ${socStatus.barColor}`}
              style={{ width: `${socStatus.pct}%` }}
            />
          </div>

          <div className="flex items-center justify-between text-[10px]">
            <span className="text-neutral-500 font-mono">0.0% Critical</span>
            <span className={`font-semibold px-2 py-0.5 rounded ${socStatus.bg} ${socStatus.color}`}>
              {socStatus.label}
            </span>
            <span className="text-neutral-500 font-mono">&gt;1.5% Opt.</span>
          </div>
        </div>

        {/* 2. Annual Rainfall with Gauge */}
        <div className="p-3.5 rounded-xl bg-[#13241b] border border-[#203a2c] space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-neutral-400 flex items-center gap-1.5">
              <Wind className="w-3.5 h-3.5 text-cyan-400" /> Annual Rainfall
            </span>
            <span className="text-sm font-bold text-neutral-100 font-mono">
              {rainfall !== undefined && rainfall !== null ? `${rainfall} mm` : '—'}
            </span>
          </div>

          <div className="w-full bg-[#0a140e] h-2 rounded-full overflow-hidden p-0.5 border border-[#1b3424]">
            <div
              className="h-full rounded-full bg-cyan-500 transition-all duration-500"
              style={{ width: `${rainfallPct}%` }}
            />
          </div>

          <div className="flex items-center justify-between text-[10px]">
            <span className="text-neutral-500 font-mono">&lt;400mm Arid</span>
            <span className="text-cyan-400 font-medium">
              {rainfall !== undefined && rainfall !== null
                ? rainfall < 500 ? 'Dryland Climate' : 'Moderate Precip.'
                : 'Awaiting precipitation'}
            </span>
            <span className="text-neutral-500 font-mono">1000mm+</span>
          </div>
        </div>

        {/* 3. Soil Moisture & pH Dual Card */}
        <div className="grid grid-cols-2 gap-2.5 text-xs">
          {/* Soil Moisture */}
          <div className="p-3 rounded-xl bg-[#13241b] border border-[#203a2c] space-y-1.5">
            <div className="flex items-center justify-between text-[11px] text-neutral-400">
              <span>Moisture</span>
              <Droplets className="w-3.5 h-3.5 text-blue-400" />
            </div>
            <div className="text-base font-bold text-neutral-100 font-mono">
              {moisture !== undefined && moisture !== null ? `${moisture}%` : '—'}
            </div>
            <div className="w-full bg-[#0a140e] h-1.5 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full transition-all duration-500"
                style={{ width: `${moisturePct}%` }}
              />
            </div>
            <span className="text-[10px] text-neutral-400 block">
              {moisture !== undefined && moisture !== null ? (moisture < 18 ? 'Moisture Deficit' : 'Sufficient') : 'Volumetric %'}
            </span>
          </div>

          {/* Soil pH */}
          <div className="p-3 rounded-xl bg-[#13241b] border border-[#203a2c] space-y-1.5">
            <div className="flex items-center justify-between text-[11px] text-neutral-400">
              <span>Soil pH</span>
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div className="text-base font-bold text-neutral-100 font-mono">
              {ph !== undefined && ph !== null ? ph : '—'}
            </div>
            <div className="w-full bg-[#0a140e] h-1.5 rounded-full overflow-hidden">
              <div
                className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                style={{ width: `${phPct}%` }}
              />
            </div>
            <span className="text-[10px] text-neutral-400 block">
              {ph !== undefined && ph !== null ? (ph > 7.5 ? 'Alkaline (>7.5)' : ph < 6.5 ? 'Acidic' : 'Optimal') : 'pH Scale'}
            </span>
          </div>
        </div>
      </div>

      {/* Contextual Attributes */}
      <div className="pt-2 border-t border-[#1d3326] space-y-2 text-xs">
        <div className="flex items-center justify-between py-1 border-b border-[#14261c]">
          <span className="text-neutral-400 flex items-center gap-1.5">
            <Compass className="w-3.5 h-3.5 text-emerald-500" /> Biome / Region:
          </span>
          <span className="text-neutral-200 font-medium capitalize truncate max-w-[140px] text-right">
            {region}
          </span>
        </div>

        <div className="flex items-center justify-between py-1 border-b border-[#14261c]">
          <span className="text-neutral-400 flex items-center gap-1.5">
            <Sprout className="w-3.5 h-3.5 text-amber-500" /> Primary Crop:
          </span>
          <span className="text-neutral-200 font-medium capitalize">
            {crop}
          </span>
        </div>

        <div className="flex items-center justify-between py-1">
          <span className="text-neutral-400 flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5 text-rose-400" /> Cropping System:
          </span>
          <span className="text-neutral-200 font-medium capitalize">
            {cropping}
          </span>
        </div>
      </div>

      {/* Ecological Vulnerability Diagnosis Indicator */}
      <div className={`p-3 rounded-xl border text-xs space-y-1 ${
        isHighRisk
          ? 'bg-amber-950/50 border-amber-800/60 text-amber-200'
          : 'bg-[#12251a] border-[#1e3e2c] text-neutral-300'
      }`}>
        <div className="flex items-center gap-1.5 font-semibold text-[11px]">
          {isHighRisk ? (
            <>
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              <span>Ecological Vulnerability: Elevated</span>
            </>
          ) : (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Ecological State Status</span>
            </>
          )}
        </div>
        <p className="text-[11px] opacity-85 leading-snug">
          {isHighRisk
            ? 'Compounding low rainfall and depleted organic carbon suppress microbial biomass and water holding capacity.'
            : 'Variables dynamically tracked across multi-metric causal reasoning graph.'}
        </p>
      </div>
    </div>
  );
};
