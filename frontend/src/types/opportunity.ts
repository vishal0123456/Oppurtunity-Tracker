export type OpportunityCategory =
    | "scholarship"
    | "fellowship"
    | "accelerator"
    | "vc_program"
    | "grant"
    | "competition"
    | "conference"
    | "exhibition"
    | "exchange_program"
    | "travel_program"
    | "government_scheme"
    | "giveaway"
    | "other";

export type ApplicationStatus =
    | "saved"
    | "planning"
    | "applied"
    | "interview"
    | "accepted"
    | "rejected"
    | "waitlisted";

export interface Opportunity {
    id: string;
    title: string;
    organization: string | null;
    description: string | null;
    category: OpportunityCategory;
    tags: string[];
    country: string[];
    is_remote: boolean;
    women_friendly: boolean;
    india_eligible: boolean;
    student_eligible: boolean;
    age_limit: string | null;
    eligibility: string | null;
    funding_amount: string | null;
    application_fee: string | null;
    link: string;
    source_name: string | null;
    deadline: string | null; // ISO date string
    is_expired: boolean;
    created_at: string;
    updated_at: string;
}

export interface OpportunityListResponse {
    total: number;
    page: number;
    page_size: number;
    results: Opportunity[];
}

export interface Application {
    id: string;
    opportunity_id: string;
    status: ApplicationStatus;
    notes: string | null;
    priority: number;
    applied_at: string | null;
    reminder_date: string | null;
    document_links: string | null;
    created_at: string;
    updated_at: string;
    opportunity: Opportunity | null;
}

export interface OpportunityFilters {
    search?: string;
    category?: string;
    country?: string;
    tag?: string;
    women_friendly?: boolean;
    india_eligible?: boolean;
    student_eligible?: boolean;
    is_remote?: boolean;
    is_expired?: boolean;
    page?: number;
    page_size?: number;
}
