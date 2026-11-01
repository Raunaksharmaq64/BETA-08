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
    <nav className="flex border-b border-slate-800 mb-8 overflow-x-auto scrollbar-none gap-1 sm:gap-2 text-xs font-medium text-slate-400 -mx-4 px-4 sm:mx-0 sm:px-0" aria-label="Resume Sub-Navigation">
      {links.map((link) => {
        const isActive = pathname === link.href;
        return (
          <Link
            key={link.href}
            href={link.href}
            className={`pb-3 px-3 transition-colors border-b-2 whitespace-nowrap ${isActive
              ? "border-indigo-500 text-indigo-400 font-semibold"
              : "border-transparent hover:text-slate-200 hover:border-slate-700"
              }`}
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
