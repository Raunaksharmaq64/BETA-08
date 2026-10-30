"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient } from "../../../services/apiClient";

export default function VerifyEmailPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);

    try {
      const resp = await apiClient<{ message: string }>("/auth/verify-email", {
        method: "POST",
        body: JSON.stringify({ token }),
      });
      setMessage(resp.data.message);
      setTimeout(() => router.push("/profile"), 2500);
    } catch (err: any) {
      setError(err.message || "Email verification failed. Token may be expired.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-slate-100 px-4">
      <div className="max-w-md w-full bg-slate-800 p-8 rounded-xl shadow-lg border border-slate-700">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold tracking-tight text-white">Verify Your Email</h1>
          <p className="text-sm text-slate-400 mt-2">Enter the verification token from your confirmation email.</p>
        </div>

        {message && (
          <div className="mb-6 p-4 bg-emerald-950/80 border border-emerald-500/50 rounded-lg text-sm text-emerald-200">
            {message} Redirecting to your profile...
          </div>
        )}

        {error && (
          <div className="mb-6 p-3 bg-red-950/80 border border-red-500/50 rounded-lg text-sm text-red-200">
            {error}
          </div>
        )}

        <form onSubmit={handleVerify} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
              Verification Token
            </label>
            <input
              type="text"
              required
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Paste verification token here"
              className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium rounded-lg transition-colors focus:ring-2 focus:ring-indigo-400 focus:outline-none"
          >
            {loading ? "Verifying..." : "Verify Email"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-400">
          <Link href="/profile" className="text-indigo-400 hover:underline">
            Skip for now (Go to Profile)
          </Link>
        </div>
      </div>
    </div>
  );
}
