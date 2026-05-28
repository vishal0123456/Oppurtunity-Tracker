"""
Seed script — populates the database with realistic sample opportunities.

Usage:
    cd backend
    python scripts/seed_data.py
"""
import asyncio
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import AsyncSessionLocal, init_db
from app.models.opportunity import Opportunity

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SEED_OPPORTUNITIES = [
    # ── Scholarships ──────────────────────────────────────────────────────────
    {
        "title": "Chevening Scholarships 2026/2027",
        "organization": "UK Foreign, Commonwealth & Development Office",
        "description": "Chevening is the UK government's international awards programme, offering fully funded scholarships to study any eligible master's degree at any UK university.",
        "category": "scholarship",
        "tags": ["Scholarship", "Leadership", "Education"],
        "country": ["Global", "UK"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "eligibility": "Citizens of Chevening-eligible countries with at least 2 years of work experience.",
        "funding_amount": "Fully funded",
        "application_fee": "Free",
        "link": "https://www.chevening.org/scholarships/",
        "source_name": "Chevening",
        "deadline": "2026-11-05",
    },
    {
        "title": "Fulbright Foreign Student Program 2026",
        "organization": "U.S. Department of State",
        "description": "The Fulbright Program offers grants for graduate study, advanced research, university teaching, and teaching in elementary and secondary schools.",
        "category": "scholarship",
        "tags": ["Scholarship", "Research", "Education", "Student"],
        "country": ["USA", "Global"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "eligibility": "Citizens of participating countries. Must hold a bachelor's degree or equivalent.",
        "funding_amount": "Fully funded",
        "application_fee": "Free",
        "link": "https://foreign.fulbrightonline.org/",
        "source_name": "Fulbright",
        "deadline": "2026-10-15",
    },
    {
        "title": "DAAD Scholarships for Development-Related Postgraduate Courses",
        "organization": "German Academic Exchange Service (DAAD)",
        "description": "Scholarships for postgraduate courses in Germany for graduates from developing countries. Covers tuition, living expenses, travel, and health insurance.",
        "category": "scholarship",
        "tags": ["Scholarship", "Research", "Education", "Student"],
        "country": ["Germany", "Europe"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "age_limit": "Under 36",
        "eligibility": "Graduates from developing countries with at least 2 years of professional experience.",
        "funding_amount": "Fully funded",
        "application_fee": "Free",
        "link": "https://www.daad.de/en/study-and-research-in-germany/scholarships/",
        "source_name": "DAAD",
        "deadline": "2026-09-30",
    },
    # ── Fellowships ─
    {
        "title": "Obama Foundation Scholars Program 2026",
        "organization": "Obama Foundation",
        "description": "A one-year program at Columbia University for emerging leaders from around the world who are working to create change in their communities.",
        "category": "fellowship",
        "tags": ["Fellowship", "Leadership", "Social Impact", "Student"],
        "country": ["USA", "Global"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": False,
        "eligibility": "Emerging leaders aged 25-40 with demonstrated commitment to community impact.",
        "funding_amount": "Fully funded",
        "application_fee": "Free",
        "link": "https://www.obama.org/scholars/",
        "source_name": "Obama Foundation",
        "deadline": "2026-12-01",
    },
    {
        "title": "Acumen Fellowship India 2026",
        "organization": "Acumen",
        "description": "A year-long leadership development program for India's most promising social change leaders. Fellows work on solving problems of poverty.",
        "category": "fellowship",
        "tags": ["Fellowship", "Social Impact", "Leadership", "Startup"],
        "country": ["India"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": False,
        "age_limit": "Under 40",
        "eligibility": "Indian citizens with 5+ years of experience in social sector or business.",
        "funding_amount": "Stipend provided",
        "application_fee": "Free",
        "link": "https://acumen.org/fellowships/",
        "source_name": "Acumen",
        "deadline": "2026-08-31",
    },
    {
        "title": "Atlantic Fellows for Social and Economic Equity",
        "organization": "London School of Economics",
        "description": "A global fellowship program that brings together leaders committed to advancing social and economic equity. Based at LSE with global network.",
        "category": "fellowship",
        "tags": ["Fellowship", "Social Impact", "Leadership", "Research"],
        "country": ["UK", "Global"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": False,
        "eligibility": "Mid-career professionals with 7+ years of experience working on equity issues.",
        "funding_amount": "Fully funded",
        "application_fee": "Free",
        "link": "https://www.atlanticfellows.org/",
        "source_name": "Atlantic Fellows",
        "deadline": "2026-11-15",
    },
    # ── Accelerators ──
    {
        "title": "Y Combinator W2027 Batch",
        "organization": "Y Combinator",
        "description": "Y Combinator provides seed funding for startups. Twice a year we invest a small amount of money in a large number of startups.",
        "category": "accelerator",
        "tags": ["Startup", "Founder", "Tech", "AI"],
        "country": ["USA", "Global"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "eligibility": "Early-stage startups with a working prototype or MVP. Open to all nationalities.",
        "funding_amount": "$500,000",
        "application_fee": "Free",
        "link": "https://www.ycombinator.com/apply/",
        "source_name": "Y Combinator",
        "deadline": "2026-10-14",
    },
    {
        "title": "Google for Startups Accelerator: India 2026",
        "organization": "Google",
        "description": "A 3-month equity-free accelerator program for Seed to Series A technology startups in India. Provides mentorship, Google credits, and workspace.",
        "category": "accelerator",
        "tags": ["Startup", "AI", "Tech", "Founder"],
        "country": ["India"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": False,
        "eligibility": "Indian tech startups at Seed to Series A stage with a working product.",
        "funding_amount": "Equity-free + $200,000 in Google Cloud credits",
        "application_fee": "Free",
        "link": "https://startup.google.com/programs/accelerator/india/",
        "source_name": "Google for Startups",
        "deadline": "2026-09-15",
    },
    {
        "title": "Antler Residency Program — Singapore",
        "organization": "Antler",
        "description": "Antler is a global early-stage VC that enables exceptional people to build great companies. The residency brings together talented individuals to form startups.",
        "category": "accelerator",
        "tags": ["Startup", "Founder", "Tech", "AI"],
        "country": ["Singapore"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": False,
        "eligibility": "Exceptional individuals with domain expertise, technical skills, or entrepreneurial experience.",
        "funding_amount": "$100,000 for 10% equity",
        "application_fee": "Free",
        "link": "https://www.antler.co/residency",
        "source_name": "Antler",
        "deadline": "2026-12-31",
    },
    # ── Grants ──
    {
        "title": "Bill & Melinda Gates Foundation Grand Challenges",
        "organization": "Bill & Melinda Gates Foundation",
        "description": "Grand Challenges funds bold ideas to solve persistent global health and development problems. Open to innovators worldwide.",
        "category": "grant",
        "tags": ["Grant", "Health", "Research", "Social Impact"],
        "country": ["Global"],
        "is_remote": True,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "eligibility": "Researchers, entrepreneurs, and innovators from any country working on global health challenges.",
        "funding_amount": "Up to $100,000",
        "application_fee": "Free",
        "link": "https://gcgh.grandchallenges.org/",
        "source_name": "Gates Foundation",
        "deadline": "2026-10-31",
    },
    {
        "title": "Cartier Women's Initiative 2027",
        "organization": "Cartier",
        "description": "An international business plan competition and grant program that aims to identify, support and encourage women entrepreneurs.",
        "category": "grant",
        "tags": ["Women", "Startup", "Founder", "Grant", "Social Impact"],
        "country": ["Global"],
        "is_remote": True,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": False,
        "eligibility": "Women entrepreneurs running an early-stage business (1-3 years old) with positive social or environmental impact.",
        "funding_amount": "$100,000 (1st prize), $30,000 (2nd prize)",
        "application_fee": "Free",
        "link": "https://www.cartierwomensinitiative.com/",
        "source_name": "Cartier",
        "deadline": "2026-09-30",
    },
    {
        "title": "Startup India Seed Fund Scheme",
        "organization": "Department for Promotion of Industry and Internal Trade (DPIIT)",
        "description": "Provides financial assistance to startups for proof of concept, prototype development, product trials, market entry and commercialization.",
        "category": "government_scheme",
        "tags": ["Startup", "Founder", "Grant", "Government"],
        "country": ["India"],
        "is_remote": True,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": False,
        "eligibility": "DPIIT-recognized startups incorporated not more than 2 years ago.",
        "funding_amount": "Up to ₹50 lakhs",
        "application_fee": "Free",
        "link": "https://seedfund.startupindia.gov.in/",
        "source_name": "Startup India",
        "deadline": "2026-12-31",
    },
    # ── Competitions ────
    {
        "title": "MIT Solve Global Challenges 2026",
        "organization": "MIT",
        "description": "MIT Solve is a marketplace for social impact innovation. Solve challenges invite tech-based social entrepreneurs to submit solutions to global problems.",
        "category": "competition",
        "tags": ["Hackathon", "Social Impact", "Tech", "AI", "Startup"],
        "country": ["USA", "Global"],
        "is_remote": True,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "eligibility": "Tech-based social entrepreneurs and innovators from any country.",
        "funding_amount": "Up to $10,000 + in-kind support",
        "application_fee": "Free",
        "link": "https://solve.mit.edu/",
        "source_name": "MIT Solve",
        "deadline": "2026-08-15",
    },
    {
        "title": "HackerEarth AI Hackathon 2026",
        "organization": "HackerEarth",
        "description": "Build AI-powered solutions to real-world problems. Open to developers, data scientists, and AI enthusiasts globally.",
        "category": "competition",
        "tags": ["Hackathon", "AI", "Tech", "Engineering", "Student"],
        "country": ["Global"],
        "is_remote": True,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "eligibility": "Open to all developers and students globally.",
        "funding_amount": "$5,000 total prize pool",
        "application_fee": "Free",
        "link": "https://www.hackerearth.com/challenges/",
        "source_name": "HackerEarth",
        "deadline": "2026-09-01",
    },
    # ── Exchange Programs ───
    {
        "title": "AIESEC Global Volunteer Program",
        "organization": "AIESEC",
        "description": "Cross-cultural volunteer experiences in 120+ countries. Work on UN Sustainable Development Goals projects while developing leadership skills.",
        "category": "exchange_program",
        "tags": ["Travel", "Social Impact", "Leadership", "Student"],
        "country": ["Global"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "age_limit": "18-30",
        "eligibility": "Students and recent graduates aged 18-30.",
        "funding_amount": "Partially funded",
        "application_fee": "Program fee applies",
        "link": "https://aiesec.org/global-volunteer",
        "source_name": "AIESEC",
        "deadline": "2026-12-31",
    },
    {
        "title": "DAAD WISE Scholarship — Research Internship in Germany",
        "organization": "DAAD",
        "description": "Working Internships in Science and Engineering (WISE) for Indian students to undertake research internships at top German universities.",
        "category": "exchange_program",
        "tags": ["Research", "Engineering", "Student", "Travel", "Scholarship"],
        "country": ["Germany", "Europe"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "eligibility": "Indian students enrolled in B.Tech/B.E./M.Tech/M.E./M.Sc. programs.",
        "funding_amount": "€934/month + travel allowance",
        "application_fee": "Free",
        "link": "https://www.daad.in/en/find-funding/scholarships-for-indians/wise-scholarship/",
        "source_name": "DAAD India",
        "deadline": "2026-11-30",
    },
    # ── Travel Programs ─
    {
        "title": "Atlas Corps Fellowship",
        "organization": "Atlas Corps",
        "description": "Atlas Corps builds a network of global leaders by placing top nonprofit professionals from around the world in fellowships at leading organizations in the USA.",
        "category": "travel_program",
        "tags": ["Fellowship", "Leadership", "Social Impact", "Travel"],
        "country": ["USA"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": False,
        "age_limit": "35 or under",
        "eligibility": "Nonprofit professionals with 2+ years of experience, aged 35 or under.",
        "funding_amount": "Stipend + housing + health insurance",
        "application_fee": "Free",
        "link": "https://atlascorps.org/apply/",
        "source_name": "Atlas Corps",
        "deadline": "2026-10-01",
    },
    # ── VC Programs ────
    {
        "title": "Sequoia Surge — Southeast Asia & India",
        "organization": "Sequoia Capital",
        "description": "Surge is a rapid scale-up program for startups in Southeast Asia and India. 16-week program with $1-2M investment.",
        "category": "vc_program",
        "tags": ["Startup", "Founder", "Tech", "AI", "Finance"],
        "country": ["India", "Singapore"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": False,
        "eligibility": "Early-stage startups in Southeast Asia and India with a working product.",
        "funding_amount": "$1M - $2M",
        "application_fee": "Free",
        "link": "https://www.surgeahead.com/",
        "source_name": "Sequoia Surge",
        "deadline": "2026-11-01",
    },
    # ── Conferences ────
    {
        "title": "Grace Hopper Celebration 2026 — Scholarship",
        "organization": "AnitaB.org",
        "description": "The world's largest gathering of women technologists. Scholarships available for students and professionals to attend.",
        "category": "conference",
        "tags": ["Women", "Tech", "Engineering", "Student", "Leadership"],
        "country": ["USA"],
        "is_remote": True,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "eligibility": "Women and non-binary technologists. Scholarship available for students.",
        "funding_amount": "Full conference scholarship",
        "application_fee": "Free",
        "link": "https://ghc.anitab.org/",
        "source_name": "AnitaB.org",
        "deadline": "2026-07-31",
    },
    # ── Giveaways ─────
    {
        "title": "AWS Activate — Startup Credits Program",
        "organization": "Amazon Web Services",
        "description": "AWS Activate provides startups with free tools, resources, and more to quickly get started on AWS. Up to $100,000 in AWS credits.",
        "category": "giveaway",
        "tags": ["Startup", "Tech", "Founder", "AI"],
        "country": ["Global"],
        "is_remote": True,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": False,
        "eligibility": "Early-stage startups associated with an AWS Activate Provider.",
        "funding_amount": "Up to $100,000 in AWS credits",
        "application_fee": "Free",
        "link": "https://aws.amazon.com/activate/",
        "source_name": "AWS",
        "deadline": "2026-12-31",
    },
    {
        "title": "Google for Startups Cloud Program",
        "organization": "Google",
        "description": "Provides early-stage startups with Google Cloud credits, technical support, and access to Google's network of partners and investors.",
        "category": "giveaway",
        "tags": ["Startup", "Tech", "Founder", "AI"],
        "country": ["Global"],
        "is_remote": True,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": False,
        "eligibility": "Early-stage startups (pre-Series A) working on technology products.",
        "funding_amount": "Up to $200,000 in Google Cloud credits",
        "application_fee": "Free",
        "link": "https://cloud.google.com/startup",
        "source_name": "Google Cloud",
        "deadline": "2026-12-31",
    },
    # ── Research ────
    {
        "title": "DST-INSPIRE Fellowship for PhD",
        "organization": "Department of Science & Technology, India",
        "description": "INSPIRE Fellowship supports PhD students in natural and basic sciences. Provides monthly fellowship and contingency grant.",
        "category": "fellowship",
        "tags": ["Research", "Student", "Government", "Scholarship"],
        "country": ["India"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "age_limit": "Under 32",
        "eligibility": "Indian students pursuing PhD in natural and basic sciences.",
        "funding_amount": "₹31,000/month + ₹20,000 contingency/year",
        "application_fee": "Free",
        "link": "https://online-inspire.gov.in/",
        "source_name": "DST India",
        "deadline": "2026-10-31",
    },
    {
        "title": "Microsoft Research PhD Fellowship",
        "organization": "Microsoft Research",
        "description": "Supports exceptional PhD students pursuing research in areas relevant to Microsoft. Provides funding, mentorship, and internship opportunities.",
        "category": "fellowship",
        "tags": ["Research", "AI", "Tech", "Engineering", "Student"],
        "country": ["USA", "India", "Europe"],
        "is_remote": False,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "eligibility": "PhD students in computer science, electrical engineering, or related fields.",
        "funding_amount": "Full tuition + $42,000/year stipend",
        "application_fee": "Free",
        "link": "https://www.microsoft.com/en-us/research/academic-program/phd-fellowship/",
        "source_name": "Microsoft Research",
        "deadline": "2026-09-15",
    },
    # ── Climate ───
    {
        "title": "Climate Launchpad — Green Business Ideas Competition",
        "organization": "EIT Climate-KIC",
        "description": "The world's biggest green business ideas competition. Supports entrepreneurs with climate-positive business ideas.",
        "category": "competition",
        "tags": ["Climate", "Startup", "Founder", "Social Impact", "Hackathon"],
        "country": ["Europe", "Global"],
        "is_remote": True,
        "women_friendly": True,
        "india_eligible": True,
        "student_eligible": True,
        "eligibility": "Entrepreneurs and innovators with a climate-positive business idea.",
        "funding_amount": "€10,000 (global winner)",
        "application_fee": "Free",
        "link": "https://climatelaunchpad.org/",
        "source_name": "EIT Climate-KIC",
        "deadline": "2026-08-01",
    },
]


async def reset_expired_and_update_deadlines():
    """
    Reset all existing opportunities:
    - Set is_expired = False
    - Update deadlines to 2026/2027
    """
    from sqlalchemy import update as sql_update
    from datetime import date

    async with AsyncSessionLocal() as db:
        # Reset all to not expired
        await db.execute(
            sql_update(Opportunity).values(is_expired=False)
        )
        await db.commit()
        logger.info("Reset all opportunities to is_expired=False")

        # Update each existing opportunity's deadline by adding 1 year
        from sqlalchemy import select
        result = await db.execute(select(Opportunity))
        opps = result.scalars().all()

        updated = 0
        for opp in opps:
            if opp.deadline:
                try:
                    new_deadline = opp.deadline.replace(year=opp.deadline.year + 1)
                    opp.deadline = new_deadline
                    updated += 1
                except ValueError:
                    # Feb 29 edge case
                    opp.deadline = opp.deadline.replace(year=opp.deadline.year + 1, day=28)
                    updated += 1

        await db.commit()
        logger.info(f"Updated {updated} opportunity deadlines to next year")


async def seed():
    """Insert new seed opportunities, skipping any that already exist by URL."""
    await init_db()

    #  reseting all expired records and updating deadlines
    await reset_expired_and_update_deadlines()

    async with AsyncSessionLocal() as db:
        inserted = 0
        skipped = 0

        for data in SEED_OPPORTUNITIES:
            from sqlalchemy import select
            result = await db.execute(
                select(Opportunity).where(Opportunity.link == data["link"])
            )
            if result.scalar_one_or_none():
                skipped += 1
                continue

            from datetime import date as date_type
            deadline = None
            if data.get("deadline"):
                deadline = date_type.fromisoformat(data["deadline"])

            opp = Opportunity(
                title=data["title"],
                organization=data.get("organization"),
                description=data.get("description"),
                category=data["category"],
                tags=data.get("tags", []),
                country=data.get("country", []),
                is_remote=data.get("is_remote", False),
                women_friendly=data.get("women_friendly", False),
                india_eligible=data.get("india_eligible", False),
                student_eligible=data.get("student_eligible", False),
                age_limit=data.get("age_limit"),
                eligibility=data.get("eligibility"),
                funding_amount=data.get("funding_amount"),
                application_fee=data.get("application_fee"),
                link=data["link"],
                source_name=data.get("source_name"),
                source_url=data["link"],
                deadline=deadline,
                is_expired=False,
            )
            db.add(opp)
            inserted += 1

        await db.commit()
        logger.info(f"Seed complete: {inserted} inserted, {skipped} already existed.")


if __name__ == "__main__":
    asyncio.run(seed())
