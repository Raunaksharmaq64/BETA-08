'use client';

import React, { useState } from 'react';
import {
  FileText,
  CheckCircle2,
  Download,
  Sparkles,
  ShieldCheck,
  Cpu,
  Layers,
  Copy,
  Check,
} from 'lucide-react';

export function ResumeIntelligenceSection() {
  const [activeTab, setActiveTab] = useState<'master' | 'tailored' | 'ats_audit'>('master');
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col gap-6 w-full select-none">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 w-full">
        <div>
          <h2 className="text-[#171c23] text-2xl sm:text-[26px] font-bold tracking-tight">
            Resume Intelligence & ATS Proof Engine
          </h2>
          <p className="text-[#5d5e63] text-xs max-w-lg mt-0.5">
            Automated semantic parsing, ATS verification, and tailored evidence mapping for Alex Mercer.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleCopy}
            className="bg-white border border-gray-200 rounded-full px-3.5 py-1.5 text-xs font-semibold text-gray-800 shadow-sm hover:bg-gray-50 transition-all flex items-center gap-1.5"
          >
            {copied ? <Check className="size-3.5 text-emerald-600" /> : <Copy className="size-3.5" />}
            <span>{copied ? 'Copied Markdown' : 'Copy Text'}</span>
          </button>
          <button className="bg-black text-white rounded-full px-4 py-1.5 text-xs font-semibold shadow-md hover:bg-gray-800 transition-all flex items-center gap-1.5">
            <Download className="size-3.5" />
            <span>Download Verified PDF</span>
          </button>
        </div>
      </div>

      {/* 4 Bento Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="backdrop-blur-[14px] bg-[rgba(255,255,255,0.75)] border border-white rounded-2xl p-4 shadow-sm flex flex-col justify-between">
          <span className="text-[11px] font-medium text-gray-500 uppercase tracking-wider">ATS READABILITY</span>
          <div className="my-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-black">94%</span>
            <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full">Top 2%</span>
          </div>
          <span className="text-[11px] text-gray-500">Greenhouse & Lever Compliant</span>
        </div>

        <div className="backdrop-blur-[14px] bg-[rgba(255,255,255,0.75)] border border-white rounded-2xl p-4 shadow-sm flex flex-col justify-between">
          <span className="text-[11px] font-medium text-gray-500 uppercase tracking-wider">VERIFIED CORE SKILLS</span>
          <div className="my-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-black">28</span>
            <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">Evidence Backed</span>
          </div>
          <span className="text-[11px] text-gray-500">eBPF, Rust, Concurrency, Kafka</span>
        </div>

        <div className="backdrop-blur-[14px] bg-[rgba(255,255,255,0.75)] border border-white rounded-2xl p-4 shadow-sm flex flex-col justify-between">
          <span className="text-[11px] font-medium text-gray-500 uppercase tracking-wider">TARGET ROLE FIT</span>
          <div className="my-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-black">Staff/Principal</span>
          </div>
          <span className="text-[11px] text-gray-500">Distributed Runtime Focus</span>
        </div>

        <div className="backdrop-blur-[14px] bg-[rgba(255,255,255,0.75)] border border-white rounded-2xl p-4 shadow-sm flex flex-col justify-between">
          <span className="text-[11px] font-medium text-gray-500 uppercase tracking-wider">TAILORED VARIANTS</span>
          <div className="my-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold text-black">4 Active</span>
            <span className="text-xs font-bold text-purple-600 bg-purple-50 px-2 py-0.5 rounded-full">Synced</span>
          </div>
          <span className="text-[11px] text-gray-500">Cognition, Vercel, Datadog</span>
        </div>
      </div>

      {/* Main Split: Left Resume Dossier & Right ATS Evidence Checker */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left: Master Architecture Resume (8 cols) */}
        <div className="lg:col-span-8 backdrop-blur-[14px] bg-[rgba(255,255,255,0.85)] border border-white rounded-[28px] p-6 shadow-sm flex flex-col gap-5 text-gray-900">
          {/* Resume Header */}
          <div className="border-b border-gray-200 pb-4">
            <h3 className="text-2xl font-bold text-black">Alex Mercer</h3>
            <p className="text-sm font-semibold text-gray-700 mt-0.5">
              Principal Systems & Distributed Runtime Architect
            </p>
            <p className="text-xs text-gray-500 mt-1">
              San Francisco, CA • alex.mercer@careerintel.io • github.com/alex-mercer-systems
            </p>
          </div>

          {/* Professional Summary (verbatim from Figma 5:3) */}
          <div className="flex flex-col gap-1.5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Professional Summary
            </h4>
            <p className="text-xs sm:text-[13px] text-gray-800 leading-relaxed bg-gray-50/70 p-3.5 rounded-2xl border border-gray-100">
              Accomplished Distributed Systems Architect with 12+ years designing multi-region cloud infrastructures, bare-metal container runtimes, and real-time transaction fabrics handling 5.2M+ QPS. Proven track record leading core platform migrations, reducing multi-million dollar compute budgets by 34%, and driving zero-downtime microservice transitions across Fortune 100 engineering teams.
            </p>
          </div>

          {/* Core Architectural Competencies */}
          <div className="flex flex-col gap-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Core Competencies & Verified Technical Skills
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              <div className="p-3 bg-gray-50/70 rounded-xl border border-gray-100">
                <span className="text-xs font-bold text-black block mb-1">Runtimes & Isolation</span>
                <p className="text-[11px] text-gray-600">eBPF, V8 Isolates, Linux Namespaces, cgroups v2, WASM, WebAssembly micro-sandboxing</p>
              </div>
              <div className="p-3 bg-gray-50/70 rounded-xl border border-gray-100">
                <span className="text-xs font-bold text-black block mb-1">Distributed Fabrics</span>
                <p className="text-[11px] text-gray-600">Raft, Paxos, Kafka, gRPC, lockless ring buffers, CQRS, multi-region database replication</p>
              </div>
              <div className="p-3 bg-gray-50/70 rounded-xl border border-gray-100">
                <span className="text-xs font-bold text-black block mb-1">Scale & Infrastructure</span>
                <p className="text-[11px] text-gray-600">Kubernetes Operators, Terraform, Go, Rust, C++, AWS Graviton, GPU inference scheduling</p>
              </div>
            </div>
          </div>

          {/* Experience Highlights */}
          <div className="flex flex-col gap-3 pt-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500">
              Key Architecture Experience
            </h4>

            <div className="border-l-2 border-black pl-3.5 py-1 flex flex-col gap-1">
              <div className="flex justify-between items-baseline">
                <span className="font-bold text-sm text-black">Staff Infrastructure Architect • CloudScale Systems</span>
                <span className="text-xs text-gray-500 font-mono">2021 — Present</span>
              </div>
              <p className="text-xs text-gray-700">
                • Architected multi-tenant code execution engine utilizing deterministic sandboxing, reducing p99 latency from 420ms to 28ms under 250k concurrent tenant load.
              </p>
              <p className="text-xs text-gray-700">
                • Directed migration of 14,000 node Kubernetes cluster to ARM64 architecture, achieving $2.4M annualized cloud infrastructure savings.
              </p>
            </div>

            <div className="border-l-2 border-gray-300 pl-3.5 py-1 flex flex-col gap-1">
              <div className="flex justify-between items-baseline">
                <span className="font-bold text-sm text-black">Lead Platform Engineer • DataMesh Core</span>
                <span className="text-xs text-gray-500 font-mono">2017 — 2021</span>
              </div>
              <p className="text-xs text-gray-700">
                • Built distributed logging ingestion service processing 5.2M QPS with zero data loss using memory-mapped ring buffers and zero-copy networking.
              </p>
            </div>
          </div>
        </div>

        {/* Right: ATS Verification & Semantic Match Audit (4 cols) */}
        <div className="lg:col-span-4 backdrop-blur-[14px] bg-[rgba(255,255,255,0.85)] border border-white rounded-[28px] p-5 shadow-sm flex flex-col gap-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="size-4 text-emerald-600" />
            <h3 className="font-bold text-sm text-black">ATS Proof & Parser Telemetry</h3>
          </div>

          <div className="space-y-2.5 text-xs">
            <div className="p-3 bg-emerald-50 rounded-2xl border border-emerald-100">
              <div className="flex justify-between font-bold text-emerald-950 mb-1">
                <span>Greenhouse ATS Parsing</span>
                <span>Pass (98.4%)</span>
              </div>
              <p className="text-emerald-800 text-[11px]">
                Zero format errors detected. All employment ranges, skills, and titles extract with 100% field accuracy.
              </p>
            </div>

            <div className="p-3 bg-blue-50 rounded-2xl border border-blue-100">
              <div className="flex justify-between font-bold text-blue-950 mb-1">
                <span>Workday Semantic Scanner</span>
                <span>Pass (96.2%)</span>
              </div>
              <p className="text-blue-800 text-[11px]">
                High synergy on "Distributed Runtimes", "eBPF", and "Principal Architecture" keywords.
              </p>
            </div>
          </div>

          {/* Tailored Version Selector */}
          <div className="pt-3 border-t border-gray-100 flex flex-col gap-2">
            <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider">
              Role-Tailored Resumes (Auto-Generated)
            </span>

            <div className="p-3 rounded-2xl bg-gray-50 border border-gray-200/80 flex items-center justify-between">
              <div>
                <span className="font-bold text-black text-xs block">Cognition AI Tailored</span>
                <span className="text-[10px] text-gray-500">Emphasis: Large-scale synthesis runners</span>
              </div>
              <span className="bg-black text-white text-[10px] font-bold px-2 py-0.5 rounded-full">98% Fit</span>
            </div>

            <div className="p-3 rounded-2xl bg-gray-50 border border-gray-200/80 flex items-center justify-between">
              <div>
                <span className="font-bold text-black text-xs block">Vercel Edge Labs Tailored</span>
                <span className="text-[10px] text-gray-500">Emphasis: V8 Isolates & cold starts</span>
              </div>
              <span className="bg-black text-white text-[10px] font-bold px-2 py-0.5 rounded-full">95% Fit</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

