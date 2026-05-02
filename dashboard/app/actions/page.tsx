import { getJson } from "../../lib/api";

type ActionItem = {
  id: string;
  status: string;
  action_type: string;
  workflow_id: string;
  agent_id: string;
  risk_score?: number | null;
  execution_duration_ms?: number | null;
  created_at: string;
};

export default async function ActionsPage() {
  const data = await getJson<{ items: ActionItem[] }>("/api/v1/actions?limit=50").catch(() => ({ items: [] }));

  return (
    <div className="grid">
      <section className="hero">
        <span className="meta">Action timeline</span>
        <h1>Recent action history</h1>
        <p>
          Every action is persisted as an append-only timeline with policy, risk, approval, and execution events. This
          table gives reviewers and operators a fast read on what the system is doing.
        </p>
      </section>

      <section className="card">
        <h2>Actions</h2>
        {data.items.length === 0 ? (
          <div className="empty">No actions recorded yet.</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Action</th>
                <th>Status</th>
                <th>Workflow</th>
                <th>Agent</th>
                <th>Risk</th>
                <th>Latency</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((action) => (
                <tr key={action.id}>
                  <td>
                    <div className="mono">{action.action_type}</div>
                    <div className="muted mono">{action.id}</div>
                  </td>
                  <td>
                    <span className={`status ${action.status}`}>{action.status}</span>
                  </td>
                  <td>{action.workflow_id}</td>
                  <td>{action.agent_id}</td>
                  <td>{action.risk_score ?? "-"}</td>
                  <td>{action.execution_duration_ms ? `${action.execution_duration_ms} ms` : "-"}</td>
                  <td>{new Date(action.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
