import Link from "next/link";
import { getJson } from "../lib/api";

type ApprovalItem = {
  id: string;
  status: string;
  action_id: string;
};

type ActionItem = {
  id: string;
  status: string;
  action_type: string;
  agent_id: string;
  workflow_id: string;
};

export default async function HomePage() {
  const approvals = await getJson<{ items: ApprovalItem[] }>("/api/v1/approvals").catch(() => ({ items: [] }));
  const actions = await getJson<{ items: ActionItem[] }>("/api/v1/actions?limit=8").catch(() => ({ items: [] }));

  const latest = actions.items[0];

  return (
    <div className="grid">
      <section className="hero">
        <span className="meta">Server mode dashboard</span>
        <h1>Review the actions your agents want to take before those actions become incidents.</h1>
        <p>
          AgentSpine keeps the SDK generic, routes side effects through a normalized execution boundary, and gives
          reviewers a thin control surface for approvals, timelines, and policy inspection.
        </p>
      </section>

      <section className="grid two">
        <article className="card">
          <h2>Approval Queue</h2>
          <p className="muted">Pending approvals currently waiting for a human decision.</p>
          <div className="stack">
            <div className="meta">{approvals.items.length} pending</div>
            <Link href="/approvals">Open approval inbox</Link>
          </div>
        </article>

        <article className="card">
          <h2>Latest Action</h2>
          {latest ? (
            <div className="stack">
              <div className={`status ${latest.status}`}>{latest.status}</div>
              <div className="mono">{latest.action_type}</div>
              <div className="muted">
                {latest.agent_id} in {latest.workflow_id}
              </div>
              <Link href="/actions">Inspect timeline</Link>
            </div>
          ) : (
            <div className="empty">No actions recorded yet.</div>
          )}
        </article>
      </section>

      <section className="card">
        <h2>Control Surface</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Area</th>
              <th>Purpose</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Approvals</td>
              <td>Inspect and resolve human-in-the-loop actions.</td>
            </tr>
            <tr>
              <td>Actions</td>
              <td>Browse the audit timeline and latest execution outcomes.</td>
            </tr>
            <tr>
              <td>Policies</td>
              <td>Review the active policy rules loaded into the control plane.</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  );
}
