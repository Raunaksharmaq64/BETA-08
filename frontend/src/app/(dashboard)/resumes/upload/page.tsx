"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

export default function ResumeUploadPage() {
  const router = useRouter();
  const [title, setTitle] = useState("Software Engineer Resume");
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    setError(null);
    const validExtensions = [".pdf", ".docx"];
    const ext = selectedFile.name.substring(selectedFile.name.lastIndexOf(".")).toLowerCase();

    if (!validExtensions.includes(ext)) {
      setError("Invalid file format. Please upload a PDF (.pdf) or Word document (.docx).");
      setFile(null);
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("File exceeds 10MB limit. Please compress or choose a smaller document.");
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a resume file to upload.");
      return;
    }

    try {
      setUploading(true);
      setError(null);

      const formData = new FormData();
      formData.append("title", title);
      formData.append("file", file);

      const res = await apiClient.postForm<any>("/api/v1/resumes", formData);
      if (res.success && res.data) {
        // Automatically initiate parsing pipeline
        try {
          await apiClient.post(`/api/v1/resumes/${res.data.resume_id}/parse`);
        } catch (parseErr) {
          console.warn("Auto-parse trigger:", parseErr);
        }
        // Redirect directly to parsed resume profile & analysis
        router.push(`/resumes/${res.data.resume_id}/analysis`);
      }
    } catch (err: any) {
      setError(err.message || "Failed to upload resume document.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <Link href="/resumes" className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center mb-2">
          ← Back to Resumes
        </Link>
        <h1 className="text-2xl font-bold text-slate-100">Upload Resume Document</h1>
        <p className="mt-1 text-sm text-slate-400">
          Upload your resume in PDF or DOCX format to initiate privacy-preserving entity extraction and evidence citation.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-rose-900/40 border border-rose-700 text-rose-300 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-slate-900/60 border border-slate-800 rounded-xl p-8 shadow-sm">
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-300 mb-2">Resume Title / Version Label</label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-4 py-2.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
            placeholder="e.g. Senior Backend Developer Resume"
          />
        </div>

        {/* Drag and Drop Zone */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-10 text-center transition-colors cursor-pointer ${
            dragActive
              ? "border-indigo-500 bg-indigo-950/20"
              : file
              ? "border-emerald-600/70 bg-emerald-950/10"
              : "border-slate-700 hover:border-slate-600 bg-slate-800/40"
          }`}
          onClick={() => document.getElementById("fileInput")?.click()}
        >
          <input
            id="fileInput"
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={handleChange}
            className="hidden"
          />

          <div className="w-12 h-12 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-3 text-indigo-400">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
          </div>

          {file ? (
            <div>
              <p className="text-sm font-semibold text-emerald-400">{file.name}</p>
              <p className="text-xs text-slate-400 mt-1">{(file.size / (1024 * 1024)).toFixed(2)} MB • Ready to upload</p>
              <span className="mt-3 inline-block text-xs text-indigo-400 hover:underline">Click to choose different file</span>
            </div>
          ) : (
            <div>
              <p className="text-sm font-medium text-slate-300">
                Drag and drop your resume here, or <span className="text-indigo-400 font-semibold">browse files</span>
              </p>
              <p className="text-xs text-slate-400 mt-1">Supports PDF (.pdf) or Word (.docx) up to 10 MB</p>
            </div>
          )}
        </div>

        {/* Security Notice */}
        <div className="mt-6 p-4 rounded-lg bg-slate-800/60 border border-slate-700/60 text-xs text-slate-400">
          <p className="font-semibold text-slate-300 mb-1">Privacy & Evidence Notice:</p>
          <p>
            Files are stored in private isolated storage and are never publicly accessible. Information extracted from
            this document will remain pending candidate review and will not overwrite your profile facts without explicit confirmation.
          </p>
        </div>

        <div className="mt-8 flex justify-end space-x-3">
          <Link
            href="/resumes"
            className="px-4 py-2 border border-slate-700 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-800 transition-colors"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={!file || uploading}
            className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center"
          >
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Uploading & Validating...
              </>
            ) : (
              "Upload and Continue"
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

