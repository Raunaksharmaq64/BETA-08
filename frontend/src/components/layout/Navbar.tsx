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

  // Primary links visible on navigation bar
  const primaryLinks = [
    { name: "Dashboard", href: "/dashboard" },
    { name: "Opportunities", href: "/opportunities" },
    { name: "Find Jobs", href: "/search" },
    { name: "Startups", href: "/startups" },
    { name: "Freelance", href: "/freelance" },
    { name: "Applications", href: "/applications" },
    { name: "Resumes", href: "/resumes" },
  ];

  // Secondary candidate tools in More dropdown
  const secondaryLinks = [
    { name: "Candidate Profile", href: "/profile", icon: "👤" },
    { name: "Saved Bookmarks", href: "/saved-opportunities", icon: "⭐" },
    { name: "Calendar & Deadlines", href: "/calendar", icon: "📅" },
  ];

  // Check if current active page is inside the More dropdown
  const isMoreActive = secondaryLinks.some((l) => pathname === l.href);

  return (
    <nav className="neo-box sticky top-0 z-40 backdrop-blur-md border-b border-white/80 text-slate-900 transition-all duration-200">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center gap-2">
          {/* Left: Brand */}
          <div className="flex items-center shrink-0">
            <Link href="/dashboard" className="flex items-center space-x-2 shrink-0 group">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-600 shadow-sm group-hover:scale-125 transition-transform" />
              <span className="text-lg sm:text-xl font-black tracking-tight text-slate-900 whitespace-nowrap">
                RIGHT <span className="text-indigo-600">FIT</span>
              </span>
            </Link>
          </div>

          {/* Center: Desktop & Tablet Navigation Links (Full coverage, unclipped dropdown) */}
          <div className="hidden md:flex items-center space-x-1 lg:space-x-1.5 py-1">
            <div className="flex items-center space-x-1 lg:space-x-1.5 overflow-x-auto no-scrollbar py-0.5">
              {primaryLinks.map((link) => {
                const isActive = pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`px-2.5 lg:px-3 py-1.5 rounded-xl text-xs lg:text-[13px] font-bold transition-all duration-150 shrink-0 whitespace-nowrap ${
                      isActive
                        ? "neo-inset text-indigo-700 font-black border border-slate-300/80 shadow-inner scale-[1.02]"
                        : "text-slate-900 hover:text-indigo-600 hover:bg-white/90 font-bold"
                    }`}
                  >
                    {link.name}
                  </Link>
                );
              })}
            </div>

            {/* "More ▾" Flyout Dropdown (Isolated outside overflow-x-auto to prevent clipping) */}
            <div className="relative shrink-0" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setMoreDropdownOpen((prev) => !prev)}
                className={`px-3 py-1.5 rounded-xl text-xs lg:text-[13px] font-bold transition-all duration-150 flex items-center gap-1 shrink-0 whitespace-nowrap cursor-pointer ${
                  isMoreActive || moreDropdownOpen
                    ? "neo-inset text-indigo-700 font-black border border-slate-300/80"
                    : "neo-pill text-slate-900 hover:text-indigo-600 font-bold"
                }`}
                aria-expanded={moreDropdownOpen}
              >
                <span>More</span>
                <span className={`text-[10px] transition-transform duration-200 ${moreDropdownOpen ? "rotate-180" : ""}`}>
                  ▾
                </span>
              </button>

              {moreDropdownOpen && (
                <div className="absolute right-0 top-full mt-2 w-56 neo-box rounded-2xl shadow-2xl p-2 space-y-1 z-50 animate-fade-in border border-white/95">
                  {secondaryLinks.map((link) => {
                    const isActive = pathname === link.href;
                    return (
                      <Link
                        key={link.href}
                        href={link.href}
                        onClick={() => setMoreDropdownOpen(false)}
                        className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap cursor-pointer ${
                          isActive
                            ? "neo-inset text-indigo-700 font-black"
                            : "text-slate-900 hover:bg-white/90 hover:text-indigo-600 font-bold"
                        }`}
                      >
                        <span className="text-sm">{link.icon}</span>
                        <span>{link.name}</span>
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Right: User Status & Mobile Hamburger Toggle */}
          <div className="flex items-center space-x-2 shrink-0">
            {!mounted ? (
              <div className="w-16 h-8 rounded-xl bg-slate-300/50 animate-pulse" />
            ) : user ? (
              <div className="flex items-center space-x-2 sm:space-x-3">
                <div className="text-right hidden sm:block max-w-[120px] md:max-w-xs truncate">
                  <div className="text-xs font-black text-slate-900 truncate">{user.full_name}</div>
                  <div className="text-[11px] font-bold text-slate-600 truncate">{user.email}</div>
                </div>
                <button
                  onClick={handleLogout}
                  className="neo-pill px-2.5 sm:px-3 py-1.5 text-xs font-bold text-rose-700 hover:text-rose-900 transition-all shrink-0 whitespace-nowrap"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <Link
                href="/login"
                className="neo-btn-primary px-3 sm:px-4 py-1.5 sm:py-2 text-xs font-bold rounded-xl transition-all shrink-0 shadow-md whitespace-nowrap"
              >
                Sign In
              </Link>
            )}

            {/* Hamburger Button for Mobile (< 768px) */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen((prev) => !prev)}
              aria-label="Toggle navigation menu"
              className="md:hidden neo-pill p-2 text-slate-900 hover:text-indigo-600 focus:outline-none transition-all"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {mobileMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer (< 768px) */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-300/70 neo-box px-4 pt-3 pb-8 space-y-5 max-h-[85vh] overflow-y-auto animate-fade-in">
          {mounted && user && (
            <div className="p-3 neo-inset rounded-2xl flex items-center justify-between">
              <div>
                <div className="text-sm font-black text-slate-900">{user.full_name}</div>
                <div className="text-xs font-bold text-slate-600">{user.email}</div>
              </div>
              <button
                onClick={handleLogout}
                className="neo-pill px-3 py-1 text-xs font-bold text-rose-700"
              >
                Sign Out
              </button>
            </div>
          )}

          {/* Primary Quick Links */}
          <div className="space-y-1">
            <div className="text-[11px] font-black uppercase tracking-wider text-indigo-700 px-2 pb-1">
              Core Modules
            </div>
            <div className="grid grid-cols-2 gap-2">
              {primaryLinks.map((link) => {
                const isActive = pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`px-3 py-2 rounded-xl text-xs font-bold transition-all text-center ${
                      isActive
                        ? "neo-inset text-indigo-700 font-black shadow-inner"
                        : "neo-card text-slate-900 hover:text-indigo-600 font-bold"
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
            <div className="text-[11px] font-black uppercase tracking-wider text-slate-900 px-2 pb-1 border-b border-slate-300/60">
              Candidate Tools
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
              {secondaryLinks.map((link) => {
                const isActive = pathname === link.href;
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-bold transition-all ${
                      isActive
                        ? "neo-inset text-indigo-700 font-black"
                        : "neo-card text-slate-900 hover:text-indigo-600 font-bold"
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
