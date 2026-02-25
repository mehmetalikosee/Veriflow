"use client";

import { useState } from "react";
import Link from "next/link";

export interface FindingItem {
  finding_id: string;
  requirement_id: string;
  clause_ref: string;
  source_reference: string;
  status: string;
  message: string;
  parameter_name?: string;
  expected_value?: string;
  actual_value?: string;
  confidence: number;
  requires_manual_review: boolean;
}

interface ApprovalPanelProps {
  findings: FindingItem[];
  onFindingsChange: (findings: FindingItem[]) => void;
  onOverallStatusChange?: (status: string) => void;
  onAuditDecision?: () => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function ApprovalPanel({
  findings,
  onFindingsChange,
  onOverallStatusChange,
  onAuditDecision,
}: ApprovalPanelProps) {
  const [decisions, setDecisions] = useState<Record<string, "approve" | "reject" | null>>({});

  const handleDecision = (findingId: string, action: "approve" | "reject") => {
    setDecisions((prev) => ({ ...prev, [findingId]: action }));
    fetch(`${API_URL}/api/audit/log`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        finding_id: findingId,
        action,
        user_id: "auditor-1",
      }),
    })
      .then(() => onAuditDecision?.())
      .catch(() => {});
  };

  if (findings.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-[var(--muted-foreground)] text-sm text-center space-y-4">
        <p>No findings yet. Run verification from the Upload page to see compliance gaps and citations.</p>
        <Link
          href="/upload"
          className="rounded-xl bg-[var(--primary)] px-4 py-2 text-[var(--primary-foreground)] text-sm font-medium hover:bg-[var(--primary-hover)] transition-colors"
        >
          Go to Upload & Verify
        </Link>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-auto p-4 space-y-4">
      {findings.map((f) => (
        <div
          key={f.finding_id}
          className={`rounded-[var(--radius)] border p-4 ${
            f.status === "pass"
              ? "border-[var(--success)]/30 bg-[var(--success-muted)]"
              : f.status === "fail"
              ? "border-[var(--destructive)]/30 bg-[var(--destructive-muted)]"
              : "border-[var(--warning)]/30 bg-[var(--warning-muted)]"
          }`}
        >
          <div className="flex justify-between items-start gap-3">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-xs font-medium px-2 py-0.5 rounded bg-[var(--muted)] text-[var(--foreground)]">
                  Clause {f.clause_ref}
                </span>
                {f.requires_manual_review && (
                  <span className="text-xs text-[var(--warning)]">Manual review</span>
                )}
              </div>
              <p className="text-sm text-[var(--foreground)] font-medium mt-1">{f.message}</p>
              <p className="text-xs text-[var(--muted-foreground)] mt-2">
                Source: {f.source_reference}
              </p>
              {(f.expected_value != null || f.actual_value != null) && (
                <p className="text-xs text-[var(--muted-foreground)] mt-1">
                  Expected: <strong className="text-[var(--foreground)]">{f.expected_value}</strong> — Actual: <strong className="text-[var(--foreground)]">{f.actual_value}</strong>
                </p>
              )}
            </div>
            <div className="flex gap-2 shrink-0">
              <button
                onClick={() => handleDecision(f.finding_id, "approve")}
                className="rounded-lg px-3 py-2 text-xs font-medium bg-[var(--success)]/20 text-[var(--success)] hover:bg-[var(--success)]/30 transition"
              >
                Approve
              </button>
              <button
                onClick={() => handleDecision(f.finding_id, "reject")}
                className="rounded-lg px-3 py-2 text-xs font-medium bg-[var(--destructive-muted)] text-[var(--destructive)] hover:bg-[var(--destructive)]/20 transition-colors"
              >
                Reject
              </button>
            </div>
          </div>
          {decisions[f.finding_id] && (
            <p className="text-xs text-[var(--muted-foreground)] mt-2 pt-2 border-t border-[var(--border)]">
              You {decisions[f.finding_id]}d this finding.
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
