'use client';

import React, { useState, useRef } from 'react';
import {
  X, Code2, Play, Sparkles, Upload, FileText, Sliders, CheckCircle2,
  AlertCircle, Sprout, Droplets, Wind, Activity, Compass, MapPin
} from 'lucide-react';
import { analyzeEnvironmentJson } from '../lib/api';
import { ChatResponse } from '../lib/types';

interface JsonInputModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (data: ChatResponse) => void;
}

const PRESETS = {
  semi_arid_wheat: {
    name: 'Scenario 1: Semi-Arid Wheat (Thar Belt)',
    data: {
      soil_ph: 7.8,
      organic_carbon: 0.3,
      moisture: 15.0,
      rainfall: 450.0,
      temperature: 32.0,
      crop: 'wheat',
      land_use: 'monoculture',
      cropping_system: 'monoculture',
      region: 'semi-arid',
      country: 'India',
      latitude: 26.9124,
      longitude: 75.7873
    }
  },
  intensive_cotton: {
    name: 'Intensive Cotton with High Pesticide Pressure',
    data: {
      soil_ph: 8.1,
      organic_carbon: 0.38,
      moisture: 18.0,
      rainfall: 620.0,
      temperature: 34.0,
      crop: 'cotton',
      land_use: 'cropland',
      cropping_system: 'monoculture',
      pesticide_pressure: 'high',
      region: 'semi-arid plateau',
      country: 'India'
    }
  },
  degraded_rice: {
    name: 'Degraded Cereal Basin (Low Microbial Diversity)',
    data: {
      soil_ph: 7.9,
      organic_carbon: 0.35,
      moisture: 22.0,
      rainfall: 550.0,
      temperature: 30.0,
      crop: 'rice',
      land_use: 'cropland',
      cropping_system: 'monoculture',
      region: 'alluvial plains',
      country: 'India'
    }
  }
};

