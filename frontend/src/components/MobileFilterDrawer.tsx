"use client";

import { useState } from "react";
import { SlidersHorizontal, X } from "lucide-react";
import { FilterContent } from "./FilterPanel";
import type { OpportunityFilters } from "@/types/opportunity";

interface Props {
    filters: OpportunityFilters;
    onChange: (filters: OpportunityFilters) => void;
}

export default function MobileFilterDrawer({ filters, onChange }: Props) {
    const [open, setOpen] = useState(false);

    // Count active filters (excluding defaults)
    const activeCount = [
        filters.category,
        filters.country,
        filters.tag,
        filters.women_friendly,
        filters.india_eligible,
        filters.student_eligible,
        filters.is_remote,
    ].filter(Boolean).length;

    return (
        <>
            {/* Trigger button — only visible on mobile */}
            <button
                onClick={() => setOpen(true)}
                className="lg:hidden flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 shadow-sm"
                aria-label="Open filters"
            >
                <SlidersHorizontal size={16} />
                Filters
                {activeCount > 0 && (
                    <span className="ml-1 px-1.5 py-0.5 bg-brand-600 text-white text-xs rounded-full">
                        {activeCount}
                    </span>
                )}
            </button>

            {/* Backdrop */}
            {open && (
                <div
                    className="fixed inset-0 bg-black/40 z-40 lg:hidden"
                    onClick={() => setOpen(false)}
                    aria-hidden="true"
                />
            )}

            {/* Drawer */}
            <div
                className={`fixed inset-y-0 left-0 z-50 w-80 bg-white shadow-xl transform transition-transform duration-300 lg:hidden overflow-y-auto ${open ? "translate-x-0" : "-translate-x-full"
                    }`}
                role="dialog"
                aria-modal="true"
                aria-label="Filters"
            >
                {/* Drawer header */}
                <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
                    <h2 className="font-semibold text-gray-900">Filters</h2>
                    <button
                        onClick={() => setOpen(false)}
                        className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-500"
                        aria-label="Close filters"
                    >
                        <X size={18} />
                    </button>
                </div>

                {/* Filter content — reuse FilterContent without the sticky/border wrapper */}
                <div className="p-5">
                    <FilterContent
                        filters={filters}
                        onChange={(f) => {
                            onChange(f);
                            setOpen(false);
                        }}
                    />
                </div>
            </div>
        </>
    );
}
