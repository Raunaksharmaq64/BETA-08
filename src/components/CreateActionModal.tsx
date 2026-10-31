'use client';

import React, { useState } from 'react';
import { X, Plus, Sparkles, Check, Zap, Play } from 'lucide-react';

interface CreateActionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (title: string) => Promise<void>;
}

export function CreateActionModal({
  isOpen,
  onClose,
  onSubmit,
}: CreateActionModalProps) {
  const [title, setTitle] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const templates = [
    'Deep Architecture Synergy Audit on Cognition AI',
    'Real-time Scraping of Series A Founder Technical Pain Points',
    'Resume ATS Alignment against Frontier LLM Labs',
    '48h Interview Question Synthesis (Datadog & Vercel)',
  ];

  const handleApplyTemplate = (tmpl: string) => {
    setSelectedTemplate(tmpl);
    setTitle(tmpl);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    try {
      await onSubmit(title.trim());
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        setTitle('');
        setIsSubmitting(false);
        onClose();
      }, 1000);
    } catch {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-fade-in select-none">
      <div className="bg-white/95 backdrop-blur-xl border border-white/90 rounded-[32px] shadow-2xl w-full max-w-lg p-6 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 size-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-600 transition-colors"
        >
          <X className="size-4" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-2.5 mb-4">
          <div className="bg-black p-2 rounded-xl text-white">
            <Zap className="size-4.5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-[#171c23]">
              Launch New AI Pipeline Action
            </h3>
            <p className="text-xs text-gray-500">
              Run automated matching, scraping, or ATS tailoring jobs
            </p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="text-xs font-semibold text-gray-800 block mb-1.5">
              Action Title / Workflow Intent
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Run Deep ATS Optimization for Staff Systems roles..."
              className="w-full bg-gray-50 border border-gray-200 rounded-xl px-3.5 py-2.5 text-xs text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-black/10 focus:bg-white"
            />
          </div>

          {/* Quick Presets */}
          <div>
            <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider block mb-2">
              Recommended Presets
            </span>
            <div className="flex flex-col gap-1.5">
              {templates.map((tmpl) => (
                <button
                  type="button"
                  key={tmpl}
                  onClick={() => handleApplyTemplate(tmpl)}
                  className={`text-left text-xs p-2.5 rounded-xl border transition-all ${
                    selectedTemplate === tmpl
                      ? 'bg-black text-white border-black font-medium'
                      : 'bg-gray-50/80 border-gray-200/60 text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {tmpl}
                </button>
              ))}
            </div>
          </div>

          {/* Submit */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-gray-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs text-gray-600 hover:text-black"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !title.trim()}
              className="bg-black text-white text-xs font-semibold px-5 py-2.5 rounded-full hover:bg-gray-800 transition-colors flex items-center gap-1.5 disabled:opacity-50"
            >
              {success ? (
                <>
                  <Check className="size-3.5 text-emerald-400" />
                  <span>Workflow Dispatched!</span>
                </>
              ) : (
                <>
                  <Play className="size-3.5 fill-current" />
                  <span>Execute Workflow</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

