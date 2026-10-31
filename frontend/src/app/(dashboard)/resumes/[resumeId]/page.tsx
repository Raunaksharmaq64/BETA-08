"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";

export default function ResumeRootPage() {
  const params = useParams();
  const router = useRouter();
  const resumeId = params?.resumeId as string;

  useEffect(() => {
    if (resumeId) {
      router.replace(`/resumes/${resumeId}/review`);
    }
  }, [resumeId, router]);

  return (
    <div className="flex items-center justify-center min-h-[50vh] text-slate-400">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mr-3"></div>
      <span>Redirecting to resume review workbench...</span>
    </div>
  );
}

