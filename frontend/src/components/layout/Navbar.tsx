"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [moreDropdownOpen, setMoreDropdownOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Close menus on route change
  useEffect(() => {
    setMobileMenuOpen(false);
    setMoreDropdownOpen(false);
  }, [pathname]);

  // Click outside listener for dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setMoreDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  // 6 primary links visible directly on desktop navigation bar
  const primaryLinks = [
    { name: "Dashboard", href: "/dashboard" },
    { name: "Opportunities", href: "/opportunities" },
    { name: "Find Jobs", href: "/search" },
    { name: "Startups", href: "/startups" },
    { name: "Freelance", href: "/freelance" },
    { name: "Applications", href: "/applications" },
    { name: "Resumes", href: "/resumes" },
  ];

  // Secondary candidate tools: Only Profile and Saved Bookmarks
  const secondaryLinks = [
    { name: "Candidate Profile", href: "/profile", icon: "👤" },
    { name: "Saved Bookmarks", href: "/saved-opportunities", icon: "⭐" },
  ];

  // Check if current active page is inside the More dropdown
  const isMoreActive = secondaryLinks.some((l) => pathname === l.href);

  return (
    <nav className="bg-slate-900 border-b border-slate-800 text-slate-200 sticky top-0 z-40 backdrop-blur-md bg-slate-900/95">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Left: Brand & Desktop Links */}
          <div className="flex items-center space-x-3 lg:space-x-6">
            <Link href="/profile" className="flex items-center space-x-2 shrink-0">
              <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                RIGHT FIT
              </span>
            </Link>

            {/* Desktop Navigation Links */}
            <div className="hidden lg:flex items-center space-x-1 xl:space-x-2">
              {primaryLinks.map((link) => {
                const isActive = pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`px-2.5 xl:px-3 py-1.5 rounded-lg text-xs xl:text-sm font-medium transition-colors shrink-0 ${isActive
                        ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30"
                        : "text-slate-300 hover:bg-slate-800 hover:text-white"
                      }`}
                  >
                    {link.name}
                  </Link>
                );
              })}

              {/* "More ▾" Flyout Dropdown */}
              <div className="relative" ref={dropdownRef}>
                <button
                  type="button"
                  onClick={() => setMoreDropdownOpen((prev) => !prev)}
                  className={`px-2.5 xl:px-3 py-1.5 rounded-lg text-xs xl:text-sm font-medium transition-colors flex items-center gap-1 shrink-0 ${isMoreActive || moreDropdownOpen
                      ? "bg-slate-800 text-indigo-400 border border-slate-700"
                      : "text-slate-300 hover:bg-slate-800 hover:text-white"
                    }`}
                  aria-expanded={moreDropdownOpen}
                >
                  <span>More</span>
                  <span className={`text-[10px] transition-transform duration-200 ${moreDropdownOpen ? "rotate-180" : ""}`}>
                    ▾
                  </span>
                </button>

                {moreDropdownOpen && (
                  <div className="absolute left-0 mt-2 w-52 bg-slate-900 border border-slate-700/80 rounded-xl shadow-2xl p-2 space-y-1 z-50 animate-in fade-in zoom-in-95 duration-150">
                    {secondaryLinks.map((link) => {
                      const isActive = pathname === link.href;
                      return (
                        <Link
                          key={link.href}
                          href={link.href}
                          onClick={() => setMoreDropdownOpen(false)}
                          className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs transition-colors ${isActive
                              ? "bg-indigo-600/30 text-indigo-300 font-semibold"
                              : "text-slate-300 hover:bg-slate-800 hover:text-white"
                            }`}
                        >
                          <span className="text-sm">{link.icon}</span>
                          <span className="font-medium">{link.name}</span>
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Tablet Navigation Links (Medium Screens 768px - 1024px) */}
            <div className="hidden md:flex lg:hidden items-center space-x-1">
              {primaryLinks.slice(0, 4).map((link) => {
                const isActive = pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors shrink-0 ${isActive
                        ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30"
                        : "text-slate-300 hover:bg-slate-800 hover:text-white"
                      }`}
                  >
                    {link.name}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Right: User Status & Mobile Hamburger Toggle */}
          <div className="flex items-center space-x-3">
            {!mounted ? (
              <div className="w-16 h-8 rounded-lg bg-slate-800/40 animate-pulse" />
            ) : user ? (
              <div className="flex items-center space-x-3">
                <div className="text-right hidden sm:block max-w-[150px] md:max-w-xs truncate">
                  <div className="text-xs font-semibold text-white truncate">{user.full_name}</div>
                  <div className="text-[11px] text-slate-400 truncate">{user.email}</div>
                </div>
                <button
                  onClick={handleLogout}
                  className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors shrink-0"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <Link
                href="/login"
                className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors shrink-0"
              >
                Sign In
              </Link>
            )}

            {/* Hamburger Button for Mobile / Tablet (< 1024px) */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen((prev) => !prev)}
              aria-label="Toggle navigation menu"
              className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile & Tablet Slide-Down Drawer (< 1024px) */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-slate-800 bg-slate-950 px-4 pt-3 pb-8 space-y-5 max-h-[85vh] overflow-y-auto">
          {mounted && user && (
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between">
              <div>
                <div className="text-sm font-bold text-white">{user.full_name}</div>
                <div className="text-xs text-slate-400">{user.email}</div>
              </div>
              <button
                onClick={handleLogout}
                className="px-3 py-1 text-xs font-semibold rounded-lg bg-slate-800 text-rose-300 border border-rose-900/50"
              >
                Sign Out
              </button>
            </div>
          )}

          {/* Primary Quick Links */}
          <div className="space-y-1">
            <div className="text-[11px] font-bold uppercase tracking-wider text-indigo-400 px-2 pb-1">
              Core Workflows
            </div>
            <div className="grid grid-cols-2 gap-1.5">
              {primaryLinks.map((link) => {
                const isActive = pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`px-3 py-2 rounded-lg text-xs font-semibold transition-colors ${isActive
                        ? "bg-indigo-600 text-white shadow-sm"
                        : "bg-slate-900 text-slate-300 hover:bg-slate-850 hover:text-white"
                      }`}
                  >
                    {link.name}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Candidate Quick Tools */}
          <div className="space-y-1.5">
            <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-2 pb-1 border-b border-slate-800/80">
              Candidate Tools
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 pt-1">
              {secondaryLinks.map((link) => {
                const isActive = pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs transition-colors ${isActive
                        ? "bg-indigo-600/30 text-indigo-300 font-bold border border-indigo-500/40"
                        : "text-slate-300 hover:bg-slate-900 hover:text-white"
                      }`}
                  >
                    <span className="text-sm">{link.icon}</span>
                    <span>{link.name}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
