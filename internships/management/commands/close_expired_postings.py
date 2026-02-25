from django.core.management.base import BaseCommand
from django.utils import timezone
from internships.models import Job, Internship


class Command(BaseCommand):
    help = 'Close jobs and internships whose deadline has passed'

    def handle(self, *args, **options):
        today = timezone.now().date()

        expired_jobs = Job.objects.filter(
            status='open', deadline__lt=today
        ).update(status='closed')

        expired_internships = Internship.objects.filter(
            status='open', deadline__lt=today
        ).update(status='closed')

        total = expired_jobs + expired_internships
        self.stdout.write(self.style.SUCCESS(
            f'Closed {expired_jobs} job(s) and {expired_internships} internship(s) ({total} total)'
        ))
