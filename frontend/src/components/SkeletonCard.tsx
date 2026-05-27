/**
 * Skeleton loading card — shown while opportunities are being fetched.
 * Matches the layout of OpportunityCard for a smooth loading experience.
 */
export default function SkeletonCard() {
    return (
        <div className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col gap-3 animate-pulse">
            {/* Header */}
            <div className="flex items-start justify-between gap-2">
                <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                    <div className="h-3 bg-gray-100 rounded w-1/2" />
                </div>
                <div className="w-7 h-7 bg-gray-100 rounded-lg flex-shrink-0" />
            </div>

            {/* Description */}
            <div className="space-y-1.5">
                <div className="h-3 bg-gray-100 rounded w-full" />
                <div className="h-3 bg-gray-100 rounded w-5/6" />
            </div>

            {/* Meta row */}
            <div className="flex flex-wrap gap-2">
                <div className="h-5 bg-gray-200 rounded-full w-20" />
                <div className="h-5 bg-gray-100 rounded-full w-16" />
                <div className="h-5 bg-gray-100 rounded-full w-14" />
            </div>

            {/* Badges */}
            <div className="flex gap-1.5">
                <div className="h-5 bg-pink-50 rounded-full w-16" />
                <div className="h-5 bg-blue-50 rounded-full w-16" />
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between pt-1 border-t border-gray-100">
                <div className="h-3 bg-gray-100 rounded w-16" />
                <div className="h-3 bg-gray-100 rounded w-12" />
            </div>
        </div>
    );
}

export function SkeletonGrid({ count = 6 }: { count?: number }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {Array.from({ length: count }).map((_, i) => (
                <SkeletonCard key={i} />
            ))}
        </div>
    );
}
