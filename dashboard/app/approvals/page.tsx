import { getJson } from "../../lib/api";
import { approveApproval, rejectApproval } from "./actions";

type ApprovalItem = {
  id: string;
  action_id: string;
  status: string;
  approver_type: string;
  created_at: string;
  comments?: string | null;
};

export default async function ApprovalsPage() {
  const data = await getJson<{ items: ApprovalItem[] }>("/api/v1/approvals").catch(() => ({ items: [] }));

  return (
    <div className="grid">
      <section className="hero">
        <span className="meta">Approval inbox</span>
        <h1>Pending human review</h1>
        <p>
          This MVP view is intentionally read-heavy. Reviewers can see what is waiting and then resolve approvals via
          the server API or API client while richer mutation UX is added.
        </p>
      </section>

      <section className="card">
        <h2>Inbox</h2>
        {data.items.length === 0 ? (
          <div className="empty">No pending approvals.</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Approval</th>
                <th>Action</th>
                <th>Status</th>
                <th>Route</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((approval) => (
                <tr key={approval.id}>
                  <td className="mono">{approval.id}</td>
                  <td className="mono">{approval.action_id}</td>
                  <td>
                    <span className={`status ${approval.status}`}>{approval.status}</span>
                  </td>
                  <td>{approval.approver_type}</td>
                  <td>{new Date(approval.created_at).toLocaleString()}</td>
                  <td>
                    <form className="stack" action={approveApproval.bind(null, approval.id)}>
                      <input type="text" name="comments" placeholder="Optional note" />
                      <button type="submit">Approve</button>
                    </form>
                    <form className="stack" action={rejectApproval.bind(null, approval.id)}>
                      <input type="hidden" name="comments" value="Rejected from dashboard" />
                      <button type="submit">Reject</button>
                    </form>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
