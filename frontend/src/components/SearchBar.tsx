"use client";

import { useState, useCallback } from "react";
import { Search, X, Sparkles } from "lucide-react";

interface Props {
    onSearch: (query: string) => void;
    placeholder?: string;
    isAI?: boolean;
}

export default function SearchBar({
    onSearch,
    placeholder = 'Search opportunities... e.g. "Women founder grants in Europe"',
    isAI = true,
}: Props) {
    const [value, setValue] = useState("");

    const handleSubmit = useCallback(
        (e: React.FormEvent) => {
            e.preventDefault();
            onSearch(value.trim());
        },
        [value, onSearch]
    );

    const handleClear = () => {
        setValue("");
        onSearch("");
    };

    return (
        <form onSubmit={handleSubmit} className="relative w-full">
            <div className="relative flex items-center">
                {isAI ? (
                    <Sparkles
                        size={18}
                        className="absolute left-4 text-brand-500 pointer-events-none"
                    />
                ) : (
                    <Search
                        size={18}
                        className="absolute left-4 text-gray-400 pointer-events-none"
                    />
                )}

                <input
                    type="text"
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    placeholder={placeholder}
                    className="w-full pl-11 pr-24 py-3 rounded-xl border border-gray-200 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-gray-900 placeholder-gray-400"
                    aria-label="Search opportunities"
                />

                {value && (
                    <button
                        type="button"
                        onClick={handleClear}
                        className="absolute right-20 text-gray-400 hover:text-gray-600 p-1"
                        aria-label="Clear search"
                    >
                        <X size={16} />
                    </button>
                )}

                <button
                    type="submit"
                    className="absolute right-2 px-4 py-1.5 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors"
                >
                    Search
                </button>
            </div>

            {isAI && (
                <p className="mt-1.5 text-xs text-gray-400 pl-1">
                    ✨ AI-powered — try natural language queries
                </p>
            )}
        </form>
    );
}
