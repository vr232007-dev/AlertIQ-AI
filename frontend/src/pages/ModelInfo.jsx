import React, { useState } from 'react';
import { Cpu, Database, CheckCircle2, Search, Layers, FileCode } from 'lucide-react';

export function ModelInfo({ modelInfo }) {
  const [searchTerm, setSearchTerm] = useState('');

  const features = modelInfo?.features || [];
  const filteredFeatures = features.filter(f =>
    f.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Specifications Card */}
      <div className="bg-navy-900 border border-navy-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">Machine Learning Model Architecture</h3>
            <p className="text-xs text-slate-400">Scikit-learn trained intrusion classification pipeline</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-navy-950/70 border border-navy-800">
            <span className="text-slate-400 block mb-1">Model Type</span>
            <span className="font-semibold text-white">Random Forest (Pipeline)</span>
          </div>

          <div className="p-3 rounded-lg bg-navy-950/70 border border-navy-800">
            <span className="text-slate-400 block mb-1">Training Dataset</span>
            <span className="font-semibold text-cyan-300">CIC-IDS2017 Flows</span>
          </div>

          <div className="p-3 rounded-lg bg-navy-950/70 border border-navy-800">
            <span className="text-slate-400 block mb-1">Feature Dimension</span>
            <span className="font-mono font-semibold text-emerald-400">78 Input Features</span>
          </div>

          <div className="p-3 rounded-lg bg-navy-950/70 border border-navy-800">
            <span className="text-slate-400 block mb-1">Model Version</span>
            <span className="font-mono font-semibold text-amber-300">v{modelInfo?.model_version || '1.0.0'}</span>
          </div>
        </div>

        <div className="p-4 rounded-lg bg-navy-950/50 border border-navy-800 text-xs text-slate-300 leading-relaxed">
          <p className="font-semibold text-slate-200 mb-1">Pipeline Processing Details:</p>
          AlertIQ AI utilizes a two-stage Scikit-learn Pipeline. Incoming flows are first passed through a <code className="text-cyan-300 bg-navy-900 px-1 py-0.5 rounded">SimpleImputer(strategy='median')</code> to gracefully substitute missing or zero-division values, followed by a 100-estimator <code className="text-cyan-300 bg-navy-900 px-1 py-0.5 rounded">RandomForestClassifier</code> with balanced class weighting. Predictions yield calibrated class probabilities for real-time triage.
        </div>
      </div>

      {/* 78 Features Reference List */}
      <div className="bg-navy-900 border border-navy-800 rounded-xl p-5 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <h4 className="text-sm font-semibold text-white">78 CIC-IDS2017 Feature Registry</h4>
            <p className="text-xs text-slate-400">All required network flow fields validated during CSV upload and single-flow inference</p>
          </div>

          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search features (e.g. 'Packets', 'IAT')..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-navy-950 border border-navy-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-[460px] overflow-y-auto p-1">
          {filteredFeatures.map((feat, idx) => (
            <div
              key={feat}
              className="p-2 rounded bg-navy-950 border border-navy-800 text-xs flex items-center justify-between hover:border-navy-700 transition-colors"
            >
              <span className="font-mono text-slate-400 text-[11px] truncate" title={feat}>
                {feat}
              </span>
              <span className="text-[10px] font-mono text-cyan-400 bg-navy-900 px-1.5 py-0.5 rounded border border-navy-800">
                #{idx + 1}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
