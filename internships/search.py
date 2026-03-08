"""
Advanced search engine for the Remotely Internship Platform.
Handles smart keyword parsing, relevance scoring, skill matching,
auto-suggestions, and trending searches.
"""
from django.db.models import Q, F
from django.utils import timezone
from datetime import timedelta
from collections import Counter


# ==================== SMART KEYWORD PARSER ====================

# Common skills for detection
COMMON_SKILLS = [
    'python', 'django', 'javascript', 'react', 'angular', 'vue', 'nodejs', 'node.js',
    'typescript', 'html', 'css', 'tailwind', 'bootstrap', 'sass', 'less',
    'java', 'spring', 'kotlin', 'swift', 'flutter', 'dart', 'react native',
    'php', 'laravel', 'wordpress', 'ruby', 'rails', 'go', 'golang', 'rust',
    'c++', 'c#', '.net', 'asp.net', 'unity',
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd',
    'git', 'linux', 'nginx', 'apache',
    'machine learning', 'deep learning', 'ai', 'data science', 'pandas', 'numpy',
    'tensorflow', 'pytorch', 'nlp', 'computer vision',
    'figma', 'photoshop', 'illustrator', 'ui/ux', 'ux design', 'ui design',
    'devops', 'sre', 'cybersecurity', 'blockchain', 'solidity', 'web3',
    'graphql', 'rest api', 'api', 'microservices',
    'agile', 'scrum', 'jira', 'project management',
    'excel', 'power bi', 'tableau', 'sap', 'salesforce',
    'android', 'ios', 'mobile', 'responsive design',
    'seo', 'digital marketing', 'content writing', 'copywriting',
    'accounting', 'finance', 'hr', 'human resources', 'recruitment',
]

# Work mode keywords
WORK_MODE_KEYWORDS = {
    'remote': ['remote', 'work from home', 'wfh', 'telecommute', 'virtual'],
    'hybrid': ['hybrid', 'flexible', 'partially remote'],
    'onsite': ['onsite', 'on-site', 'in-office', 'office-based', 'in office'],
}

# Job type keywords
JOB_TYPE_KEYWORDS = {
    'full_time': ['full time', 'full-time', 'fulltime', 'ft'],
    'part_time': ['part time', 'part-time', 'parttime', 'pt'],
    'contract': ['contract', 'contractual', 'temporary', 'temp'],
    'freelance': ['freelance', 'freelancer', 'gig', 'project-based'],
    'internship': ['internship', 'intern', 'trainee', 'apprentice'],
}

# Experience keywords
EXPERIENCE_KEYWORDS = {
    'fresher': ['fresher', 'fresh graduate', 'entry level', 'entry-level', 'no experience', 'graduate', 'beginner'],
    'junior': ['junior', '1-3 years', '1 year', '2 years', '3 years'],
    'mid': ['mid level', 'mid-level', 'intermediate', '3-5 years', '4 years', '5 years'],
    'senior': ['senior', 'experienced', '5-8 years', '6 years', '7 years', '8 years'],
    'lead': ['lead', 'principal', 'staff', 'architect', '8+ years', '10 years', '10+ years'],
}


def parse_smart_query(query_text):
    """
    Parse a natural language search query and extract structured filters.
    Returns dict with: keywords, detected_skills, detected_work_mode,
    detected_job_type, detected_experience, detected_location
    """
    if not query_text:
        return {'keywords': '', 'detected_skills': [], 'detected_work_mode': None,
                'detected_job_type': None, 'detected_experience': None, 'detected_location': None}

    import re
    query_lower = query_text.lower().strip()
    remaining = query_lower

    # Detect skills (use word boundaries for short skills to avoid false positives)
    detected_skills = []
    for skill in sorted(COMMON_SKILLS, key=len, reverse=True):
        if len(skill) <= 3:
            # Short skills need boundary check (use lookarounds for non-word char skills like c++, c#)
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill) + r'(?![a-zA-Z0-9])'
            if re.search(pattern, remaining):
                detected_skills.append(skill)
                remaining = re.sub(pattern, ' ', remaining, count=1)
        else:
            if skill in remaining:
                detected_skills.append(skill)
                remaining = remaining.replace(skill, ' ', 1)

    # Detect work mode
    detected_work_mode = None
    for mode, keywords in WORK_MODE_KEYWORDS.items():
        for kw in keywords:
            if kw in query_lower:
                detected_work_mode = mode
                remaining = remaining.replace(kw, ' ', 1)
                break
        if detected_work_mode:
            break

    # Detect job type
    detected_job_type = None
    for jtype, keywords in JOB_TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in query_lower:
                detected_job_type = jtype
                remaining = remaining.replace(kw, ' ', 1)
                break
        if detected_job_type:
            break

    # Detect experience level
    detected_experience = None
    for exp, keywords in EXPERIENCE_KEYWORDS.items():
        for kw in keywords:
            if kw in query_lower:
                detected_experience = exp
                remaining = remaining.replace(kw, ' ', 1)
                break
        if detected_experience:
            break

    # Clean remaining as general keywords
    keywords = ' '.join(remaining.split()).strip()

    return {
        'keywords': keywords,
        'detected_skills': detected_skills,
        'detected_work_mode': detected_work_mode,
        'detected_job_type': detected_job_type,
        'detected_experience': detected_experience,
        'detected_location': None,  # Location detection from keywords is ambiguous, use explicit filter
    }


