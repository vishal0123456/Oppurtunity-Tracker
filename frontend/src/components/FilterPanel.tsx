"use client";

import { OpportunityFilters } from "@/types/opportunity";
import clsx from "clsx";

interface Props {
    filters: OpportunityFilters;
    onChange: (filters: OpportunityFilters) => void;
}

const CATEGORIES = [
    { value: "", label: "All Categories" },
    { value: "scholarship", label: "Scholarship" },
    { value: "fellowship", label: "Fellowship" },
    { value: "accelerator", label: "Accelerator" },
    { value: "grant", label: "Grant" },
    { value: "competition", label: "Competition" },
    { value: "conference", label: "Conference" },
    { value: "exhibition", label: "Exhibition" },
    { value: "vc_program", label: "VC Program" },
    { value: "exchange_program", label: "Exchange Program" },
    { value: "travel_program", label: "Travel Program" },
    { value: "government_scheme", label: "Government Scheme" },
    { value: "giveaway", label: "Giveaway" },
];

const COUNTRIES = [
    "India", "USA", "UK", "Europe", "Singapore",
    "China", "South America", "New Zealand", "Middle East", "Africa", "Global",
];

const TAGS = [
    "AI", "Startup", "Women", "Research", "Engineering",
    "Climate", "Social Impact", "Hackathon", "Student", "Founder",
];

interface ToggleProps {
    label: string;
    checked: boolean;
    onChange: (v: boolean) => void;
}

function Toggle({ label, checked, onChange }: ToggleProps) {
    return (
        <label className="flex items-center gap-2 cursor-pointer select-none">
            <div
                role="switch"
                aria-checked={checked}
                onClick={() => onChange(!checked)}
                className={clsx(
                    "relative w-9 h-5 rounded-full transition-colors",
                    checked ? "bg-brand-600" : "bg-gray-200"
                )}
            >
                <span
                    className={clsx(
                        "absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform",
                        checked && "translate-x-4"
                    )}
                />
            </div>
            <span className="text-sm text-gray-700">{label}</span>
        </label>
    );
}

/**
 * FilterContent — the actual filter controls, usable standalone or inside a drawer.
 */
function FilterContent({ filters, onChange }: Props) {
    const update = (key: keyof OpportunityFilters, value: unknown) => {
        onChange({ ...filters, [key]: value || undefined, page: 1 });
    };

    return (
        <div className="space-y-5">
            {/* Category */}
            <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                    Category
                </label>
                <select
                    value={filters.category || ""}
                    onChange={(e) => update("category", e.target.value)}
                    className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
                    aria-label="Filter by category"
                >
                    {CATEGORIES.map((c) => (
                        <option key={c.value} value={c.value}>
                            {c.label}
                        </option>
                    ))}
                </select>
            </div>

            {/* Country */}
            <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                    Country / Region
                </label>
                <select
                    value={filters.country || ""}
                    onChange={(e) => update("country", e.target.value)}
                    className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
                    aria-label="Filter by country"
                >
                    <option value="">All Regions</option>
                    {COUNTRIES.map((c) => (
                        <option key={c} value={c}>
                            {c}
                        </option>
                    ))}
                </select>
            </div>

            {/* Tags */}
            <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                    Tags
                </label>
                <div className="flex flex-wrap gap-1.5">
                    {TAGS.map((tag) => (
                        <button
                            key={tag}
                            onClick={() => update("tag", filters.tag === tag ? "" : tag)}
                            className={clsx(
                                "px-2.5 py-1 text-xs rounded-full border transition-colors",
                                filters.tag === tag
                                    ? "bg-brand-600 text-white border-brand-600"
                                    : "bg-white text-gray-600 border-gray-200 hover:border-brand-400"
                            )}
                        >
                            {tag}
                        </button>
                    ))}
                </div>
            </div>

            {/* Eligibility toggles */}
            <div>
                <label className="block text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
                    Eligibility
                </label>
                <div className="space-y-2.5">
                    <Toggle
                        label="Women Friendly"
                        checked={!!filters.women_friendly}
                        onChange={(v) => update("women_friendly", v || undefined)}
                    />
                    <Toggle
                        label="India Eligible"
                        checked={!!filters.india_eligible}
                        onChange={(v) => update("india_eligible", v || undefined)}
                    />
                    <Toggle
                        label="Students"
                        checked={!!filters.student_eligible}
                        onChange={(v) => update("student_eligible", v || undefined)}
                    />
                    <Toggle
                        label="Remote / Online"
                        checked={!!filters.is_remote}
                        onChange={(v) => update("is_remote", v || undefined)}
                    />
                </div>
            </div>

            {/* Reset */}
            <button
                onClick={() => onChange({ is_expired: false, page: 1 })}
                className="w-full text-sm text-gray-500 hover:text-gray-700 underline"
            >
                Reset all filters
            </button>
        </div>
    );
}

/**
 * FilterPanel — desktop sticky sidebar wrapper around FilterContent.
 */
export default function FilterPanel({ filters, onChange }: Props) {
    return (
        <aside className="bg-white rounded-xl border border-gray-200 p-5 h-fit sticky top-4">
            <h2 className="font-semibold text-gray-900 mb-5">Filters</h2>
            <FilterContent filters={filters} onChange={onChange} />
        </aside>
    );
}

export { FilterContent };
