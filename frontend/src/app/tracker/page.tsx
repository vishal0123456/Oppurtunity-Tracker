"use client";

import { useEffect, useState } from "react";
import { getApplications, updateApplication, deleteApplication } from "@/lib/api";
import type { Application, ApplicationStatus } from "@/types/opportunity";
import { format, parseISO } from "date-fns";
import {
    ExternalLink, Trash2, ChevronDown, Loader2, AlertCircle,
    BookOpen, Calendar, Link2, ChevronUp,
} from "lucide-react";
import clsx from "clsx";
import Link from "next/link";

const STATUSES: { value: ApplicationStatus; label: string; color: string }[] = [
    { value: "saved", label: "Saved", color: "bg-gray-100 text-gray-700" },
    { value: "planning", label: "Planning", color: "bg-blue-100 text-blue-700" },
    { value: "applied", label: "Applied", color: "bg-yellow-100 text-yellow-700" },
    { value: "interview", label: "Interview", color: "bg-purple-100 text-purple-700" },
    { value: "accepted", label: "Accepted", color: "bg-green-100 text-green-700" },
    { value: "rejected", label: "Rejected", color: "bg-red-100 text-red-700" },
    { value: "waitlisted", label: "Waitlisted", color: "bg-orange-100 text-orange-700" },
];

function StatusBadge({ status }: { status: ApplicationStatus }) {
    const s = STATUSES.find((s) => s.value === status);
    return (
        <span className={clsx("px-2.5 py-0.5 text-xs font-medium rounded-full", s?.color)}>
            {s?.label || status}
        </span>
    );
}

