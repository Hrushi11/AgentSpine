"use server";

import { revalidatePath } from "next/cache";

const API_URL = process.env.AGENTSPINE_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://server:8080";

export async function createPolicy(formData: FormData) {
  const name = String(formData.get("name") || "").trim();
  const action = String(formData.get("action") || "allow").trim();
  const actionType = String(formData.get("actionType") || "").trim();
  const scopeId = String(formData.get("scopeId") || "").trim();

  const response = await fetch(`${API_URL}/api/v1/policies`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      org_id: "default",
      name,
      action,
      scope_type: "workflow",
      scope_id: scopeId || null,
      priority: Number(formData.get("priority") || 0),
      is_active: true,
      condition: actionType ? { action_types: [actionType] } : {}
    }),
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Policy creation failed: ${response.status}`);
  }

  revalidatePath("/policies");
}

export async function deletePolicy(policyId: string) {
  const response = await fetch(`${API_URL}/api/v1/policies/${policyId}`, {
    method: "DELETE",
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Policy deletion failed: ${response.status}`);
  }

  revalidatePath("/policies");
}
