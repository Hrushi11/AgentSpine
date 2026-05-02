import { getJson } from "../../lib/api";
import { createPolicy, deletePolicy } from "./actions";

type PolicyItem = {
  id: string;
  name: string;
  action: string;
  scope_type: string;
  scope_id?: string | null;
  priority: number;
  is_active: boolean;
};

export default async function PoliciesPage() {
  const data = await getJson<{ items: PolicyItem[] }>("/api/v1/policies").catch(() => ({ items: [] }));

  return (
    <div className="grid">
      <section className="hero">
        <span className="meta">Policy inspection</span>
        <h1>Active control rules</h1>
        <p>
          Policies stay generic and data-driven. The SDK does not know about Gmail, CRMs, or ticketing providers; it
          only evaluates action metadata against these rules and emits normalized execution signals downstream.
        </p>
      </section>

      <section className="card">
        <h2>Create policy</h2>
        <form className="policy-form" action={createPolicy}>
          <div className="policy-form-grid">
            <input type="text" name="name" placeholder="Policy name" required />
            <input type="text" name="actionType" placeholder="Action type, e.g. billing.refund" />
            <input type="text" name="scopeId" placeholder="Workflow scope id" />
            <input type="number" name="priority" placeholder="Priority" defaultValue={0} />
            <select name="action" defaultValue="require_approval">
              <option value="allow">allow</option>
              <option value="deny">deny</option>
              <option value="require_approval">require_approval</option>
            </select>
          </div>
          <button type="submit">Save policy</button>
        </form>
      </section>

      <section className="card">
        <h2>Policies</h2>
        {data.items.length === 0 ? (
          <div className="empty">No policies configured yet.</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Decision</th>
                <th>Scope</th>
                <th>Priority</th>
                <th>Active</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((policy) => (
                <tr key={policy.id}>
                  <td>
                    <div>{policy.name}</div>
                    <div className="muted mono">{policy.id}</div>
                  </td>
                  <td className="mono">{policy.action}</td>
                  <td>
                    {policy.scope_type}
                    {policy.scope_id ? `:${policy.scope_id}` : ""}
                  </td>
                  <td>{policy.priority}</td>
                  <td>{policy.is_active ? "yes" : "no"}</td>
                  <td>
                    <form action={deletePolicy.bind(null, policy.id)}>
                      <button type="submit">Delete</button>
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
