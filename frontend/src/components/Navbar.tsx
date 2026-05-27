import Link from "next/link";
import { Globe, BookOpen, LayoutDashboard } from "lucide-react";

export default function Navbar() {
    return (
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 font-bold text-gray-900 text-lg">
                        <Globe size={22} className="text-brand-600" />
                        <span>OpportunityTracker</span>
                    </Link>

                    {/* Nav links */}
                    <div className="flex items-center gap-1">
                        <Link
                            href="/"
                            className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                            <LayoutDashboard size={16} />
                            Discover
                        </Link>
                        <Link
                            href="/tracker"
                            className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                            <BookOpen size={16} />
                            My Tracker
                        </Link>
                    </div>
                </div>
            </div>
        </nav>
    );
}
