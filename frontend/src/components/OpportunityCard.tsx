"use client";

import { Opportunity } from "@/types/opportunity";
import { formatDistanceToNow, parseISO, isPast, differenceInDays } from "date-fns";
import { ExternalLink, Calendar, MapPin, Tag, Bookmark } from "lucide-react";
import clsx from "clsx";
import Link from "next/link";

interface Props {
    opportunity: Opportunity;
    onSave?: (id: string) => void;
    isSaved?: boolean;
}

const CATEGORY_COLORS: Record<string, string> = {
    scholarship: "bg-blue-100 text-blue-800",
    fellowship: "bg-purple-100 text-purple-800",
    accelerator: "bg-orange-100 text-orange-800",
    vc_program: "bg-yellow-100 text-yellow-800",
    grant: "bg-green-100 text-green-800",
    competition: "bg-red-100 text-red-800",
    conference: "bg-indigo-100 text-indigo-800",
    exhibition: "bg-violet-100 text-violet-800",
    exchange_program: "bg-teal-100 text-teal-800",
    travel_program: "bg-cyan-100 text-cyan-800",
    government_scheme: "bg-gray-100 text-gray-800",
    giveaway: "bg-pink-100 text-pink-800",
    other: "bg-slate-100 text-slate-800",
};

function DeadlineBadge({ deadline }: { deadline: string | null }) {
    if (!deadline) return null;

    const deadlineDate = parseISO(deadline);
    const daysLeft = differenceInDays(deadlineDate, new Date());
    const isExpired = isPast(deadlineDate);

    const colorClass = isExpired
        ? "text-gray-400"
        : daysLeft <= 7
            ? "text-red-600 font-semibold"
            : daysLeft <= 30
                ? "text-amber-600"
                : "text-green-600";

    return (
        <span className={clsx("flex items-center gap-1 text-sm", colorClass)}>
            <Calendar size={14} />
            {isExpired
                ? "Expired"
                : daysLeft === 0
                    ? "Due today"
                    : `${daysLeft}d left`}
        </span>
    );
}

export default function OpportunityCard({ opportunity, onSave, isSaved }: Props) {
    const categoryColor = CATEGORY_COLORS[opportunity.category] || CATEGORY_COLORS.other;
    const categoryLabel = opportunity.category.replace(/_/g, " ");

    return (
        <div
            className={clsx(
                "bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow flex flex-col gap-3",
                opportunity.is_expired && "opacity-60"
            )}
        >
            {/* Header */}
            <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                    <Link
                        href={`/opportunities/${opportunity.id}`}
                        className="font-semibold text-gray-900 hover:text-brand-600 line-clamp-2 leading-snug"
                    >
                        {opportunity.title}
                    </Link>
                    {opportunity.organization && (
                        <p className="text-sm text-gray-500 mt-0.5">{opportunity.organization}</p>
                    )}
                </div>
                <button
                    onClick={() => onSave?.(opportunity.id)}
                    aria-label={isSaved ? "Unsave opportunity" : "Save opportunity"}
                    className={clsx(
                        "p-1.5 rounded-lg transition-colors flex-shrink-0",
                        isSaved
                            ? "text-brand-600 bg-brand-50"
                            : "text-gray-400 hover:text-brand-600 hover:bg-brand-50"
                    )}
                >
                    <Bookmark size={18} fill={isSaved ? "currentColor" : "none"} />
                </button>
            </div>

            {/* Description */}
            {opportunity.description && (
                <p className="text-sm text-gray-600 line-clamp-2">{opportunity.description}</p>
            )}

            {/* Meta row */}
            <div className="flex flex-wrap items-center gap-2 text-sm">
                <span className={clsx("px-2 py-0.5 rounded-full text-xs font-medium capitalize", categoryColor)}>
                    {categoryLabel}
                </span>

                {opportunity.country.length > 0 && (
                    <span className="flex items-center gap-1 text-gray-500">
                        <MapPin size={13} />
                        {opportunity.country.slice(0, 2).join(", ")}
                        {opportunity.country.length > 2 && ` +${opportunity.country.length - 2}`}
                    </span>
                )}

                {opportunity.funding_amount && (
                    <span className="text-green-700 font-medium">{opportunity.funding_amount}</span>
                )}

                <DeadlineBadge deadline={opportunity.deadline} />
            </div>

            {/* Eligibility badges */}
            <div className="flex flex-wrap gap-1.5">
                {opportunity.women_friendly && (
                    <span className="px-2 py-0.5 bg-pink-50 text-pink-700 text-xs rounded-full">Women ✓</span>
                )}
                {opportunity.india_eligible && (
                    <span className="px-2 py-0.5 bg-orange-50 text-orange-700 text-xs rounded-full">India ✓</span>
                )}
                {opportunity.student_eligible && (
                    <span className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full">Students ✓</span>
                )}
                {opportunity.is_remote && (
                    <span className="px-2 py-0.5 bg-teal-50 text-teal-700 text-xs rounded-full">Remote</span>
                )}
            </div>

            {/* Tags */}
            {opportunity.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                    {opportunity.tags.slice(0, 4).map((tag) => (
                        <span key={tag} className="flex items-center gap-0.5 px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">
                            <Tag size={10} />
                            {tag}
                        </span>
                    ))}
                    {opportunity.tags.length > 4 && (
                        <span className="px-2 py-0.5 bg-gray-100 text-gray-500 text-xs rounded-full">
                            +{opportunity.tags.length - 4}
                        </span>
                    )}
                </div>
            )}

            {/* Footer */}
            <div className="flex items-center justify-between pt-1 border-t border-gray-100">
                <span className="text-xs text-gray-400">
                    {opportunity.source_name || "Web"}
                </span>
                <a
                    href={opportunity.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-sm text-brand-600 hover:text-brand-700 font-medium"
                >
                    Apply <ExternalLink size={13} />
                </a>
            </div>
        </div>
    );
}
