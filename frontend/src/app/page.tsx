"use client";

import { useState, useEffect, useCallback } from "react";
import SearchBar from "@/components/SearchBar";
import FilterPanel from "@/components/FilterPanel";
import MobileFilterDrawer from "@/components/MobileFilterDrawer";
import OpportunityCard from "@/components/OpportunityCard";
import { SkeletonGrid } from "@/components/SkeletonCard";
import { getOpportunities, searchOpportunities, createApplication, triggerPipeline, getStats } from "@/lib/api";
import type { Opportunity, OpportunityFilters } from "@/types/opportunity";
import { AlertCircle, ChevronLeft, ChevronRight, RefreshCw, Zap, Globe, Clock } from "lucide-react";

interface Stats {
    total: number;
    active: number;
    expiring_soon: number;
    by_category: { category: string; count: number }[];
}

function StatsBar({ stats }: { stats: Stats }) {
    return (
        <div className="grid grid-cols-3 gap-3 mb-2">
            {[
                { icon: <Globe size={16} />, label: "Total Opportunities", value: stats.total.toLocaleString(), color: "text-brand-600" },
                { icon: <Zap size={16} />, label: "Active Now", value: stats.active.toLocaleString(), color: "text-green-600" },
                { icon: <Clock size={16} />, label: "Closing This Week", value: stats.expiring_soon.toLocaleString(), color: "text-amber-600" },
            ].map((s) => (
                <div key={s.label} className="bg-white rounded-xl border border-gray-200 px-4 py-3 flex items-center gap-3">
                    <span className={s.color}>{s.icon}</span>
                    <div>
                        <p className={`text-xl font-bold ${s.color}`}>{s.value}</p>
                        <p className="text-xs text-gray-500">{s.label}</p>
                    </div>
                </div>
            ))}
        </div>
    );
}

