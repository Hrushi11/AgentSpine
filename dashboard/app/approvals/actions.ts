"use server";

import { revalidatePath } from "next/cache";

const API_URL = process.env.AGENTSPINE_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://server:8080";

async function resolve(approvalId: string, status: "approved" | "rejected", formData: FormData) {
  const comments = String(formData.get("comments") || "").trim();
  const response = await fetch(`${API_URL}/api/v1/approvals/${approvalId}/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, comments: comments || null }),
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Approval resolution failed: ${response.status}`);
  }

  revalidatePath("/approvals");
  revalidatePath("/actions");
  revalidatePath("/");
}

export async function approveApproval(approvalId: string, formData: FormData) {
  await resolve(approvalId, "approved", formData);
}

export async function rejectApproval(approvalId: string, formData: FormData) {
  await resolve(approvalId, "rejected", formData);
}