function ApplicationRow({
    app,
    onUpdate,
    onDelete,
}: {
    app: Application;
    onUpdate: (id: string, data: Partial<Application>) => void;
    onDelete: (id: string) => void;
}) {
    const [notes, setNotes] = useState(app.notes || "");
    const [editingNotes, setEditingNotes] = useState(false);
    const [showDetails, setShowDetails] = useState(false);

    // Local state for date/link fields
    const [appliedAt, setAppliedAt] = useState(app.applied_at || "");
    const [reminderDate, setReminderDate] = useState(app.reminder_date || "");
    const [docLinks, setDocLinks] = useState(app.document_links || "");
    const [editingLinks, setEditingLinks] = useState(false);

    const opp = app.opportunity;
    if (!opp) return null;

    const handleDateBlur = (field: "applied_at" | "reminder_date", value: string) => {
        onUpdate(app.id, { [field]: value || undefined });
    };

    return (
        <div className="bg-white rounded-xl border border-gray-200 p-5 space-y-3">
            {/* Header */}
            <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                    <Link
                        href={`/opportunities/${opp.id}`}
                        className="font-semibold text-gray-900 hover:text-brand-600 line-clamp-1"
                    >
                        {opp.title}
                    </Link>
                    {opp.organization && (
                        <p className="text-sm text-gray-500">{opp.organization}</p>
                    )}
                </div>
                <button
                    onClick={() => onDelete(app.id)}
                    className="text-gray-300 hover:text-red-500 transition-colors p-1"
                    aria-label="Remove from tracker"
                >
                    <Trash2 size={16} />
                </button>
            </div>

            {/* Status + deadline row */}
            <div className="flex flex-wrap items-center gap-3">
                {/* Status selector */}
                <div className="relative">
                    <select
                        value={app.status}
                        onChange={(e) => onUpdate(app.id, { status: e.target.value as ApplicationStatus })}
                        className="appearance-none pl-3 pr-8 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 bg-white"
                        aria-label="Application status"
                    >
                        {STATUSES.map((s) => (
                            <option key={s.value} value={s.value}>
                                {s.label}
                            </option>
                        ))}
                    </select>
                    <ChevronDown size={14} className="absolute right-2 top-2.5 text-gray-400 pointer-events-none" />
                </div>

                <StatusBadge status={app.status} />

                {opp.deadline && (
                    <span className="text-sm text-gray-500">
                        Deadline: {format(parseISO(opp.deadline), "MMM d, yyyy")}
                    </span>
                )}

                {/* Priority */}
                <div className="flex items-center gap-1.5 ml-auto">
                    <span className="text-xs text-gray-400">Priority:</span>
                    <select
                        value={app.priority}
                        onChange={(e) => onUpdate(app.id, { priority: Number(e.target.value) })}
                        className="text-sm border border-gray-200 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-brand-500"
                        aria-label="Priority"
                    >
                        {[1, 2, 3, 4, 5].map((p) => (
                            <option key={p} value={p}>
                                {p === 1 ? "🔴 High" : p === 2 ? "🟠 Med-High" : p === 3 ? "🟡 Medium" : p === 4 ? "🟢 Low" : "⚪ Lowest"}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Notes */}
            <div>
                {editingNotes ? (
                    <div className="space-y-2">
                        <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            placeholder="Add notes..."
                            rows={3}
                            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none"
                            aria-label="Application notes"
                        />
                        <div className="flex gap-2">
                            <button
                                onClick={() => {
                                    onUpdate(app.id, { notes });
                                    setEditingNotes(false);
                                }}
                                className="px-3 py-1 bg-brand-600 text-white text-sm rounded-lg hover:bg-brand-700"
                            >
                                Save
                            </button>
                            <button
                                onClick={() => {
                                    setNotes(app.notes || "");
                                    setEditingNotes(false);
                                }}
                                className="px-3 py-1 border border-gray-200 text-sm rounded-lg hover:bg-gray-50"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                ) : (
                    <button
                        onClick={() => setEditingNotes(true)}
                        className="text-sm text-gray-400 hover:text-gray-600 italic text-left w-full"
                    >
                        {notes || "Add notes..."}
                    </button>
                )}
            </div>

            {/* Expandable details section */}
            <div>
                <button
                    onClick={() => setShowDetails((v) => !v)}
                    className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600"
                >
                    {showDetails ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                    {showDetails ? "Hide details" : "Dates & links"}
                </button>

                {showDetails && (
                    <div className="mt-3 space-y-3 border-t border-gray-100 pt-3">
                        {/* Applied date */}
                        <div className="flex items-center gap-3">
                            <Calendar size={14} className="text-gray-400 flex-shrink-0" />
                            <div className="flex-1">
                                <label className="block text-xs text-gray-500 mb-1">Applied on</label>
                                <input
                                    type="date"
                                    value={appliedAt}
                                    onChange={(e) => setAppliedAt(e.target.value)}
                                    onBlur={(e) => handleDateBlur("applied_at", e.target.value)}
                                    className="text-sm border border-gray-200 rounded-lg px-2 py-1 focus:outline-none focus:ring-1 focus:ring-brand-500 w-full"
                                    aria-label="Date applied"
                                />
                            </div>
                        </div>

                        {/* Reminder date */}
                        <div className="flex items-center gap-3">
                            <Calendar size={14} className="text-amber-400 flex-shrink-0" />
                            <div className="flex-1">
                                <label className="block text-xs text-gray-500 mb-1">Reminder date</label>
                                <input
                                    type="date"
                                    value={reminderDate}
                                    onChange={(e) => setReminderDate(e.target.value)}
                                    onBlur={(e) => handleDateBlur("reminder_date", e.target.value)}
                                    className="text-sm border border-gray-200 rounded-lg px-2 py-1 focus:outline-none focus:ring-1 focus:ring-brand-500 w-full"
                                    aria-label="Reminder date"
                                />
                            </div>
                        </div>

                        {/* Document links */}
                        <div className="flex items-start gap-3">
                            <Link2 size={14} className="text-gray-400 flex-shrink-0 mt-1" />
                            <div className="flex-1">
                                <label className="block text-xs text-gray-500 mb-1">
                                    Document links (one per line)
                                </label>
                                {editingLinks ? (
                                    <div className="space-y-2">
                                        <textarea
                                            value={docLinks}
                                            onChange={(e) => setDocLinks(e.target.value)}
                                            placeholder="https://drive.google.com/..."
                                            rows={3}
                                            className="w-full text-sm border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-brand-500 resize-none"
                                            aria-label="Document links"
                                        />
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => {
                                                    onUpdate(app.id, { document_links: docLinks });
                                                    setEditingLinks(false);
                                                }}
                                                className="px-2.5 py-1 bg-brand-600 text-white text-xs rounded-lg hover:bg-brand-700"
                                            >
                                                Save
                                            </button>
                                            <button
                                                onClick={() => {
                                                    setDocLinks(app.document_links || "");
                                                    setEditingLinks(false);
                                                }}
                                                className="px-2.5 py-1 border border-gray-200 text-xs rounded-lg hover:bg-gray-50"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <div>
                                        {docLinks ? (
                                            <div className="space-y-1">
                                                {docLinks.split("\n").filter(Boolean).map((link, i) => (
                                                    <a
                                                        key={i}
                                                        href={link.trim()}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="block text-xs text-brand-600 hover:underline truncate"
                                                    >
                                                        {link.trim()}
                                                    </a>
                                                ))}
                                            </div>
                                        ) : null}
                                        <button
                                            onClick={() => setEditingLinks(true)}
                                            className="text-xs text-gray-400 hover:text-gray-600 italic mt-1"
                                        >
                                            {docLinks ? "Edit links" : "Add document links..."}
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                <span className="text-xs text-gray-400">
                    Saved {format(parseISO(app.created_at), "MMM d, yyyy")}
                </span>
                <a
                    href={opp.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-sm text-brand-600 hover:text-brand-700"
                >
                    Open <ExternalLink size={13} />
                </a>
            </div>
        </div>
    );
}

export default function TrackerPage() {
    const [applications, setApplications] = useState<Application[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeStatus, setActiveStatus] = useState<string>("all");

    useEffect(() => {
        getApplications()
            .then(setApplications)
            .catch((e) => setError(e.message))
            .finally(() => setLoading(false));
    }, []);

    const handleUpdate = async (id: string, data: Partial<Application>) => {
        try {
            const updated = await updateApplication(id, data);
            setApplications((prev) => prev.map((a) => (a.id === id ? updated : a)));
        } catch (e) {
            console.error("Update failed:", e);
        }
    };

    const handleDelete = async (id: string) => {
        try {
            await deleteApplication(id);
            setApplications((prev) => prev.filter((a) => a.id !== id));
        } catch (e) {
            console.error("Delete failed:", e);
        }
    };

    const filtered =
        activeStatus === "all"
            ? applications
            : applications.filter((a) => a.status === activeStatus);

    const countByStatus = (status: string) =>
        applications.filter((a) => a.status === status).length;

    // Summary stats
    const stats = {
        total: applications.length,
        applied: countByStatus("applied"),
        accepted: countByStatus("accepted"),
        interview: countByStatus("interview"),
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900">My Application Tracker</h1>
                <p className="text-gray-500 mt-1">
                    Track your opportunity applications from saved to accepted.
                </p>
            </div>

            {/* Summary stats */}
            {applications.length > 0 && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {[
                        { label: "Total Tracked", value: stats.total, color: "text-gray-900" },
                        { label: "Applied", value: stats.applied, color: "text-yellow-700" },
                        { label: "Interviews", value: stats.interview, color: "text-purple-700" },
                        { label: "Accepted", value: stats.accepted, color: "text-green-700" },
                    ].map((s) => (
                        <div key={s.label} className="bg-white rounded-xl border border-gray-200 p-4 text-center">
                            <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
                            <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
                        </div>
                    ))}
                </div>
            )}

            {/* Status tabs */}
            <div className="flex flex-wrap gap-2">
                <button
                    onClick={() => setActiveStatus("all")}
                    className={clsx(
                        "px-3 py-1.5 text-sm rounded-lg border transition-colors",
                        activeStatus === "all"
                            ? "bg-brand-600 text-white border-brand-600"
                            : "bg-white text-gray-600 border-gray-200 hover:bg-gray-50"
                    )}
                >
                    All ({applications.length})
                </button>
                {STATUSES.map((s) => (
                    <button
                        key={s.value}
                        onClick={() => setActiveStatus(s.value)}
                        className={clsx(
                            "px-3 py-1.5 text-sm rounded-lg border transition-colors",
                            activeStatus === s.value
                                ? "bg-brand-600 text-white border-brand-600"
                                : "bg-white text-gray-600 border-gray-200 hover:bg-gray-50"
                        )}
                    >
                        {s.label} ({countByStatus(s.value)})
                    </button>
                ))}
            </div>

            {/* Content */}
            {loading ? (
                <div className="flex items-center justify-center py-20">
                    <Loader2 size={32} className="animate-spin text-brand-500" />
                </div>
            ) : error ? (
                <div className="flex items-center gap-3 p-4 bg-red-50 text-red-700 rounded-xl">
                    <AlertCircle size={20} />
                    <p>{error}</p>
                </div>
            ) : filtered.length === 0 ? (
                <div className="text-center py-20 text-gray-400 space-y-3">
                    <BookOpen size={40} className="mx-auto opacity-40" />
                    <p className="text-lg font-medium">No applications yet</p>
                    <p className="text-sm">
                        Browse opportunities and click &quot;Save to Tracker&quot; to start tracking.
                    </p>
                    <Link
                        href="/"
                        className="inline-block mt-2 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 text-sm"
                    >
                        Discover Opportunities
                    </Link>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                    {filtered.map((app) => (
                        <ApplicationRow
                            key={app.id}
                            app={app}
                            onUpdate={handleUpdate}
                            onDelete={handleDelete}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}
