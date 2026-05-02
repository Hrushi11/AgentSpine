import "./globals.css";
import Link from "next/link";
import type { ReactNode } from "react";

export const metadata = {
  title: "AgentSpine Dashboard",
  description: "Approval inbox, action timeline, and policy visibility for AgentSpine."
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <aside className="sidebar">
            <div className="brand">AgentSpine</div>
            <div className="muted">Adaptive control plane for agent actions.</div>
            <nav className="nav">
              <Link href="/">Overview</Link>
              <Link href="/approvals">Approvals</Link>
              <Link href="/actions">Actions</Link>
              <Link href="/policies">Policies</Link>
            </nav>
          </aside>
          <main className="content">{children}</main>
        </div>
      </body>
    </html>
  );
}
