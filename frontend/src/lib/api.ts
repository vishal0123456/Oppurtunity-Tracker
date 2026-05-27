/**
 * Typed API client for the Opportunity Tracker backend.
 */
import type {
    Opportunity,
    OpportunityListResponse,
    OpportunityFilters,
    Application,
} from "@/types/opportunity";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(error.detail || `API error ${res.status}`);
    }

    return res.json();
}

function buildQueryString(params: Record<string, unknown>): string {
    const qs = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && value !== "") {
            qs.append(key, String(value));
        }
    }
    const str = qs.toString();
    return str ? `?${str}` : "";
}

// ─── Opportunities ────────────────────────────────────────────────────────────

export async function getOpportunities(
    filters: OpportunityFilters = {}
): Promise<OpportunityListResponse> {
    const qs = buildQueryString(filters as Record<string, unknown>);
    return apiFetch<OpportunityListResponse>(`/opportunities${qs}`);
}

export async function searchOpportunities(
    query: string,
    page = 1,
    pageSize = 20
): Promise<OpportunityListResponse> {
    const qs = buildQueryString({ q: query, page, page_size: pageSize });
    return apiFetch<OpportunityListResponse>(`/opportunities/search${qs}`);
}

export async function getOpportunity(id: string): Promise<Opportunity> {
    return apiFetch<Opportunity>(`/opportunities/${id}`);
}

export async function triggerPipeline(): Promise<{ message: string }> {
    return apiFetch<{ message: string }>("/opportunities/run-pipeline", {
        method: "POST",
    });
}

export async function getStats(): Promise<{
    total: number;
    active: number;
    expiring_soon: number;
    by_category: { category: string; count: number }[];
}> {
    return apiFetch("/opportunities/stats");
}

// ─── Applications ─────────────────────────────────────────────────────────────

export async function getApplications(status?: string): Promise<Application[]> {
    const qs = status ? `?status=${status}` : "";
    return apiFetch<Application[]>(`/applications${qs}`);
}

export async function createApplication(data: {
    opportunity_id: string;
    status?: string;
    notes?: string;
    priority?: number;
}): Promise<Application> {
    return apiFetch<Application>("/applications", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export async function updateApplication(
    id: string,
    data: Partial<{
        status: string;
        notes: string;
        priority: number;
        applied_at: string;
        reminder_date: string;
        document_links: string;
    }>
): Promise<Application> {
    return apiFetch<Application>(`/applications/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
}

export async function deleteApplication(id: string): Promise<void> {
    await apiFetch<void>(`/applications/${id}`, { method: "DELETE" });
}
