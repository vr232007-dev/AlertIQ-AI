import React, { useState } from 'react';
import { X, Search, Activity, Network } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export function FeatureModal({ isOpen, onClose, record }) {
  const [searchTerm, setSearchTerm] = useState('');

  if (!isOpen || !record) return null;

  const features = record.features || {};
  const featureEntries = Object.entries(features);

  const filteredFeatures = featureEntries.filter(([key]) =>
    key.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-navy-900 border border-navy-700 rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-navy-800 flex items-center justify-between bg-navy-850">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Network className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-semibold text-white">Flow Feature Inspector</h3>
                <StatusBadge type="prediction" value={record.predicted_class} />
              </div>
              <p className="text-xs text-slate-400">
                Destination Port: <span className="text-slate-200 font-mono">{record.destination_port}</span> | Attack Confidence: <span className="text-slate-200 font-mono">{Math.round(record.attack_probability * 100)}%</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-navy-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search bar */}
        <div className="p-4 border-b border-navy-800 bg-navy-900 flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search through all 78 network features (e.g., 'Port', 'Packet', 'Duration', 'IAT')..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-navy-950 border border-navy-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <span className="text-xs text-slate-400 whitespace-nowrap">
            Showing {filteredFeatures.length} of {featureEntries.length} features
          </span>
        </div>

        {/* Feature Grid */}
        <div className="p-6 overflow-y-auto flex-1">
          {filteredFeatures.length === 0 ? (
            <div className="text-center py-10 text-slate-400 text-xs">
              No features match "{searchTerm}"
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
              {filteredFeatures.map(([name, val]) => (
                <div
                  key={name}
                  className="bg-navy-950/70 border border-navy-800 rounded-lg p-2.5 hover:border-navy-700 transition-colors"
                >
                  <p className="text-[11px] font-medium text-slate-400 truncate mb-1" title={name}>
                    {name}
                  </p>
                  <p className="text-xs font-mono font-semibold text-cyan-300 truncate">
                    {typeof val === 'number' ? val.toLocaleString() : String(val)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-navy-800 bg-navy-850 flex items-center justify-between text-xs text-slate-400">
          <span>78 Network Features extracted from CIC-IDS2017 Dataset</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-navy-700 hover:bg-navy-600 text-white font-medium text-xs transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