# ==================== SKILL MATCHING ====================

def calculate_skill_match(user_skills_str, job_skills_str):
    """
    Calculate skill match percentage between user and job.
    Returns dict with match_percentage, matching_skills, missing_skills.
    """
    if not user_skills_str or not job_skills_str:
        return {'match_percentage': 0, 'matching_skills': [], 'missing_skills': []}

    user_skills = {s.strip().lower() for s in user_skills_str.split(',') if s.strip()}
    job_skills = {s.strip().lower() for s in job_skills_str.split(',') if s.strip()}

    if not job_skills:
        return {'match_percentage': 0, 'matching_skills': [], 'missing_skills': []}

    matching = user_skills & job_skills
    missing = job_skills - user_skills

    percentage = int((len(matching) / len(job_skills)) * 100) if job_skills else 0

    return {
        'match_percentage': percentage,
        'matching_skills': sorted(matching),
        'missing_skills': sorted(missing),
    }


# ==================== RELEVANCE SCORING ====================

def search_jobs(request, queryset=None):
    """
    Advanced job search with smart parsing, filtering, sorting, and relevance scoring.
    Returns context dict with results, parsed query info, and metadata.
    """
    from .models import Job, SearchLog

    if queryset is None:
        queryset = Job.objects.filter(status='open').select_related('company__company_profile', 'category')

    params = request.GET
    query = params.get('q', '').strip()

    # Smart parse the query
    parsed = parse_smart_query(query)

    # === KEYWORD SEARCH ===
    if query:
        keyword_q = (
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(required_skills__icontains=query) |
            Q(location__icontains=query) |
            Q(company__company_profile__company_name__icontains=query)
        )
        # Also search for individual detected skills
        for skill in parsed['detected_skills']:
            keyword_q |= Q(required_skills__icontains=skill)
        queryset = queryset.filter(keyword_q)

    # === EXPLICIT FILTERS ===
    # Job type
    job_type = params.get('type', '') or (parsed['detected_job_type'] if parsed['detected_job_type'] and parsed['detected_job_type'] != 'internship' else '')
    if job_type:
        queryset = queryset.filter(job_type=job_type)

    # Experience level
    experience = params.get('experience', '') or (parsed['detected_experience'] or '')
    if experience:
        queryset = queryset.filter(experience_level=experience)

    # Work mode
    work_mode = params.get('work_mode', '') or (parsed['detected_work_mode'] or '')
    if work_mode:
        queryset = queryset.filter(work_mode=work_mode)

    # Remote filter (backward compat)
    remote = params.get('remote', '')
    if remote == 'yes':
        queryset = queryset.filter(Q(is_remote=True) | Q(work_mode='remote'))

    # Category
    category = params.get('category', '')
    if category:
        queryset = queryset.filter(category__slug=category)

    # Skills filter (multi-select, OR logic)
    skills = params.getlist('skills')
    if skills:
        skills_q = Q()
        for skill in skills:
            s = skill.strip()
            if s:
                skills_q |= Q(required_skills__icontains=s)
        if skills_q:
            queryset = queryset.filter(skills_q)

    # Location
    location = params.get('location', '')
    if location:
        queryset = queryset.filter(location__icontains=location)

    # Date posted
    date_posted = params.get('date_posted', '')
    if date_posted == '24h':
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(hours=24))
    elif date_posted == '7d':
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=7))
    elif date_posted == '30d':
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=30))

    # Salary range
    salary_min = params.get('salary_min', '')
    if salary_min:
        try:
            queryset = queryset.filter(salary_max__gte=int(salary_min))
        except ValueError:
            pass

    salary_max = params.get('salary_max', '')
    if salary_max:
        try:
            queryset = queryset.filter(salary_min__lte=int(salary_max))
        except ValueError:
            pass

    # === SORTING ===
    sort_by = params.get('sort', 'relevance')
    if sort_by == 'latest':
        queryset = queryset.order_by('-is_premium', '-created_at')
    elif sort_by == 'salary_high':
        queryset = queryset.order_by('-is_premium', F('salary_max').desc(nulls_last=True))
    elif sort_by == 'salary_low':
        queryset = queryset.order_by('-is_premium', F('salary_min').asc(nulls_last=True))
    else:
        # Relevance: premium first, then by created_at
        queryset = queryset.order_by('-is_premium', '-created_at')

    # === LOG SEARCH ===
    if query:
        SearchLog.objects.create(
            query=query,
            user=request.user if request.user.is_authenticated else None,
            results_count=queryset.count(),
        )

    return {
        'queryset': queryset,
        'query': query,
        'parsed': parsed,
        'filters': {
            'type': job_type,
            'experience': experience,
            'work_mode': work_mode,
            'remote': remote,
            'category': category,
            'skills': skills,
            'location': location,
            'date_posted': date_posted,
            'salary_min': salary_min,
            'salary_max': salary_max,
            'sort': sort_by,
        },
    }


