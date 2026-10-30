import React from "react";
import Link from "next/link";
import Navbar from "@/components/layout/Navbar";

export default function HomePage() {
  const features = [
    {
      title: "Canonical Opportunities",
      desc: "Browse and search verified career opportunities ingested from governed ATS feeds with complete provenance and un-fabricated salary numbers.",
      href: "/opportunities",
      badge: "Phase 5 Active",
      badgeColor: "bg-emerald-950 text-emerald-400 border-emerald-800",
      cta: "Explore Jobs &rarr;",
    },
    {
      title: "Job Source Framework",
      desc: "Manage and monitor external job sources (Greenhouse, Ashby, etc.) equipped with a 3-state circuit breaker, sliding-window rate limits, and policy gating.",
      href: "/sources",
      badge: "Phase 5 Active",
      badgeColor: "bg-emerald-950 text-emerald-400 border-emerald-800",
      cta: "Manage Sources &rarr;",
    },
    {
      title: "Resume Intelligence",
      desc: "Upload resumes, inspect extracted skills and evidence chunks, review candidate facts on the review workbench, and analyze ATS keyword match score.",
      href: "/resumes",
      badge: "Phase 4 Active",
      badgeColor: "bg-indigo-950 text-indigo-400 border-indigo-800",
      cta: "View Resumes &rarr;",
    },
    {
      title: "Candidate Profile & Privacy",
      desc: "Manage candidate skills, work experience, education credentials, career preferences, and execute GDPR/CCPA data rights (export & deletion).",
      href: "/profile",
      badge: "Phase 3 Active",
      badgeColor: "bg-blue-950 text-blue-400 border-blue-800",
      cta: "Candidate Profile &rarr;",
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-12">
        {/* Hero Section */}
        <div className="text-center space-y-4 max-w-3xl mx-auto">
          <div className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-indigo-950 text-indigo-300 border border-indigo-800">
            RIGHT FIT &bull; Hybrid Modular Career Intelligence
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white">
            AI-Powered Career Intelligence Platform
          </h1>
          <p className="text-base sm:text-lg text-slate-400 leading-relaxed">
            A production-ready platform featuring evidence-backed Resume Intelligence, governed ATS job feeds,
            and privacy-first candidate workflows.
          </p>
          <div className="flex flex-wrap justify-center gap-4 pt-4">
            <Link
              href="/opportunities"
              className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition-all"
            >
              Search Opportunities
            </Link>
            <Link
              href="/sources"
              className="px-6 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 font-semibold text-sm transition-all"
            >
              Job Source Registry
            </Link>
            <Link
              href="/login"
              className="px-6 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 font-semibold text-sm transition-all"
            >
              Sign In
            </Link>
          </div>
        </div>

        {/* Feature Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-8">
          {features.map((feat) => (
            <div
              key={feat.title}
              className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all shadow-xl flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-bold text-white">{feat.title}</h3>
                  <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${feat.badgeColor}`}>
                    {feat.badge}
                  </span>
                </div>
                <p className="text-sm text-slate-300 leading-relaxed">{feat.desc}</p>
              </div>

              <div className="pt-6 mt-4 border-t border-slate-800/80">
                <Link
                  href={feat.href}
                  className="text-sm font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  {feat.cta}
                </Link>
              </div>
            </div>
          ))}
        </div>

        {/* System Architecture & Status Card */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 text-xs text-slate-400 space-y-3">
          <div className="font-semibold text-slate-300 uppercase tracking-wider text-[11px]">
            Platform Infrastructure Endpoints
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-500 block">Core Backend API</span>
              <a href="http://localhost:8000" target="_blank" rel="noreferrer" className="text-indigo-400 font-mono">
                http://localhost:8000
              </a>
            </div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-500 block">FastAPI Swagger Docs</span>
              <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="text-indigo-400 font-mono">
                http://localhost:8000/docs
              </a>
            </div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-500 block">Next.js Web UI</span>
              <span className="text-emerald-400 font-mono">http://localhost:3000</span>
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        RIGHT FIT &bull; AI-Powered Career Intelligence Platform &bull; Phase 5 Complete
      </footer>
    </div>
  );
}

