from django.core.management.base import BaseCommand
from internships.models import RejectionTag, AcceptanceTag


class Command(BaseCommand):
    help = 'Seed predefined rejection and acceptance tags for the screening system'

    def handle(self, *args, **options):
        rejection_tags = [
            {'slug': 'course_mismatch', 'name': 'Course Mismatch', 'description': "Applicant's course/degree does not match requirements", 'sort_order': 1},
            {'slug': 'skills_not_matching', 'name': 'Skills Not Matching', 'description': "Required skills not found in applicant's profile", 'sort_order': 2},
            {'slug': 'insufficient_experience', 'name': 'Insufficient Experience', 'description': 'Does not meet minimum experience requirements', 'sort_order': 3},
            {'slug': 'location_issue', 'name': 'Location Issue', 'description': "Applicant's location is not suitable for this position", 'sort_order': 4},
            {'slug': 'poor_english', 'name': 'Poor English', 'description': 'English proficiency below required level', 'sort_order': 5},
            {'slug': 'poor_internet', 'name': 'Poor Internet Setup', 'description': 'Internet quality insufficient for remote work', 'sort_order': 6},
            {'slug': 'failed_assessment', 'name': 'Failed Assessment', 'description': 'Did not pass required skill assessments', 'sort_order': 7},
            {'slug': 'low_interview_score', 'name': 'Low Interview Score', 'description': 'Performance in interview was below expectations', 'sort_order': 8},
            {'slug': 'overqualified', 'name': 'Overqualified', 'description': 'Applicant is overqualified for this position', 'sort_order': 9},
            {'slug': 'incomplete_profile', 'name': 'Incomplete Profile', 'description': "Applicant's profile is not complete enough", 'sort_order': 10},
            {'slug': 'low_gpa', 'name': 'Low GPA', 'description': 'GPA is below the minimum requirement', 'sort_order': 11},
            {'slug': 'poor_communication', 'name': 'Poor Communication', 'description': 'Communication skills need improvement', 'sort_order': 12},
        ]

        acceptance_tags = [
            {'slug': 'strong_technical', 'name': 'Strong Technical Skills', 'description': 'Excellent technical skill match', 'sort_order': 1},
            {'slug': 'high_assessment', 'name': 'High Assessment Score', 'description': 'Outstanding performance in skill assessments', 'sort_order': 2},
            {'slug': 'good_communication', 'name': 'Good Communication', 'description': 'Strong communication and interpersonal skills', 'sort_order': 3},
            {'slug': 'suitable_location', 'name': 'Suitable Location', 'description': 'Location is convenient for the role', 'sort_order': 4},
            {'slug': 'cultural_fit', 'name': 'Cultural Fit', 'description': 'Good cultural alignment with company values', 'sort_order': 5},
            {'slug': 'prior_experience', 'name': 'Prior Experience', 'description': 'Relevant prior experience in similar roles', 'sort_order': 6},
            {'slug': 'strong_portfolio', 'name': 'Strong Portfolio', 'description': 'Impressive portfolio/projects demonstrated', 'sort_order': 7},
            {'slug': 'high_gpa', 'name': 'High GPA', 'description': 'Academic performance exceeds expectations', 'sort_order': 8},
            {'slug': 'leadership_quality', 'name': 'Leadership Quality', 'description': 'Demonstrates strong leadership potential', 'sort_order': 9},
            {'slug': 'quick_learner', 'name': 'Quick Learner', 'description': 'Shows ability to adapt and learn quickly', 'sort_order': 10},
        ]

        r_created = 0
        for tag_data in rejection_tags:
            _, created = RejectionTag.objects.update_or_create(
                slug=tag_data['slug'],
                defaults=tag_data,
            )
            if created:
                r_created += 1

        a_created = 0
        for tag_data in acceptance_tags:
            _, created = AcceptanceTag.objects.update_or_create(
                slug=tag_data['slug'],
                defaults=tag_data,
            )
            if created:
                a_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {r_created} rejection tags and {a_created} acceptance tags '
            f'({len(rejection_tags)} rejection, {len(acceptance_tags)} acceptance total)'
        ))