def search_internships(request, queryset=None):
    """
    Advanced internship search with smart parsing, filtering, sorting.
    Returns context dict with results and metadata.
    """
    from .models import Internship, SearchLog

    if queryset is None:
        queryset = Internship.objects.filter(status='open').select_related('company__company_profile', 'category')

    params = request.GET
    query = params.get('q', '').strip()

    parsed = parse_smart_query(query)

    # === KEYWORD SEARCH ===
    if query:
        keyword_q = (
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(required_skills__icontains=query) |
            Q(location__icontains=query) |
            Q(company__company_profile__company_name__icontains=query)
        )
        for skill in parsed['detected_skills']:
            keyword_q |= Q(required_skills__icontains=skill)
        queryset = queryset.filter(keyword_q)

    # === EXPLICIT FILTERS ===
    internship_type = params.get('type', '')
    if internship_type in ['paid', 'unpaid']:
        queryset = queryset.filter(internship_type=internship_type)

    work_mode = params.get('work_mode', '') or (parsed['detected_work_mode'] or '')
    if work_mode:
        queryset = queryset.filter(work_mode=work_mode)

    category = params.get('category', '')
    if category:
        queryset = queryset.filter(category__slug=category)

    # Skills filter (multi-select, OR logic)
    skills = params.getlist('skills')
    if skills:
        skills_q = Q()
        for skill in skills:
            s = skill.strip()
            if s:
                skills_q |= Q(required_skills__icontains=s)
        if skills_q:
            queryset = queryset.filter(skills_q)

    location = params.get('location', '')
    if location:
        queryset = queryset.filter(location__icontains=location)

    date_posted = params.get('date_posted', '')
    if date_posted == '24h':
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(hours=24))
    elif date_posted == '7d':
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=7))
    elif date_posted == '30d':
        queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=30))

    # Sorting
    sort_by = params.get('sort', 'relevance')
    if sort_by == 'latest':
        queryset = queryset.order_by('-is_premium', '-created_at')
    else:
        queryset = queryset.order_by('-is_premium', '-created_at')

    # Log search
    if query:
        SearchLog.objects.create(
            query=query,
            user=request.user if request.user.is_authenticated else None,
            results_count=queryset.count(),
        )

    return {
        'queryset': queryset,
        'query': query,
        'parsed': parsed,
        'filters': {
            'type': internship_type,
            'work_mode': work_mode,
            'category': category,
            'skills': skills,
            'location': location,
            'date_posted': date_posted,
            'sort': sort_by,
        },
    }


# ==================== AUTO-SUGGESTIONS ====================

