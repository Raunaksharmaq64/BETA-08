'use client';

import React, { useState } from 'react';
import {
  FileText,
  CheckCircle2,
  Sparkles,
  Download,
  Copy,
  Check,
  ShieldCheck,
  ArrowRight,
  Cpu,
  Layers,
} from 'lucide-react';

interface ResumeEvidenceMiniViewProps {
  onOpenFullSection: () => void;
}

export function ResumeEvidenceMiniView({ onOpenFullSection }: ResumeEvidenceMiniViewProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start pb-4">
      {/* Left 8 Cols: Candidate Snapshot & ATS Proof Breakdown */}
      <div className="lg:col-span-8 bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-5">
        {/* Header / Identity Snapshot */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="size-11 rounded-2xl bg-gradient-to-tr from-gray-900 to-gray-700 text-white font-extrabold flex items-center justify-center text-sm shadow-md">
              AM
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm sm:text-base font-bold text-[#171c23]">
                  Alex Mercer · Master Architecture Resume
                </h3>
                <span className="bg-emerald-50 text-emerald-700 border border-emerald-200/60 rounded-full px-2 py-0.5 text-[10px] font-bold">
                  94.8% ATS Verified
                </span>
              </div>
              <p className="text-xs text-[#5d5e63] mt-0.5">
                Lead Systems & Distributed Runtime Architect (12+ Years Experience)
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="bg-white border border-gray-200 rounded-full px-3 py-1.5 text-xs font-semibold text-gray-700 shadow-sm hover:bg-gray-50 transition-all flex items-center gap-1.5"
            >
              {copied ? <Check className="size-3.5 text-emerald-600" /> : <Copy className="size-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Text'}</span>
            </button>
            <button className="bg-black hover:bg-gray-800 text-white rounded-full px-3.5 py-1.5 text-xs font-semibold shadow-md transition-all flex items-center gap-1.5">
              <Download className="size-3.5" />
              <span>PDF</span>
            </button>
          </div>
        </div>

        {/* Executive Abstract */}
        <div className="bg-gray-50/80 border border-gray-200/70 rounded-xl p-3.5 text-xs text-gray-700 leading-relaxed font-sans">
          <span className="font-bold text-gray-900">Executive Summary: </span>
          Accomplished Distributed Systems Architect with 12+ years designing multi-region cloud infrastructures, bare-metal container runtimes, and real-time transaction fabrics handling 5.2M+ QPS. Proven track record leading core platform migrations, reducing multi-million dollar compute budgets by 34%, and driving zero-downtime microservice transitions across Fortune 100 engineering teams.
        </div>

        {/* ATS Scoring Metric Bars */}
        <div className="flex flex-col gap-2.5">
          <div className="text-[11px] font-bold text-gray-500 uppercase tracking-wider">
            Automated ATS Alignment Scores (12 Scored Evaluators)
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="bg-white border border-gray-200/80 rounded-xl p-3 flex flex-col gap-1.5 shadow-sm">
              <div className="flex justify-between items-center text-xs">
                <span className="font-semibold text-gray-700">Keyword Density</span>
                <span className="font-extrabold text-emerald-600">96%</span>
              </div>
              <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: '96%' }} />
              </div>
              <span className="text-[10px] text-gray-400">Raft, eBPF, Rust, K8s matched</span>
            </div>

            <div className="bg-white border border-gray-200/80 rounded-xl p-3 flex flex-col gap-1.5 shadow-sm">
              <div className="flex justify-between items-center text-xs">
                <span className="font-semibold text-gray-700">Experience Impact</span>
                <span className="font-extrabold text-teal-600">94%</span>
              </div>
              <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                <div className="bg-teal-500 h-full rounded-full" style={{ width: '94%' }} />
              </div>
              <span className="text-[10px] text-gray-400">High QPS & budget metrics</span>
            </div>

            <div className="bg-white border border-gray-200/80 rounded-xl p-3 flex flex-col gap-1.5 shadow-sm">
              <div className="flex justify-between items-center text-xs">
                <span className="font-semibold text-gray-700">ATS Formatting</span>
                <span className="font-extrabold text-indigo-600">95%</span>
              </div>
              <div className="w-full bg-gray-100 h-1.5 rounded-full overflow-hidden">
                <div className="bg-indigo-500 h-full rounded-full" style={{ width: '95%' }} />
              </div>
              <span className="text-[10px] text-gray-400">Single-column semantic parsing</span>
            </div>
          </div>
        </div>

        {/* Competencies Chips */}
        <div>
          <div className="text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-2">
            Verified Core Competencies:
          </div>
          <div className="flex flex-wrap gap-1.5">
            {[
              'Distributed Consensus (Raft/Paxos)',
              'Rust & C++20 Low-Latency',
              'eBPF Socket Filtering',
              'Multi-Region Kafka Streaming',
              'Kubernetes Operator Architecture',
              'Linux Kernel Performance Tuning',
              'High-Throughput Caching (Redis/XFetch)',
            ].map((skill) => (
              <span
                key={skill}
                className="text-xs bg-gray-100/90 hover:bg-gray-200/80 text-gray-800 border border-gray-200 px-2.5 py-1 rounded-lg transition-colors font-medium"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Right 4 Cols: ATS Cryptographic Verification & Deep Dive Trigger */}
      <div className="lg:col-span-4 bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-4">
        <div>
          <div className="text-[11px] font-bold uppercase tracking-wider text-gray-400">
            Resume Intelligence Suite
          </div>
          <h4 className="text-base font-bold text-[#171c23] mt-0.5">
            Evidence & Verification Pass
          </h4>
          <p className="text-xs text-gray-500 mt-0.5">
            Cryptographically signed proof generated from PDF source telemetry.
          </p>
        </div>

        {/* Cryptographic Proof Capsule */}
        <div className="bg-slate-900 text-white rounded-2xl p-4 flex flex-col gap-2.5 shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">
              SHA-256 ATS RECEIPT
            </span>
            <span className="bg-emerald-500/20 text-emerald-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-emerald-400/30">
              PASS
            </span>
          </div>
          <p className="font-mono text-[11px] text-gray-300 break-all leading-tight">
            e7a4b189c42ef99824c89a01f56a3e6209...
          </p>
          <div className="text-[11px] text-gray-400 pt-1.5 border-t border-white/10 flex items-center justify-between">
            <span>Model: GPT-4o + Claude 3.5 Sonnet</span>
            <span className="text-emerald-300 font-semibold">100% Parsed</span>
          </div>
        </div>

        {/* Summary Insights */}
        <div className="bg-emerald-50/70 border border-emerald-200/60 rounded-xl p-3 text-xs text-emerald-900 flex flex-col gap-1">
          <div className="font-bold flex items-center gap-1.5">
            <CheckCircle2 className="size-3.5 text-emerald-600" />
            <span>Optimal Headhunter Calibration</span>
          </div>
          <p className="text-[11px] text-emerald-800 leading-relaxed">
            Your profile matches the 99th percentile for Staff Infrastructure Engineer positions at top venture-backed AI labs.
          </p>
        </div>

        {/* Full Section Jump Button */}
        <button
          onClick={onOpenFullSection}
          className="w-full bg-black hover:bg-gray-800 text-white font-bold py-2.5 rounded-full text-xs shadow-md transition-all flex items-center justify-center gap-2 group mt-1"
        >
          <span>Open Full Resume Intelligence Suite</span>
          <ArrowRight className="size-3.5 group-hover:translate-x-0.5 transition-transform" />
        </button>
      </div>
    </div>
  );
}

