"use client";

import { useState, useEffect } from "react";
import { ApprovalPanel } from "@/components/ApprovalPanel";
import { DocumentViewer } from "@/components/DocumentViewer";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AuditEntry {
  id: number;
  finding_id: string;
  action: string;
  user_id: string;
  comment: string | null;
  created_at: string | null;
}

export interface VerificationFinding {
  finding_id: string;
  requirement_id: string;
  clause_ref: string;
  source_reference: string;
  status: "pass" | "fail" | "warning" | "manual_review";
  message: string;
  parameter_name?: string;
  expected_value?: string;
  actual_value?: string;
  confidence: number;
  requires_manual_review: boolean;
}

export default function DashboardPage() {
  const [findings, setFindings] = useState<VerificationFinding[]>([]);
  const [fileName, setFileName] = useState<string | null>(null);
  const [overallStatus, setOverallStatus] = useState<string>("");
  const [summary, setSummary] = useState<string>("");
  const [rulesChecked, setRulesChecked] = useState<string[]>([]);
  const [auditEntries, setAuditEntries] = useState<AuditEntry[]>([]);

  const fetchAuditLog = () => {
    fetch(`${API_URL}/api/audit/recent`)
      .then((r) => r.ok ? r.json() : { entries: [] })
      .then((data) => setAuditEntries(data.entries || []))
      .catch(() => setAuditEntries([]));
  };

  useEffect(() => {
    const raw = sessionStorage.getItem("veriflow_last_result");
    if (raw) {
      try {
        const data = JSON.parse(raw);
        const findingsList = data.findings || [];
        setFindings(findingsList);
        setOverallStatus(findingsList.length > 0 ? (data.overall_status || "") : "");
        setSummary(data.summary || "");
        setRulesChecked(data.rules_checked || []);
        setFileName(data.fileName || null);
      } catch {
        // ignore
      }
    }
  }, []);

  useEffect(() => {
    fetchAuditLog();
  }, []);

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-12">
      <header className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-[var(--foreground)] tracking-tight">Auditor Dashboard</h1>
          <p className="text-[var(--muted-foreground)] text-base mt-1 leading-relaxed">
            Review findings with direct citations (standard + clause). Approve or reject each finding; decisions are logged for governance.
          </p>
          {rulesChecked.length > 0 && (
            <p className="text-xs text-[var(--muted-foreground)] mt-2">
              Rules applied: {rulesChecked.map((r) => `Clause ${r}`).join(", ")}
            </p>
          )}
        </div>
        {overallStatus && (
          <div className="flex items-center gap-3">
            {summary && <span className="text-sm text-[var(--muted-foreground)]">{summary}</span>}
            <span
              className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium ${
                overallStatus === "pass"
                  ? "bg-[var(--success-muted)] text-[var(--success)]"
                  : overallStatus === "fail"
                  ? "bg-[var(--destructive-muted)] text-[var(--destructive)]"
                  : "bg-[var(--warning-muted)] text-[var(--warning)]"
              }`}
            >
              {overallStatus}
            </span>
          </div>
        )}
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 min-h-[calc(100vh-16rem)]">
        <div className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--card)] overflow-hidden flex flex-col shadow-[var(--shadow)]">
          <div className="px-4 py-3 border-b border-[var(--border)] flex items-center justify-between bg-[var(--muted)]/50">
            <span className="text-sm font-medium text-[var(--foreground)]">Uploaded document</span>
            {fileName && <span className="text-xs text-[var(--muted-foreground)] truncate max-w-[12rem]" title={fileName}>{fileName}</span>}
          </div>
          <DocumentViewer documentUrl={null} fileName={fileName} />
        </div>
        <div className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--card)] overflow-hidden flex flex-col shadow-[var(--shadow)]">
          <div className="px-4 py-3 border-b border-[var(--border)] bg-[var(--muted)]/50">
            <span className="text-sm font-medium text-[var(--foreground)]">Compliance gaps & findings</span>
          </div>
          <ApprovalPanel
            findings={findings}
            onFindingsChange={() => {}}
            onOverallStatusChange={setOverallStatus}
            onAuditDecision={fetchAuditLog}
          />
        </div>
      </div>

      {findings.length === 0 && (
        <p className="mt-4 text-center text-sm text-[var(--muted-foreground)]">
          <Link href="/upload" className="text-[var(--primary)] hover:underline">Upload & Verify</Link> a BOM to see findings here.
        </p>
      )}

      {auditEntries.length > 0 && (
        <section className="mt-10 rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--card)] overflow-hidden shadow-[var(--shadow)]">
          <div className="px-4 py-3 border-b border-[var(--border)] bg-[var(--muted)]/50">
            <span className="text-sm font-medium text-[var(--foreground)]">Recent audit log</span>
            <span className="ml-2 text-xs text-[var(--muted-foreground)]">(Approve/Reject decisions persisted when PostgreSQL is configured)</span>
          </div>
          <ul className="divide-y divide-[var(--border)] max-h-48 overflow-y-auto">
            {auditEntries.slice(0, 10).map((e) => (
              <li key={e.id} className="px-4 py-2 text-sm flex flex-wrap items-center gap-2">
                <span className={e.action === "approve" ? "text-[var(--success)]" : "text-[var(--destructive)]"}>{e.action}</span>
                <span className="text-[var(--muted-foreground)]">finding</span>
                <code className="text-xs bg-[var(--muted)] px-1.5 py-0.5 rounded truncate max-w-[8rem]">{e.finding_id.slice(0, 8)}…</code>
                <span className="text-[var(--muted-foreground)]">by {e.user_id}</span>
                {e.created_at && <span className="text-xs text-[var(--muted-foreground)]">{new Date(e.created_at).toLocaleString()}</span>}
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