def get_auto_suggestions(query, limit=10):
    """
    Get auto-suggestions based on partial query.
    Returns dict with skill_suggestions, title_suggestions, location_suggestions.
    """
    from .models import Job, Internship

    if not query or len(query) < 2:
        return {'skills': [], 'titles': [], 'locations': []}

    query_lower = query.lower().strip()

    # Skill suggestions from common skills list
    skill_suggestions = [s for s in COMMON_SKILLS if query_lower in s][:limit]

    # Title suggestions from existing jobs/internships
    title_suggestions = list(
        Job.objects.filter(status='open', title__icontains=query)
        .values_list('title', flat=True)
        .distinct()[:limit]
    )
    title_suggestions += list(
        Internship.objects.filter(status='open', title__icontains=query)
        .values_list('title', flat=True)
        .distinct()[:limit]
    )
    title_suggestions = list(dict.fromkeys(title_suggestions))[:limit]

    # Location suggestions
    location_suggestions = list(
        Job.objects.filter(status='open', location__icontains=query)
        .values_list('location', flat=True)
        .distinct()[:limit]
    )
    location_suggestions += list(
        Internship.objects.filter(status='open', location__icontains=query)
        .values_list('location', flat=True)
        .distinct()[:limit]
    )
    location_suggestions = list(dict.fromkeys(location_suggestions))[:limit]

    return {
        'skills': skill_suggestions,
        'titles': title_suggestions,
        'locations': location_suggestions,
    }


# ==================== TRENDING SEARCHES ====================

def get_trending_searches(days=7, limit=10):
    """Get trending search queries from the last N days."""
    from .models import SearchLog

    since = timezone.now() - timedelta(days=days)
    recent_searches = (
        SearchLog.objects.filter(created_at__gte=since)
        .values_list('query', flat=True)
    )

    # Count and return most common
    counter = Counter(q.lower().strip() for q in recent_searches if q.strip())
    return [{'query': q, 'count': c} for q, c in counter.most_common(limit)]


# ==================== RECOMMENDED JOBS ====================

def get_recommended_jobs(user, limit=20):
    """
    Get job recommendations based on user's profile skills and past applications.
    Returns list of dicts with job, matching_skills, match_percentage.
    """
    from .models import Job, JobApplication
    from accounts.models import UserProfile

    try:
        profile = UserProfile.objects.get(user=user)
        user_skills = {s.strip().lower() for s in profile.skills.split(',') if s.strip()}
    except UserProfile.DoesNotExist:
        user_skills = set()

    if not user_skills:
        return []

    # Get skills from past applications too
    past_job_skills = (
        JobApplication.objects.filter(applicant=user)
        .values_list('job__required_skills', flat=True)
    )
    for skills_str in past_job_skills:
        if skills_str:
            for s in skills_str.split(','):
                if s.strip():
                    user_skills.add(s.strip().lower())

    # Already applied job IDs
    applied_ids = set(
        JobApplication.objects.filter(applicant=user).values_list('job_id', flat=True)
    )

    jobs = Job.objects.filter(status='open').select_related('company__company_profile', 'category')

    recommendations = []
    for job in jobs:
        if job.pk in applied_ids:
            continue

        match = calculate_skill_match(','.join(user_skills), job.required_skills)
        if match['match_percentage'] > 0:
            # Premium boost
            boost = 10 if job.is_premium else 0
            recommendations.append({
                'job': job,
                'matching_skills': match['matching_skills'],
                'missing_skills': match['missing_skills'],
                'match_percentage': min(match['match_percentage'] + boost, 100),
                'is_premium': job.is_premium,
            })

    recommendations.sort(key=lambda x: (-x['match_percentage'], not x['is_premium']))
    return recommendations[:limit]


# ==================== ALL AVAILABLE SKILLS ====================

def get_all_available_skills():
    """Get all unique skills from open jobs and internships."""
    from .models import Job, Internship

    skills = set()
    for skills_str in Job.objects.filter(status='open').values_list('required_skills', flat=True):
        if skills_str:
            for s in skills_str.split(','):
                if s.strip():
                    skills.add(s.strip())

    for skills_str in Internship.objects.filter(status='open').values_list('required_skills', flat=True):
        if skills_str:
            for s in skills_str.split(','):
                if s.strip():
                    skills.add(s.strip())

    return sorted(skills, key=str.lower)


def get_all_locations():
    """Get all unique locations from open jobs and internships."""
    from .models import Job, Internship

    locations = set()
    for loc in Job.objects.filter(status='open').values_list('location', flat=True).distinct():
        if loc:
            locations.add(loc.strip())
    for loc in Internship.objects.filter(status='open').values_list('location', flat=True).distinct():
        if loc:
            locations.add(loc.strip())

    return sorted(locations, key=str.lower)
