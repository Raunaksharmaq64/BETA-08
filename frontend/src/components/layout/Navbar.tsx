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
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleLogout = async () => {
    await logout();
    setMobileMenuOpen(false);
    router.push("/login");
  };

  // Close menus on route change
  useEffect(() => {
    setMobileMenuOpen(false);
    setMoreDropdownOpen(false);
  }, [pathname]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setMoreDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Primary links visible on desktop header
  const primaryLinks = [
    { name: "Dashboard", href: "/dashboard" },
    { name: "Opportunities", href: "/opportunities" },
    { name: "Find Jobs", href: "/search" },
    { name: "Applications", href: "/applications" },
    { name: "Resumes", href: "/resumes" },
    { name: "Calendar", href: "/calendar" },
    { name: "Notifications", href: "/notifications" },
  ];

  // Secondary links in "More" dropdown on desktop
  const secondaryLinks = [
    { name: "Freelance Leads", href: "/freelance", category: "Discovery" },
    { name: "Startup Signals", href: "/startups", category: "Discovery" },
    { name: "Saved Opportunities", href: "/saved-opportunities", category: "Tracking" },
    { name: "Saved Jobs", href: "/saved-jobs", category: "Tracking" },
    { name: "Search Alerts", href: "/saved-searches", category: "Tracking" },
    { name: "Interview Prep", href: "/interview-prep", category: "Career Tools" },
    { name: "Market Intelligence", href: "/market-intelligence", category: "Market" },
    { name: "Compensation Explorer", href: "/compensation", category: "Market" },
    { name: "Candidate Profile", href: "/profile", category: "Account" },
    { name: "Job Sources Registry", href: "/sources", category: "Operations" },
    { name: "Connectors Observability", href: "/quality/connectors", category: "Operations" },
    { name: "Discovery Operations", href: "/discovery/operations", category: "Operations" },
    { name: "Data Quality Metrics", href: "/quality", category: "Operations" },
    { name: "Beta Feedback", href: "/beta/feedback", category: "System" },
    { name: "Privacy & Data Rights", href: "/settings/privacy", category: "System" },
  ];

  // All navigation links grouped for mobile menu
  const mobileGroups = [
    {
      title: "Core Discovery",
      links: [
        { name: "Dashboard", href: "/dashboard" },
        { name: "Opportunities", href: "/opportunities" },
        { name: "Find Jobs", href: "/search" },
        { name: "Freelance Leads", href: "/freelance" },
        { name: "Startup Signals", href: "/startups" },
      ],
    },
    {
      title: "Career & CRM",
      links: [
        { name: "Applications CRM", href: "/applications" },
        { name: "Calendar & Deadlines", href: "/calendar" },
        { name: "Interview Prep", href: "/interview-prep" },
        { name: "Resume Intelligence", href: "/resumes" },
        { name: "Saved Opportunities", href: "/saved-opportunities" },
        { name: "Saved Jobs", href: "/saved-jobs" },
        { name: "Search Alerts", href: "/saved-searches" },
      ],
    },
    {
      title: "Market Intelligence",
      links: [
        { name: "Market & Skills Intel", href: "/market-intelligence" },
        { name: "Compensation Explorer", href: "/compensation" },
      ],
    },
    {
      title: "System & Governance",
      links: [
        { name: "Candidate Profile", href: "/profile" },
        { name: "Notifications", href: "/notifications" },
        { name: "Job Sources", href: "/sources" },
        { name: "Connector Health", href: "/quality/connectors" },
        { name: "Discovery Operations", href: "/discovery/operations" },
        { name: "Data Quality", href: "/quality" },
        { name: "Beta Feedback", href: "/beta/feedback" },
        { name: "Privacy & Security", href: "/settings/privacy" },
      ],
    },
  ];

  const isMoreActive = secondaryLinks.some((l) => pathname === l.href || pathname?.startsWith(`${l.href}/`));

  return (
    <header className="sticky top-0 z-50 bg-slate-900/95 backdrop-blur-md border-b border-slate-800 text-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Desktop Primary Navigation */}
          <div className="flex items-center space-x-6 lg:space-x-8">
            <Link href="/dashboard" className="flex items-center space-x-2 shrink-0 group">
              <span className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-black text-white text-sm shadow-md shadow-indigo-600/30 group-hover:bg-indigo-500 transition-colors">
                RF
              </span>
              <span className="text-lg font-bold tracking-tight text-white group-hover:text-indigo-400 transition-colors">
                RIGHT FIT
              </span>
            </Link>

            {/* Desktop Navigation Links */}
            <nav className="hidden lg:flex items-center space-x-1" aria-label="Main Navigation">
              {primaryLinks.map((link) => {
                const isActive = pathname === link.href || pathname?.startsWith(`${link.href}/`);
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      isActive
                        ? "bg-slate-800 text-indigo-400 border border-slate-700/80 shadow-sm"
                        : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
                    }`}
                  >
                    {link.name}
                  </Link>
                );
              })}

              {/* "More" Dropdown Menu */}
              <div className="relative" ref={dropdownRef}>
                <button
                  type="button"
                  onClick={() => setMoreDropdownOpen(!moreDropdownOpen)}
                  aria-expanded={moreDropdownOpen}
                  aria-haspopup="true"
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all inline-flex items-center gap-1.5 ${
                    isMoreActive
                      ? "bg-slate-800 text-indigo-400 border border-slate-700"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
                  }`}
                >
                  <span>More</span>
                  <svg
                    className={`w-3.5 h-3.5 transition-transform duration-200 ${
                      moreDropdownOpen ? "rotate-180 text-indigo-400" : "text-slate-400"
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {moreDropdownOpen && (
                  <div className="absolute left-0 mt-2 w-64 rounded-xl bg-slate-900 border border-slate-800 shadow-2xl py-2 z-50 text-xs animate-in fade-in slide-in-from-top-1 duration-150">
                    <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-800/80">
                      Discovery & Leads
                    </div>
                    {secondaryLinks
                      .filter((l) => l.category === "Discovery" || l.category === "Tracking")
                      .map((link) => (
                        <Link
                          key={link.href}
                          href={link.href}
                          onClick={() => setMoreDropdownOpen(false)}
                          className={`block px-3.5 py-1.5 transition-colors ${
                            pathname === link.href
                              ? "bg-indigo-600/20 text-indigo-300 font-semibold"
                              : "text-slate-300 hover:bg-slate-800 hover:text-white"
                          }`}
                        >
                          {link.name}
                        </Link>
                      ))}

                    <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500 border-t border-b border-slate-800/80 mt-1">
                      Intelligence & Career
                    </div>
                    {secondaryLinks
                      .filter((l) => l.category === "Career Tools" || l.category === "Market")
                      .map((link) => (
                        <Link
                          key={link.href}
                          href={link.href}
                          onClick={() => setMoreDropdownOpen(false)}
                          className={`block px-3.5 py-1.5 transition-colors ${
                            pathname === link.href
                              ? "bg-indigo-600/20 text-indigo-300 font-semibold"
                              : "text-slate-300 hover:bg-slate-800 hover:text-white"
                          }`}
                        >
                          {link.name}
                        </Link>
                      ))}

                    <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-500 border-t border-b border-slate-800/80 mt-1">
                      Operations & System
                    </div>
                    {secondaryLinks
                      .filter((l) => l.category === "Operations" || l.category === "System" || l.category === "Account")
                      .map((link) => (
                        <Link
                          key={link.href}
                          href={link.href}
                          onClick={() => setMoreDropdownOpen(false)}
                          className={`block px-3.5 py-1.5 transition-colors ${
                            pathname === link.href
                              ? "bg-indigo-600/20 text-indigo-300 font-semibold"
                              : "text-slate-300 hover:bg-slate-800 hover:text-white"
                          }`}
                        >
                          {link.name}
                        </Link>
                      ))}
                  </div>
                )}
              </div>
            </nav>
          </div>

          {/* Right Header: User Session & Mobile Hamburger Toggle */}
          <div className="flex items-center space-x-3">
            {user ? (
              <div className="flex items-center space-x-3">
                <div className="text-right hidden sm:block">
                  <div className="text-xs font-semibold text-white truncate max-w-[140px] md:max-w-[180px]">
                    {user.full_name || "Candidate"}
                  </div>
                  <div className="text-[10px] text-slate-400 truncate max-w-[140px] md:max-w-[180px]">
                    {user.email}
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="hidden sm:inline-flex px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="hidden sm:flex items-center space-x-2">
                <Link
                  href="/login"
                  className="px-3 py-1.5 text-xs font-medium rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm transition"
                >
                  Register
                </Link>
              </div>
            )}

            {/* Mobile Hamburger Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              aria-label={mobileMenuOpen ? "Close navigation menu" : "Open navigation menu"}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Slide-Down Navigation Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-slate-800 bg-slate-900/98 backdrop-blur-xl px-4 pt-3 pb-6 max-h-[calc(100vh-4rem)] overflow-y-auto space-y-5 animate-in fade-in slide-in-from-top-2 duration-200">
          {/* User profile row on mobile */}
          {user ? (
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
              <div className="truncate pr-2">
                <div className="text-sm font-semibold text-white truncate">{user.full_name || "Candidate"}</div>
                <div className="text-xs text-slate-400 truncate">{user.email}</div>
              </div>
              <button
                onClick={handleLogout}
                className="shrink-0 px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-rose-950 hover:text-rose-300 text-slate-300 border border-slate-700 transition"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-2 pt-1">
              <Link
                href="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="py-2.5 text-center text-xs font-semibold rounded-lg bg-slate-800 text-slate-200 border border-slate-700"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="py-2.5 text-center text-xs font-semibold rounded-lg bg-indigo-600 text-white"
              >
                Register
              </Link>
            </div>
          )}

          {/* Grouped mobile links */}
          {mobileGroups.map((group) => (
            <div key={group.title} className="space-y-1.5">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-2.5">
                {group.title}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
                {group.links.map((link) => {
                  const isActive = pathname === link.href || pathname?.startsWith(`${link.href}/`);
                  return (
                    <Link
                      key={link.href}
                      href={link.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className={`flex items-center px-3 py-2 rounded-lg text-xs font-medium transition ${
                        isActive
                          ? "bg-indigo-600 text-white font-semibold shadow-sm"
                          : "text-slate-300 hover:bg-slate-800 hover:text-white"
                      }`}
                    >
                      {link.name}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </header>
  );
}
