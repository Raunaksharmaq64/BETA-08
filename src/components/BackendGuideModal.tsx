'use client';

import React, { useState } from 'react';
import {
  X,
  CheckCircle2,
  Copy,
  PlugZap,
  Server,
  Check,
  RefreshCw,
} from 'lucide-react';
import { API_ENDPOINTS } from '@/services/endpoints';
import { IS_MOCK_MODE } from '@/services/apiClient';

interface BackendGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function BackendGuideModal({
  isOpen,
  onClose,
}: BackendGuideModalProps) {
  const [copied, setCopied] = useState(false);
  const [pingStatus, setPingStatus] = useState<string>('idle');

  if (!isOpen) return null;

  const envSample = `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCK_DATA=false`;

  const copyEnv = () => {
    navigator.clipboard.writeText(envSample);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const testPing = async () => {
    setPingStatus('testing');
    try {
      const url = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 1500);
      await fetch(`${url}/api/v1/health`, {
        signal: controller.signal,
        mode: 'no-cors',
      });
      clearTimeout(timeout);
      setPingStatus('online');
    } catch {
      setPingStatus('offline');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/40 backdrop-blur-sm animate-fade-in select-none">
      <div className="bg-white h-full w-full max-w-lg shadow-2xl p-6 overflow-y-auto flex flex-col justify-between border-l border-gray-200">
        <div className="flex flex-col gap-5">
          {/* Header */}
          <div className="flex items-center justify-between pb-3 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <div className="bg-amber-100 p-2 rounded-xl text-amber-800">
                <PlugZap className="size-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-[#171c23]">
                  Premade Backend Integration
                </h3>
                <p className="text-xs text-gray-500">
                  RightFit Frontend API Service Layer
                </p>
              </div>
            </div>

            <button
              onClick={onClose}
              className="size-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-600 transition-colors"
            >
              <X className="size-4" />
            </button>
          </div>

          {/* Current Status */}
          <div className="p-3.5 rounded-2xl bg-gray-50 border border-gray-200 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Server className="size-4.5 text-gray-600" />
              <div>
                <span className="text-xs font-semibold text-gray-800 block">
                  Mode:{' '}
                  {IS_MOCK_MODE ? (
                    <span className="text-amber-600">Modular Mock Layer</span>
                  ) : (
                    <span className="text-emerald-600">Live API</span>
                  )}
                </span>
                <span className="text-[11px] text-gray-500 font-mono">
                  {process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}
                </span>
              </div>
            </div>

            <button
              onClick={testPing}
              className="text-xs font-semibold px-3 py-1 rounded-full border border-gray-300 hover:bg-white flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className={`size-3 ${pingStatus === 'testing' ? 'animate-spin' : ''}`} />
              <span>
                {pingStatus === 'idle'
                  ? 'Ping'
                  : pingStatus === 'testing'
                  ? 'Checking...'
                  : pingStatus === 'online'
                  ? 'Online'
                  : 'Offline'}
              </span>
            </button>
          </div>

          {/* Env Toggle */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider">
                1. Point to your Backend (.env.local)
              </h4>
              <button
                onClick={copyEnv}
                className="text-xs font-medium text-gray-600 hover:text-black flex items-center gap-1"
              >
                {copied ? (
                  <>
                    <Check className="size-3 text-emerald-600" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="size-3" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
            <pre className="bg-[#181a1f] text-gray-200 text-xs p-3 rounded-xl font-mono overflow-x-auto">
              {envSample}
            </pre>
          </div>

          {/* Endpoints */}
          <div className="flex flex-col gap-2">
            <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider">
              2. Contract Endpoints Ready in Service Layer
            </h4>
            <div className="space-y-1.5 text-xs">
              <div className="p-2.5 bg-gray-50 rounded-xl border border-gray-100 flex items-center justify-between">
                <div>
                  <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-1.5 py-0.5 rounded mr-1.5">
                    GET
                  </span>
                  <code className="text-[#171c23] font-mono text-[11px]">
                    {API_ENDPOINTS.DASHBOARD_DATA}
                  </code>
                </div>
                <span className="text-gray-500 text-[10px]">Metrics & feeds</span>
              </div>

              <div className="p-2.5 bg-gray-50 rounded-xl border border-gray-100 flex items-center justify-between">
                <div>
                  <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-1.5 py-0.5 rounded mr-1.5">
                    GET
                  </span>
                  <code className="text-[#171c23] font-mono text-[11px]">
                    {API_ENDPOINTS.ACTIVE_WORKFLOWS}
                  </code>
                </div>
                <span className="text-gray-500 text-[10px]">Workflows query</span>
              </div>

              <div className="p-2.5 bg-gray-50 rounded-xl border border-gray-100 flex items-center justify-between">
                <div>
                  <span className="bg-blue-100 text-blue-800 text-[10px] font-bold px-1.5 py-0.5 rounded mr-1.5">
                    POST
                  </span>
                  <code className="text-[#171c23] font-mono text-[11px]">
                    {API_ENDPOINTS.RUN_WORKFLOW}
                  </code>
                </div>
                <span className="text-gray-500 text-[10px]">Trigger execution</span>
              </div>
            </div>
          </div>

          {/* Decoupling assurance */}
          <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-3.5 text-xs text-emerald-900 flex items-start gap-2">
            <CheckCircle2 className="size-4 text-emerald-600 shrink-0 mt-0.5" />
            <p className="leading-relaxed text-[11px]">
              No frontend code changes required when integrating. The UI calls <code>DashboardService</code>, which automatically switches between mock data and your HTTP endpoints.
            </p>
          </div>
        </div>

        <div className="pt-4 border-t border-gray-100 flex justify-end">
          <button
            onClick={onClose}
            className="bg-black text-white text-xs font-semibold px-5 py-2 rounded-full hover:bg-gray-800 transition-colors"
          >
            Close Guide
          </button>
        </div>
      </div>
    </div>
  );
}

