"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string>("");
  const router = useRouter();

  const runVerification = async () => {
    if (!file) {
      setError("Select a BOM file first.");
      return;
    }
    setError("");
    setStatus("Uploading and extracting BOM...");
    try {
      const form = new FormData();
      form.append("file", file);
      const extRes = await fetch(`${API_URL}/api/extraction/bom`, {
        method: "POST",
        body: form,
      });
      if (!extRes.ok) {
        const t = await extRes.text();
        throw new Error(t || "Extraction failed");
      }
      const bom = await extRes.json();
      setStatus("Running verification against UL 60335-1...");
      const verRes = await fetch(`${API_URL}/api/verification/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bom),
      });
      if (!verRes.ok) {
        const errText = await verRes.text();
        throw new Error(errText || `Verification failed (${verRes.status})`);
      }
      const result = await verRes.json();
      sessionStorage.setItem(
        "veriflow_last_result",
        JSON.stringify({
          findings: result.findings,
          overall_status: result.overall_status,
          summary: result.summary,
          rules_checked: result.rules_checked || ["7", "8.1", "29.1", "29.2"],
          fileName: file.name,
        })
      );
      setStatus("Done. Redirecting to dashboard...");
      router.push("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
      setStatus("");
    }
  };

  return (
    <main className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-[var(--foreground)] tracking-tight mb-2">Upload & Verify</h1>
        <p className="text-[var(--muted-foreground)] text-base leading-relaxed">
          Upload a BOM (CSV or Excel). The system extracts data and runs verification against IEC/UL 60335-1 with full citations.
        </p>
      </div>

      <div className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--card)] p-6 sm:p-8 space-y-5 shadow-[var(--shadow)]">
        <label className="block">
          <span className="text-[var(--foreground)] text-sm font-medium block mb-2">BOM file (CSV or XLSX)</span>
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={(e) => {
              setFile(e.target.files?.[0] ?? null);
              setError("");
            }}
            className="block w-full text-sm text-[var(--muted-foreground)] file:mr-4 file:py-2.5 file:px-4 file:rounded-lg file:border-0 file:bg-[var(--primary)] file:text-[var(--primary-foreground)] file:font-medium file:cursor-pointer hover:file:bg-[var(--primary-hover)] transition-colors"
          />
        </label>
        <p className="text-xs text-[var(--muted-foreground)]">
          Expected columns: part_number, description, quantity, working_voltage_v, rated_voltage_v, clearance_mm, creepage_distance_mm, material_group, pollution_degree, overvoltage_category, insulation_type, ip_code
        </p>
        {error && (
          <div className="rounded-lg bg-[var(--destructive-muted)] border border-[var(--destructive)]/20 px-4 py-3 text-sm text-[var(--destructive)]">
            {error}
          </div>
        )}
        {status && <p className="text-sm text-[var(--primary)]">{status}</p>}
        <button
          onClick={runVerification}
          disabled={!file}
          className="w-full rounded-xl bg-[var(--primary)] px-4 py-3.5 text-[var(--primary-foreground)] font-medium hover:bg-[var(--primary-hover)] disabled:opacity-50 disabled:pointer-events-none transition-colors"
        >
          Run verification
        </button>
      </div>

      <div className="mt-10 rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--card)] p-6 sm:p-8 shadow-[var(--shadow)]">
        <h3 className="font-semibold text-[var(--foreground)] mb-2">Test data (20 + 6 advanced + legacy)</h3>
        <p className="text-sm text-[var(--muted-foreground)] mb-3">
          In <code className="bg-[var(--muted)] px-1.5 py-0.5 rounded text-xs text-[var(--foreground)]">test-data/</code>: <strong className="text-[var(--foreground)]">bom_01</strong>–<strong className="text-[var(--foreground)]">bom_20</strong> (focused scenarios), <strong className="text-[var(--foreground)]">bom_adv_01</strong>–<strong className="text-[var(--foreground)]">bom_adv_06</strong> (professional-level: ref des, decimals, multi-voltage, audit-style).
        </p>
        <ul className="text-sm text-[var(--muted-foreground)] space-y-1 max-h-48 overflow-y-auto">
          <li><strong className="text-[var(--foreground)]">01–10</strong> Single/multi pass, fail clearance/creepage/both, edge exact, tiny breaks (0.1 under)</li>
          <li><strong className="text-[var(--foreground)]">11–20</strong> 300V, multiple failures, partial data, household/industrial, boundary pass/fail, stress mixed</li>
          <li><strong className="text-[var(--foreground)]">21–24</strong> Clause 7 (rated voltage fail) · 22 reinforced pass · 23 Clause 8.1 (no IP → manual review) · 24 reinforced fail</li>
          <li className="pt-1 border-t border-[var(--border)]"><strong className="text-[var(--foreground)]">Advanced:</strong> 01 power supply pro · 02 household pro · 03 industrial pro · 04 multi-voltage · 05 audit marginals · 06 full audit</li>
          <li><strong className="text-[var(--foreground)]">Legacy:</strong> bom_power_supply, bom_power_supply_compliant, bom_household_appliance, bom_fail_both</li>
        </ul>
        <p className="text-xs text-[var(--muted-foreground)] mt-2">See <code className="bg-[var(--muted)] px-1 py-0.5 rounded">test-data/README.md</code> for expected pass/fail and advanced scenario notes.</p>
        <Link href="/dashboard" className="inline-block mt-4 text-[var(--primary)] text-sm font-medium hover:underline">
          Open Auditor Dashboard →
        </Link>
      </div>
    </main>
  );
}