export default function HomePage() {
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [filters, setFilters] = useState<OpportunityFilters>({ is_expired: false, page: 1, page_size: 20 });
    const [savedIds, setSavedIds] = useState<Set<string>>(new Set());
    const [pipelineRunning, setPipelineRunning] = useState(false);
    const [pipelineMsg, setPipelineMsg] = useState<string | null>(null);
    const [stats, setStats] = useState<Stats | null>(null);

    // Fetch stats once on mount
    useEffect(() => {
        getStats().then(setStats).catch(() => null);
    }, []);

    const fetchOpportunities = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            let data;
            if (searchQuery) {
                data = await searchOpportunities(searchQuery, filters.page, filters.page_size);
            } else {
                data = await getOpportunities(filters);
            }
            setOpportunities(data.results);
            setTotal(data.total);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load opportunities");
        } finally {
            setLoading(false);
        }
    }, [filters, searchQuery]);

    useEffect(() => {
        fetchOpportunities();
    }, [fetchOpportunities]);

    const handleSearch = (query: string) => {
        setSearchQuery(query);
        setFilters((f) => ({ ...f, page: 1 }));
    };

    const handleSave = async (id: string) => {
        try {
            await createApplication({ opportunity_id: id, status: "saved" });
            setSavedIds((prev) => new Set([...prev, id]));
        } catch {
            setSavedIds((prev) => {
                const next = new Set(prev);
                next.delete(id);
                return next;
            });
        }
    };

    const handleRunPipeline = async () => {
        setPipelineRunning(true);
        setPipelineMsg(null);
        try {
            const res = await triggerPipeline();
            setPipelineMsg(res.message);
            // Refresh stats after pipeline
            setTimeout(() => getStats().then(setStats).catch(() => null), 3000);
        } catch (e) {
            setPipelineMsg(e instanceof Error ? e.message : "Failed to start pipeline");
        } finally {
            setPipelineRunning(false);
        }
    };

    const totalPages = Math.ceil(total / (filters.page_size || 20));
    const currentPage = filters.page || 1;

    return (
        <div className="space-y-6">
            {/* Hero */}
            <div className="text-center space-y-2 py-4">
                <h1 className="text-3xl font-bold text-gray-900">
                    Discover Global Opportunities
                </h1>
                <p className="text-gray-500 max-w-xl mx-auto">
                    Scholarships, fellowships, grants, accelerators, and more — automatically
                    discovered and updated daily.
                </p>
            </div>

            {/* Stats bar */}
            {stats && <StatsBar stats={stats} />}

            {/* Search */}
            <div className="max-w-2xl mx-auto">
                <SearchBar onSearch={handleSearch} />
            </div>

            {/* Results bar */}
            <div className="flex items-center justify-between text-sm text-gray-500 flex-wrap gap-2">
                <div className="flex items-center gap-3">
                    <span>
                        {loading ? "Searching..." : `${total.toLocaleString()} opportunities found`}
                        {searchQuery && ` for "${searchQuery}"`}
                    </span>
                    {searchQuery && (
                        <button onClick={() => handleSearch("")} className="text-brand-600 hover:underline">
                            Clear search
                        </button>
                    )}
                </div>

                {/* Pipeline trigger */}
                <div className="flex items-center gap-2">
                    {pipelineMsg && (
                        <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-lg">
                            {pipelineMsg}
                        </span>
                    )}
                    <button
                        onClick={handleRunPipeline}
                        disabled={pipelineRunning}
                        title="Manually trigger the discovery pipeline"
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-colors"
                    >
                        <RefreshCw size={13} className={pipelineRunning ? "animate-spin" : ""} />
                        {pipelineRunning ? "Running..." : "Run Pipeline"}
                    </button>
                </div>
            </div>

            {/* Main layout */}
            <div className="flex gap-6">
                {/* Mobile filter button */}
                <div className="lg:hidden">
                    <MobileFilterDrawer filters={filters} onChange={setFilters} />
                </div>

                {/* Filters sidebar — desktop only */}
                <div className="hidden lg:block w-64 flex-shrink-0">
                    <FilterPanel filters={filters} onChange={setFilters} />
                </div>

                {/* Results */}
                <div className="flex-1 min-w-0">
                    {loading ? (
                        <SkeletonGrid count={6} />
                    ) : error ? (
                        <div className="flex items-center gap-3 p-4 bg-red-50 text-red-700 rounded-xl">
                            <AlertCircle size={20} />
                            <div>
                                <p className="font-medium">Failed to load opportunities</p>
                                <p className="text-sm">{error}</p>
                                <p className="text-sm mt-1">
                                    Make sure the backend is running at{" "}
                                    {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
                                </p>
                            </div>
                        </div>
                    ) : opportunities.length === 0 ? (
                        <div className="text-center py-20 text-gray-400">
                            <p className="text-lg font-medium">No opportunities found</p>
                            <p className="text-sm mt-1">Try adjusting your filters or search query</p>
                        </div>
                    ) : (
                        <>
                            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                                {opportunities.map((opp) => (
                                    <OpportunityCard
                                        key={opp.id}
                                        opportunity={opp}
                                        onSave={handleSave}
                                        isSaved={savedIds.has(opp.id)}
                                    />
                                ))}
                            </div>

                            {/* Pagination */}
                            {totalPages > 1 && (
                                <div className="flex items-center justify-center gap-2 mt-8">
                                    <button
                                        onClick={() => setFilters((f) => ({ ...f, page: Math.max(1, currentPage - 1) }))}
                                        disabled={currentPage === 1}
                                        className="p-2 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50"
                                        aria-label="Previous page"
                                    >
                                        <ChevronLeft size={18} />
                                    </button>
                                    <span className="text-sm text-gray-600">
                                        Page {currentPage} of {totalPages}
                                    </span>
                                    <button
                                        onClick={() => setFilters((f) => ({ ...f, page: Math.min(totalPages, currentPage + 1) }))}
                                        disabled={currentPage === totalPages}
                                        className="p-2 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50"
                                        aria-label="Next page"
                                    >
                                        <ChevronRight size={18} />
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
