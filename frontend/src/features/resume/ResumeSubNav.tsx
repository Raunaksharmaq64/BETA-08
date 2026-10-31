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
    { label: "Status & Pipeline", href: `/resumes/${resumeId}/status` },
    { label: "Extraction & Evidence", href: `/resumes/${resumeId}/analysis` },
    { label: "Review Workbench", href: `/resumes/${resumeId}/review` },
    { label: "ATS & Job Matcher", href: `/resumes/${resumeId}/ats` },
    { label: "AI Suggestions & Rewrites", href: `/resumes/${resumeId}/suggestions` },
    { label: "Versions", href: `/resumes/${resumeId}/versions` },
  ];

  return (
    <div className="flex border-b border-slate-800 mb-8 overflow-x-auto gap-2 text-xs font-medium text-slate-400">
      {links.map((link) => {
        const isActive = pathname === link.href;
        return (
          <Link
            key={link.href}
            href={link.href}
            className={`pb-3 px-3 transition-colors border-b-2 whitespace-nowrap ${
              isActive
                ? "border-indigo-500 text-indigo-400 font-semibold"
                : "border-transparent hover:text-slate-200 hover:border-slate-700"
            }`}
          >
            {link.label}
          </Link>
        );
      })}
    </div>
  );
}
