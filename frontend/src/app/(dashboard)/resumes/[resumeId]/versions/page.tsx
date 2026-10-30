"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiClient } from "../../../../../services/apiClient";

interface ResumeVersion {
  id: string;
  resume_id: string;
  version_number: number;
  version_label: string;
  original_filename: string;
  file_type: string;
  file_size_bytes: number;
  parsing_status: string;
  error_message?: string;
  is_active: boolean;
  uploaded_at: string;
  parsed_at?: string;
}

export default function ResumeVersionsPage() {
  const params = useParams();
  const resumeId = params?.resumeId as string;

  const [versions, setVersions] = useState<ResumeVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [newLabel, setNewLabel] = useState("");
  const [newFile, setNewFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchVersions = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.get<ResumeVersion[]>(`/api/v1/resumes/${resumeId}/versions`);
      if (res.success && res.data) {
        setVersions(res.data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load resume versions.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (resumeId) {
      fetchVersions();
    }
  }, [resumeId]);

  const handleSetActive = async (versionId: string) => {
    try {
      setError(null);
      await apiClient.patch(`/api/v1/resumes/${resumeId}/active-version?version_id=${versionId}`);
      setSuccess("Active version updated successfully.");
      fetchVersions();
    } catch (err: any) {
      setError(err.message || "Failed to update active version.");
    }
  };

  const handleUploadVersion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFile) {
      setError("Please select a file to upload.");
      return;
    }

    try {
      setUploading(true);
      setError(null);
      setSuccess(null);

      const formData = new FormData();
      formData.append("file", newFile);
      if (newLabel) {
        formData.append("version_label", newLabel);
      }

      const res = await apiClient.postForm(`/api/v1/resumes/${resumeId}/versions`, formData);
      if (res.success) {
        setSuccess("New version uploaded successfully!");
        setNewFile(null);
        setNewLabel("");
        fetchVersions();
      }
    } catch (err: any) {
      setError(err.message || "Failed to upload new version.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8 pb-6 border-b border-slate-800">
        <Link href="/resumes" className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center mb-1">
          ← Back to Resumes
        </Link>
        <h1 className="text-2xl font-bold text-slate-100">Resume Version History</h1>
        <p className="mt-1 text-sm text-slate-400">
          Maintain multiple versions of your resume tailored for different career tracks without overwriting your original documents.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-rose-900/40 border border-rose-700 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 rounded-lg bg-emerald-900/40 border border-emerald-700 text-emerald-300 text-sm">
          {success}
        </div>
      )}

      {/* Upload New Version Form */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 mb-8">
        <h2 className="text-base font-semibold text-slate-200 mb-4 pb-2 border-b border-slate-800">
          Upload New Version
        </h2>

        <form onSubmit={handleUploadVersion} className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Version Label</label>
            <input
              type="text"
              value={newLabel}
              onChange={(e) => setNewLabel(e.target.value)}
              placeholder="e.g. v2 - Backend Track"
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Select Document (PDF / DOCX)</label>
            <input
              type="file"
              accept=".pdf,.docx"
              onChange={(e) => setNewFile(e.target.files ? e.target.files[0] : null)}
              className="w-full text-xs text-slate-400 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-indigo-400 hover:file:bg-slate-700 cursor-pointer"
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={!newFile || uploading}
              className="w-full px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-colors flex items-center justify-center"
            >
              {uploading ? "Uploading Version..." : "+ Add Version"}
            </button>
          </div>
        </form>
      </div>

      {/* Version History Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        <div className="p-6 border-b border-slate-800">
          <h2 className="text-base font-semibold text-slate-200">Existing Versions ({versions.length})</h2>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-400">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto mb-3"></div>
            Loading versions...
          </div>
        ) : versions.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-sm">No versions found.</div>
        ) : (
          <div className="divide-y divide-slate-800">
            {versions.map((ver) => (
              <div key={ver.id} className="p-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <div className="flex items-center space-x-3">
                    <span className="text-sm font-bold text-slate-100">{ver.version_label}</span>
                    {ver.is_active && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-900 text-indigo-200 border border-indigo-700">
                        ACTIVE VERSION
                      </span>
                    )}
                    <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 font-mono">
                      {ver.file_type.toUpperCase()}
                    </span>
                  </div>

                  <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-slate-400">
                    <span>{ver.original_filename}</span>
                    <span>•</span>
                    <span>{(ver.file_size_bytes / (1024 * 1024)).toFixed(2)} MB</span>
                    <span>•</span>
                    <span>Uploaded: {new Date(ver.uploaded_at).toLocaleDateString()}</span>
                    <span>•</span>
                    <span>Status: <strong className="text-slate-300">{ver.parsing_status}</strong></span>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {!ver.is_active && (
                    <button
                      onClick={() => handleSetActive(ver.id)}
                      className="px-3 py-1.5 rounded-lg border border-slate-700 hover:border-indigo-500 text-xs font-medium text-slate-300 hover:text-indigo-400 transition-colors"
                    >
                      Make Active
                    </button>
                  )}

                  <a
                    href={`/api/v1/resumes/${resumeId}/download?version_id=${ver.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 border border-slate-700 transition-colors"
                  >
                    Download
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

