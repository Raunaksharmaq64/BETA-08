'use client';

import React from 'react';
import { X, CheckCircle2, TrendingUp, ShieldCheck, ArrowRight } from 'lucide-react';

interface ReportModalProps {
  isOpen: boolean;
  type: string;
  onClose: () => void;
}

export function ReportModal({ isOpen, type, onClose }: ReportModalProps) {
  if (!isOpen) return null;

  const getTitle = () => {
    switch (type) {
      case 'ats_proof':
        return 'Resume ATS Score Audit (94/100)';
      case 'crm':
        return 'Interview Pipeline Kanban Status';
      case 'opportunities':
        return 'Target Salary Range Alignment ($165k - $190k)';
      default:
        return 'System Executions Telemetry Report';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-fade-in select-none">
      <div className="bg-white/95 backdrop-blur-xl border border-white/90 rounded-[32px] shadow-2xl w-full max-w-xl p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 size-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-600 transition-colors"
        >
          <X className="size-4" />
        </button>

        <div className="flex items-center gap-2.5 mb-4">
          <div className="bg-emerald-100 p-2 rounded-xl text-emerald-800">
            <TrendingUp className="size-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-[#171c23]">{getTitle()}</h3>
            <p className="text-xs text-gray-500">Live intelligence report • Alex Mercer</p>
          </div>
        </div>

        {type === 'ats_proof' ? (
          <div className="space-y-3 text-xs">
            <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-100 text-emerald-950">
              <span className="font-bold text-sm block mb-1">94% Senior Architecture Parsing Accuracy</span>
              <p className="text-emerald-800">
                Validated against Greenhouse, Lever, and Workday ATS parsers. Skills parsed: Distributed Systems, Deterministic Runtimes, eBPF, Rust, Go.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-gray-50 p-2.5 rounded-xl border border-gray-100">
                <span className="text-gray-500 block text-[11px]">Hard Keyword Synergy</span>
                <span className="font-bold text-black text-sm">98.2%</span>
              </div>
              <div className="bg-gray-50 p-2.5 rounded-xl border border-gray-100">
                <span className="text-gray-500 block text-[11px]">Format / Parsing Density</span>
                <span className="font-bold text-black text-sm">0 Errors</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-3 text-xs">
            <div className="p-3 bg-blue-50 rounded-xl border border-blue-100 text-blue-950">
              <span className="font-bold text-sm block mb-1">Pipeline Performance: 340 Runs Completed</span>
              <p className="text-blue-800">
                Autonomous agent loops currently maintaining a 92.4% match precision across top-tier technical openings.
              </p>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="bg-gray-50 p-2.5 rounded-xl border border-gray-100">
                <span className="text-gray-500 block text-[11px]">Success Rate</span>
                <span className="font-bold text-black text-sm">99.1%</span>
              </div>
              <div className="bg-gray-50 p-2.5 rounded-xl border border-gray-100">
                <span className="text-gray-500 block text-[11px]">Avg Latency</span>
                <span className="font-bold text-black text-sm">1.8s</span>
              </div>
              <div className="bg-gray-50 p-2.5 rounded-xl border border-gray-100">
                <span className="text-gray-500 block text-[11px]">Active Models</span>
                <span className="font-bold text-black text-sm">12</span>
              </div>
            </div>
          </div>
        )}

        <div className="pt-4 mt-4 border-t border-gray-100 flex justify-end">
          <button
            onClick={onClose}
            className="bg-black text-white text-xs font-semibold px-5 py-2.5 rounded-full hover:bg-gray-800 transition-colors"
          >
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
}

