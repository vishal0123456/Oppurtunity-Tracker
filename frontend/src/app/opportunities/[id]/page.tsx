"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getOpportunity, createApplication } from "@/lib/api";
import type { Opportunity } from "@/types/opportunity";
import {
    ArrowLeft, ExternalLink, Calendar, MapPin, Tag,
    Users, DollarSign, Globe, Bookmark, Loader2, AlertCircle
} from "lucide-react";
import { format, parseISO, differenceInDays, isPast } from "date-fns";
import clsx from "clsx";
import Link from "next/link";

function InfoRow({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
    return (
        <div className="flex items-start gap-3 py-3 border-b border-gray-100 last:border-0">
            <span className="text-gray-400 mt-0.5">{icon}</span>
            <div>
                <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">{label}</p>
                <p className="text-sm text-gray-900 mt-0.5">{value}</p>
            </div>
        </div>
    );
}

export default function OpportunityDetailPage() {
    const { id } = useParams<{ id: string }>();
    const router = useRouter();
    const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [saved, setSaved] = useState(false);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        getOpportunity(id)
            .then(setOpportunity)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false));
    }, [id]);

    const handleSave = async () => {
        if (!opportunity || saved) return;
        setSaving(true);
        try {
            await createApplication({ opportunity_id: opportunity.id, status: "saved" });
            setSaved(true);
        } catch {
            setSaved(true); // Might already be saved
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-20">
                <Loader2 size={32} className="animate-spin text-brand-500" />
            </div>
        );
    }

    if (error || !opportunity) {
        return (
            <div className="flex items-center gap-3 p-4 bg-red-50 text-red-700 rounded-xl max-w-lg mx-auto mt-8">
                <AlertCircle size={20} />
                <p>{error || "Opportunity not found"}</p>
            </div>
        );
    }

    const deadlineDays = opportunity.deadline
        ? differenceInDays(parseISO(opportunity.deadline), new Date())
        : null;
    const isExpired = opportunity.deadline ? isPast(parseISO(opportunity.deadline)) : false;

    const deadlineColor = isExpired
        ? "text-gray-400"
        : deadlineDays !== null && deadlineDays <= 7
            ? "text-red-600"
            : deadlineDays !== null && deadlineDays <= 30
                ? "text-amber-600"
                : "text-green-600";

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Back */}
            <button
                onClick={() => router.back()}
                className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900"
            >
                <ArrowLeft size={16} /> Back
            </button>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main content */}
                <div className="lg:col-span-2 space-y-5">
                    <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
                        {/* Header */}
                        <div>
                            <span className="inline-block px-2.5 py-0.5 bg-brand-100 text-brand-700 text-xs font-medium rounded-full capitalize mb-2">
                                {opportunity.category.replace(/_/g, " ")}
                            </span>
                            <h1 className="text-2xl font-bold text-gray-900 leading-tight">
                                {opportunity.title}
                            </h1>
                            {opportunity.organization && (
                                <p className="text-gray-500 mt-1">{opportunity.organization}</p>
                            )}
                        </div>

                        {/* Description */}
                        {opportunity.description && (
                            <div>
                                <h2 className="font-semibold text-gray-900 mb-2">About</h2>
                                <p className="text-gray-600 leading-relaxed">{opportunity.description}</p>
                            </div>
                        )}

                        {/* Eligibility */}
                        {opportunity.eligibility && (
                            <div>
                                <h2 className="font-semibold text-gray-900 mb-2">Eligibility</h2>
                                <p className="text-gray-600 leading-relaxed">{opportunity.eligibility}</p>
                            </div>
                        )}

                        {/* Tags */}
                        {opportunity.tags.length > 0 && (
                            <div>
                                <h2 className="font-semibold text-gray-900 mb-2">Tags</h2>
                                <div className="flex flex-wrap gap-2">
                                    {opportunity.tags.map((tag) => (
                                        <span
                                            key={tag}
                                            className="flex items-center gap-1 px-2.5 py-1 bg-gray-100 text-gray-700 text-sm rounded-full"
                                        >
                                            <Tag size={12} />
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Sidebar */}
                <div className="space-y-4">
                    {/* Action card */}
                    <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-3">
                        {/* Deadline */}
                        {opportunity.deadline && (
                            <div className={clsx("text-center py-3 rounded-lg bg-gray-50", deadlineColor)}>
                                <p className="text-xs font-medium uppercase tracking-wide text-gray-500">Deadline</p>
                                <p className="font-bold text-lg mt-0.5">
                                    {format(parseISO(opportunity.deadline), "MMM d, yyyy")}
                                </p>
                                <p className="text-sm">
                                    {isExpired ? "Expired" : `${deadlineDays} days left`}
                                </p>
                            </div>
                        )}

                        <a
                            href={opportunity.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center justify-center gap-2 w-full py-2.5 bg-brand-600 text-white font-medium rounded-lg hover:bg-brand-700 transition-colors"
                        >
                            Apply Now <ExternalLink size={15} />
                        </a>

                        <button
                            onClick={handleSave}
                            disabled={saved || saving}
                            className={clsx(
                                "flex items-center justify-center gap-2 w-full py-2.5 border rounded-lg font-medium transition-colors",
                                saved
                                    ? "border-brand-200 text-brand-600 bg-brand-50"
                                    : "border-gray-200 text-gray-700 hover:bg-gray-50"
                            )}
                        >
                            <Bookmark size={15} fill={saved ? "currentColor" : "none"} />
                            {saved ? "Saved to Tracker" : "Save to Tracker"}
                        </button>

                        <Link
                            href="/tracker"
                            className="block text-center text-sm text-brand-600 hover:underline"
                        >
                            View My Tracker →
                        </Link>
                    </div>

                    {/* Details card */}
                    <div className="bg-white rounded-xl border border-gray-200 p-5">
                        <h2 className="font-semibold text-gray-900 mb-1">Details</h2>
                        <div>
                            {opportunity.country.length > 0 && (
                                <InfoRow
                                    icon={<MapPin size={16} />}
                                    label="Countries"
                                    value={opportunity.country.join(", ")}
                                />
                            )}
                            {opportunity.funding_amount && (
                                <InfoRow
                                    icon={<DollarSign size={16} />}
                                    label="Funding"
                                    value={opportunity.funding_amount}
                                />
                            )}
                            {opportunity.age_limit && (
                                <InfoRow
                                    icon={<Users size={16} />}
                                    label="Age Limit"
                                    value={opportunity.age_limit}
                                />
                            )}
                            {opportunity.application_fee && (
                                <InfoRow
                                    icon={<DollarSign size={16} />}
                                    label="Application Fee"
                                    value={opportunity.application_fee}
                                />
                            )}
                            <InfoRow
                                icon={<Globe size={16} />}
                                label="Format"
                                value={opportunity.is_remote ? "Remote / Online" : "In-person"}
                            />
                        </div>

                        {/* Eligibility badges */}
                        <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-gray-100">
                            {opportunity.women_friendly && (
                                <span className="px-2 py-0.5 bg-pink-50 text-pink-700 text-xs rounded-full">Women Friendly</span>
                            )}
                            {opportunity.india_eligible && (
                                <span className="px-2 py-0.5 bg-orange-50 text-orange-700 text-xs rounded-full">India Eligible</span>
                            )}
                            {opportunity.student_eligible && (
                                <span className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full">Students Welcome</span>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
