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
    <div className="max-w-3xl mx-auto px-4 py-10 sm:px-6 lg:px-8 space-y-6 animate-fade-in">
      <div className="border-b border-slate-300/80 pb-5">
        <Link href="/resumes" className="text-xs font-bold text-indigo-700 hover:text-indigo-900 flex items-center gap-1 mb-2 transition-colors">
          ← Back to Resumes
        </Link>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">Upload Resume Document</h1>
        <p className="mt-1 text-sm text-slate-600 font-semibold">
          Upload your resume in PDF or DOCX format to initiate privacy-preserving entity extraction and evidence citation.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-2xl neo-inset border border-rose-300 text-rose-950 text-sm font-bold">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="neo-box p-8 rounded-2xl border border-white/95 space-y-6 shadow-md">
        <div>
          <label className="block text-xs font-black text-slate-900 uppercase tracking-wider mb-2">Resume Title / Version Label</label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-4 py-3 rounded-xl neo-inset text-slate-900 font-semibold focus:outline-none text-sm border border-slate-300/80"
            placeholder="e.g. Senior Full Stack Developer Resume"
          />
        </div>

        {/* Drag and Drop Zone */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all cursor-pointer ${
            dragActive
              ? "border-indigo-600 neo-inset"
              : file
              ? "border-emerald-500 neo-inset"
              : "border-slate-300 hover:border-indigo-500 neo-card neo-box-hover"
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

          <div className="w-14 h-14 neo-pill rounded-2xl flex items-center justify-center mx-auto mb-3 text-indigo-700 text-2xl shadow-sm">
            📄
          </div>

          {file ? (
            <div className="space-y-1">
              <p className="text-sm font-black text-emerald-800">{file.name}</p>
              <p className="text-xs text-slate-600 font-bold">{(file.size / (1024 * 1024)).toFixed(2)} MB • Ready to upload</p>
              <span className="mt-2 inline-block text-xs text-indigo-700 font-bold hover:underline">Click to change file</span>
            </div>
          ) : (
            <div className="space-y-1">
              <p className="text-sm font-bold text-slate-900">
                Drag and drop your resume here, or <span className="text-indigo-700 font-black">browse files</span>
              </p>
              <p className="text-xs text-slate-600 font-semibold">Supports PDF (.pdf) or Word (.docx) up to 10 MB</p>
            </div>
          )}
        </div>

        {/* Security Notice */}
        <div className="p-4 rounded-xl neo-inset border border-slate-300/70 text-xs text-slate-700 font-medium">
          <p className="font-black text-slate-900 mb-1">Privacy &amp; Evidence Notice:</p>
          <p>
            Files are stored in private isolated storage and are never publicly accessible. Information extracted from
            this document will remain pending candidate review and will not overwrite your profile facts without explicit confirmation.
          </p>
        </div>

        <div className="flex justify-end items-center gap-3 pt-2">
          <Link
            href="/resumes"
            className="neo-pill px-4 py-2.5 rounded-xl text-xs font-bold text-slate-800 hover:text-indigo-600 transition-all"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={!file || uploading}
            className="neo-btn-primary px-6 py-2.5 rounded-xl text-xs font-bold transition-all shadow-md flex items-center disabled:opacity-50"
          >
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Uploading &amp; Extracting Skills...
              </>
            ) : (
              "Upload and Extract Skills →"
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