export const JsonInputModal: React.FC<JsonInputModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [activeMode, setActiveMode] = useState<'visual' | 'json'>('visual');
  const [formData, setFormData] = useState(PRESETS.semi_arid_wheat.data);
  const [jsonText, setJsonText] = useState(JSON.stringify(PRESETS.semi_arid_wheat.data, null, 2));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  // Sync form to JSON
  const updateFormField = (key: string, value: any) => {
    const updated = { ...formData, [key]: value };
    setFormData(updated);
    setJsonText(JSON.stringify(updated, null, 2));
  };

  // Sync JSON to form
  const handleJsonChange = (text: string) => {
    setJsonText(text);
    try {
      const parsed = JSON.parse(text);
      setFormData(parsed);
      setError(null);
    } catch (e: any) {
      // Keep typing allowed
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const content = event.target?.result as string;
        const parsed = JSON.parse(content);
        setFormData(parsed);
        setJsonText(JSON.stringify(parsed, null, 2));
        setError(null);
      } catch (err: any) {
        setError('Uploaded file is not valid JSON');
      }
    };
    reader.readAsText(file);
  };

  const loadPreset = (presetKey: keyof typeof PRESETS) => {
    const preset = PRESETS[presetKey];
    setFormData(preset.data);
    setJsonText(JSON.stringify(preset.data, null, 2));
    setError(null);
  };

  const handleSubmit = async () => {
    setError(null);
    try {
      const payload = activeMode === 'visual' ? formData : JSON.parse(jsonText);
      setLoading(true);
      const res = await analyzeEnvironmentJson(payload);
      onSuccess(res);
      onClose();
    } catch (e: any) {
      setError(e.message || 'Invalid environmental telemetry format');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-[#0b1510] border border-[#1d3827] rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-5 max-h-[92vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#1b3424] shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-emerald-950/80 border border-emerald-800/80 text-emerald-400">
              <Code2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-neutral-100 flex items-center gap-2">
                Structured Environmental Telemetry Ingestion
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-900/60 text-emerald-300 font-mono border border-emerald-700/40">
                  POST /api/environment/analyze
                </span>
              </h3>
              <p className="text-xs text-neutral-400">
                Directly inject soil, climate, and agroecological variables into the multi-metric causal reasoning engine.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-neutral-400 hover:text-neutral-200 rounded-lg hover:bg-[#152a1d] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Mode Switcher & Presets */}
        <div className="flex flex-wrap items-center justify-between gap-2 shrink-0">
          <div className="flex items-center gap-1 bg-[#102016] p-1 rounded-xl border border-[#1b3624]">
            <button
              onClick={() => setActiveMode('visual')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeMode === 'visual'
                  ? 'bg-emerald-700 text-white shadow'
                  : 'text-neutral-400 hover:text-neutral-200'
              }`}
            >
              <Sliders className="w-3.5 h-3.5" />
              Visual Parameter Form
            </button>
            <button
              onClick={() => setActiveMode('json')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeMode === 'json'
                  ? 'bg-emerald-700 text-white shadow'
                  : 'text-neutral-400 hover:text-neutral-200'
              }`}
            >
              <Code2 className="w-3.5 h-3.5" />
              Raw JSON Editor
            </button>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".json"
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="px-3 py-1.5 rounded-lg bg-[#14261c] border border-[#22402f] hover:border-emerald-500/60 text-xs font-medium text-emerald-300 flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <Upload className="w-3.5 h-3.5" />
              Upload .json File
            </button>
          </div>
        </div>

        {/* Quick Presets Bar */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs shrink-0">
          <span className="text-neutral-500 text-[11px] font-semibold uppercase shrink-0">Presets:</span>
          {Object.entries(PRESETS).map(([key, val]) => (
            <button
              key={key}
              onClick={() => loadPreset(key as any)}
              className="px-2.5 py-1 rounded-md bg-[#112017] border border-[#1c3928] text-neutral-300 hover:text-emerald-300 hover:border-emerald-600/60 text-[11px] shrink-0 transition-colors"
            >
              {val.name.split(':')[0]}
            </button>
          ))}
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-rose-950/70 border border-rose-800 text-rose-300 text-xs flex items-center gap-2 shrink-0">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        {/* Main Content Area */}
        <div className="flex-1 overflow-y-auto pr-1">
          {activeMode === 'visual' ? (
            <div className="space-y-4">
              {/* Soil Health Section */}
              <div className="p-4 rounded-xl bg-[#0f1d15] border border-[#1d3927] space-y-3">
                <div className="flex items-center justify-between text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                  <span className="flex items-center gap-1.5">
                    <Sprout className="w-4 h-4" /> 1. Soil Health Variables
                  </span>
                  <span className="text-[11px] text-neutral-400 font-normal">Trophic foundation</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="text-[11px] text-neutral-400 block mb-1">
                      Soil pH (3.5 - 10.0)
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      value={formData.soil_ph ?? ''}
                      onChange={(e) => updateFormField('soil_ph', parseFloat(e.target.value) || null)}
                      className="w-full p-2 rounded-lg bg-[#09120c] border border-[#1f3b29] text-xs text-neutral-100 font-mono focus:outline-none focus:border-emerald-500"
                    />
                    <span className="text-[10px] text-neutral-500 mt-1 block">
                      {formData.soil_ph ? (formData.soil_ph > 7.5 ? 'Alkaline' : formData.soil_ph < 6.5 ? 'Acidic' : 'Neutral') : '—'}
                    </span>
                  </div>

                  <div>
                    <label className="text-[11px] text-neutral-400 block mb-1">
                      Organic Carbon (SOC %)
                    </label>
                    <input
                      type="number"
                      step="0.05"
                      value={formData.organic_carbon ?? ''}
                      onChange={(e) => updateFormField('organic_carbon', parseFloat(e.target.value) || null)}
                      className="w-full p-2 rounded-lg bg-[#09120c] border border-[#1f3b29] text-xs text-emerald-300 font-mono font-bold focus:outline-none focus:border-emerald-500"
                    />
                    <span className={`text-[10px] mt-1 block font-medium ${formData.organic_carbon < 0.5 ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {formData.organic_carbon < 0.5 ? 'Critical Deficit (<0.5%)' : 'Adequate'}
                    </span>
                  </div>

                  <div>
                    <label className="text-[11px] text-neutral-400 block mb-1">
                      Soil Moisture (%)
                    </label>
                    <input
                      type="number"
                      step="1"
                      value={formData.moisture ?? ''}
                      onChange={(e) => updateFormField('moisture', parseFloat(e.target.value) || null)}
                      className="w-full p-2 rounded-lg bg-[#09120c] border border-[#1f3b29] text-xs text-neutral-100 font-mono focus:outline-none focus:border-emerald-500"
                    />
                    <span className="text-[10px] text-neutral-500 mt-1 block">
                      Volumetric water content
                    </span>
                  </div>
                </div>
              </div>

              {/* Climate & Hydrology */}
              <div className="p-4 rounded-xl bg-[#0f1d15] border border-[#1d3927] space-y-3">
                <div className="flex items-center justify-between text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                  <span className="flex items-center gap-1.5">
                    <Wind className="w-4 h-4" /> 2. Climate & Hydrological Drivers
                  </span>
                  <span className="text-[11px] text-neutral-400 font-normal">Precipitation & heat stress</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="text-[11px] text-neutral-400 block mb-1">
                      Annual Rainfall (mm)
                    </label>
                    <input
                      type="number"
                      step="10"
                      value={formData.rainfall ?? ''}
                      onChange={(e) => updateFormField('rainfall', parseFloat(e.target.value) || null)}
                      className="w-full p-2 rounded-lg bg-[#09120c] border border-[#1f3b29] text-xs text-neutral-100 font-mono focus:outline-none focus:border-emerald-500"
                    />
                    <span className={`text-[10px] mt-1 block ${formData.rainfall < 500 ? 'text-amber-400' : 'text-neutral-400'}`}>
                      {formData.rainfall < 500 ? 'Dryland / Drought-vulnerable (<500mm)' : 'Sufficient Rainfall'}
                    </span>
                  </div>

                  <div>
                    <label className="text-[11px] text-neutral-400 block mb-1">
                      Mean Temperature (°C)
                    </label>
                    <input
                      type="number"
                      step="1"
                      value={formData.temperature ?? ''}
                      onChange={(e) => updateFormField('temperature', parseFloat(e.target.value) || null)}
                      className="w-full p-2 rounded-lg bg-[#09120c] border border-[#1f3b29] text-xs text-neutral-100 font-mono focus:outline-none focus:border-emerald-500"
                    />
                    <span className="text-[10px] text-neutral-500 mt-1 block">
                      Surface thermal stress indicator
                    </span>
                  </div>
                </div>
              </div>

              {/* Land Use & Cropping System */}
              <div className="p-4 rounded-xl bg-[#0f1d15] border border-[#1d3927] space-y-3">
                <div className="flex items-center justify-between text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                  <span className="flex items-center gap-1.5">
                    <Compass className="w-4 h-4" /> 3. Land Use & Cropping Structure
                  </span>
                  <span className="text-[11px] text-neutral-400 font-normal">Crop species & management</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="text-[11px] text-neutral-400 block mb-1">
                      Primary Crop
                    </label>
                    <select
                      value={formData.crop || 'wheat'}
                      onChange={(e) => updateFormField('crop', e.target.value)}
                      className="w-full p-2 rounded-lg bg-[#09120c] border border-[#1f3b29] text-xs text-neutral-100 focus:outline-none focus:border-emerald-500 capitalize"
                    >
                      <option value="wheat">Wheat</option>
                      <option value="rice">Rice</option>
                      <option value="cotton">Cotton</option>
                      <option value="maize">Maize / Corn</option>
                      <option value="soybean">Soybean</option>
                      <option value="millet">Millet / Sorghum</option>
                      <option value="pulses">Pulses / Chickpea</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] text-neutral-400 block mb-1">
                      Cropping Pattern
                    </label>
                    <select
                      value={formData.cropping_system || 'monoculture'}
                      onChange={(e) => {
                        updateFormField('cropping_system', e.target.value);
                        updateFormField('land_use', e.target.value === 'monoculture' ? 'monoculture' : 'cropland');
                      }}
                      className="w-full p-2 rounded-lg bg-[#09120c] border border-[#1f3b29] text-xs text-neutral-100 focus:outline-none focus:border-emerald-500 capitalize"
                    >
                      <option value="monoculture">Continuous Monoculture</option>
                      <option value="crop_rotation">Crop Rotation</option>
                      <option value="intercropping">Intercropping</option>
                      <option value="agroforestry">Agroforestry / Silvoarable</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-[11px] text-neutral-400 block mb-1">
                      Biogeographic Region
                    </label>
                    <input
                      type="text"
                      value={formData.region || ''}
                      onChange={(e) => updateFormField('region', e.target.value)}
                      className="w-full p-2 rounded-lg bg-[#09120c] border border-[#1f3b29] text-xs text-neutral-100 focus:outline-none focus:border-emerald-500 capitalize"
                    />
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-neutral-400 pb-1">
                <span>Direct JSON Payload (`POST /api/environment/analyze`):</span>
                <span className="font-mono text-[11px] text-emerald-400">Strict Schema Validated</span>
              </div>
              <textarea
                value={jsonText}
                onChange={(e) => handleJsonChange(e.target.value)}
                rows={12}
                className="w-full p-3.5 rounded-xl bg-[#070e0a] border border-[#1f3c2b] text-emerald-300 font-mono text-xs focus:outline-none focus:border-emerald-500 leading-relaxed shadow-inner"
              />
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="flex justify-between items-center pt-3 border-t border-[#1b3424] shrink-0">
          <div className="text-[11px] text-neutral-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Connects ≥3 variables with RAG literature verification</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-[#14261c] hover:bg-[#1a3325] text-neutral-300 text-xs font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="px-5 py-2 rounded-xl bg-emerald-700 hover:bg-emerald-600 disabled:opacity-50 text-white font-medium text-xs flex items-center gap-2 transition-all shadow-lg hover:shadow-emerald-900/40"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              {loading ? 'Analyzing Causal Graph...' : 'Execute Diagnostic'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
