"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

interface ResumeSubNavProps {
  resumeId: string;
}

export function ResumeSubNav({ resumeId }: ResumeSubNavProps) {
  const pathname = usePathname();

  const links = [
    { label: "📋 Resume Profile & Skills", href: `/resumes/${resumeId}/analysis` },
    { label: "🎯 ATS Score & Job Optimizer", href: `/resumes/${resumeId}/ats` },
  ];

  return (
    <nav className="flex items-center gap-2 mb-8 overflow-x-auto no-scrollbar py-1" aria-label="Resume Sub-Navigation">
      {links.map((link) => {
        const isActive = pathname === link.href;
        return (
          <Link
            key={link.href}
            href={link.href}
            className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all whitespace-nowrap ${
              isActive
                ? "neo-inset text-indigo-700 font-black border border-slate-300 shadow-inner scale-[1.02]"
                : "neo-pill text-slate-800 hover:text-indigo-600 font-bold"
            }`}
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
