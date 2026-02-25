import Link from "next/link";

export default function HomePage() {
  return (
    <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20">
      <div className="text-center mb-16">
        <p className="text-[var(--primary)] font-medium text-sm uppercase tracking-wider mb-2">Portfolio project</p>
        <h1 className="text-4xl sm:text-5xl font-bold text-[var(--foreground)] mb-4 tracking-tight">
          Veriflow — ACE
        </h1>
        <p className="text-xl text-[var(--muted-foreground)] max-w-2xl mx-auto leading-relaxed">
          Autonomous Compliance Engine: decision support for product compliance. Every finding is traceable to a specific clause; auditors approve or reject with full audit trail.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 gap-6 mb-12">
        <Link
          href="/upload"
          className="block rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--card)] p-6 sm:p-8 shadow-[var(--shadow)] hover:shadow-[var(--shadow-lg)] hover:border-[var(--primary)]/40 transition-all duration-200"
        >
          <h2 className="text-lg font-semibold text-[var(--foreground)] mb-2">Upload & Verify</h2>
          <p className="text-sm text-[var(--muted-foreground)]">
            Upload a BOM (CSV or Excel). The system extracts data and runs deterministic verification against UL 60335-1 with full source citations.
          </p>
          <span className="inline-block mt-3 text-[var(--primary)] font-medium text-sm">Upload BOM →</span>
        </Link>
        <Link
          href="/dashboard"
          className="block rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--card)] p-6 sm:p-8 shadow-[var(--shadow)] hover:shadow-[var(--shadow-lg)] hover:border-[var(--primary)]/40 transition-all duration-200"
        >
          <h2 className="text-lg font-semibold text-[var(--foreground)] mb-2">Auditor Dashboard</h2>
          <p className="text-sm text-[var(--muted-foreground)]">
            Review AI findings side-by-side with the uploaded document. Approve or reject each finding; every decision is logged for governance.
          </p>
          <span className="inline-block mt-3 text-[var(--primary)] font-medium text-sm">Open dashboard →</span>
        </Link>
      </div>

      <div className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--card)] p-6 sm:p-8 shadow-[var(--shadow)]">
        <h3 className="font-semibold text-[var(--foreground)] mb-3">How it works</h3>
        <ul className="space-y-2 text-sm text-[var(--muted-foreground)]">
          <li className="flex gap-2"><span className="text-[var(--primary)]">1.</span> Upload a BOM with voltage, clearance, creepage; optional: rated_voltage_v, insulation_type, ip_code.</li>
          <li className="flex gap-2"><span className="text-[var(--primary)]">2.</span> Engine applies UL 60335-1 rules: <strong className="text-[var(--foreground)]">7</strong> (rated voltage), <strong className="text-[var(--foreground)]">8.1</strong> (accessibility / IP), <strong className="text-[var(--foreground)]">29.1</strong> (clearance), <strong className="text-[var(--foreground)]">29.2</strong> (creepage); reinforced insulation uses 2× minimums.</li>
          <li className="flex gap-2"><span className="text-[var(--primary)]">3.</span> Deterministic comparison: actual vs required (no AI guessing — math and logic only).</li>
          <li className="flex gap-2"><span className="text-[var(--primary)]">4.</span> Each finding includes <strong className="text-[var(--foreground)]">source_reference</strong> (standard + clause + table).</li>
          <li className="flex gap-2"><span className="text-[var(--primary)]">5.</span> Auditors approve or reject; results &lt; 90% confidence are flagged for manual review.</li>
        </ul>
      </div>
    </main>
  );
}
