"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function SavedJobsPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/saved-opportunities");
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-[60vh] text-slate-400">
      <p className="text-sm">Redirecting to Unified Saved Bookmarks...</p>
    </div>
  );
}
