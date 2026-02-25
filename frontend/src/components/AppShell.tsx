"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const nav = [
  { href: "/", label: "Home" },
  { href: "/upload", label: "Upload & Verify" },
  { href: "/dashboard", label: "Auditor Dashboard" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--card)]/98 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-8">
              <Link href="/" className="flex items-center gap-2">
                <span className="font-semibold text-lg text-[var(--foreground)]">Veriflow</span>
                <span className="text-[var(--muted-foreground)] font-normal">— ACE</span>
              </Link>
              <nav className="hidden md:flex gap-1">
                {nav.map(({ href, label }) => (
                  <Link
                    key={href}
                    href={href}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                      pathname === href
                        ? "bg-[var(--muted)] text-[var(--foreground)]"
                        : "text-[var(--muted-foreground)] hover:text-[var(--foreground)] hover:bg-[var(--muted)]"
                    }`}
                  >
                    {label}
                  </Link>
                ))}
              </nav>
            </div>
          </div>
        </div>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="border-t border-[var(--border)] bg-[var(--card)] py-6 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-[var(--muted-foreground)]">
          Veriflow — Autonomous Compliance Engine · Portfolio project · Not affiliated with any certification body · Not a substitute for professional judgment
        </div>
      </footer>
    </div>
  );
}
