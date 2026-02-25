"use client";

interface DocumentViewerProps {
  documentUrl: string | null;
  onDocumentLoad?: (url: string | null) => void;
  fileName?: string | null;
}

export function DocumentViewer({ documentUrl, onDocumentLoad, fileName }: DocumentViewerProps) {
  return (
    <div className="flex-1 flex items-center justify-center p-8 text-[var(--muted-foreground)]">
      {documentUrl ? (
        <iframe
          src={documentUrl}
          title="Uploaded document"
          className="w-full h-full rounded border-0 min-h-[300px]"
        />
      ) : fileName ? (
        <div className="text-center">
          <p className="text-sm text-[var(--foreground)] font-medium">Uploaded file</p>
          <p className="text-sm text-[var(--muted-foreground)] mt-1 break-all">{fileName}</p>
        </div>
      ) : (
        <p className="text-sm text-center">
          Document will appear here after you run verification from Upload & Verify.
        </p>
      )}
    </div>
  );
}
