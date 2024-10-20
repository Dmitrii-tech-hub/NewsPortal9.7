from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
import logging
from simpleapp.tasks import send_weekly_posts

logger = logging.getLogger(__name__)

def delete_old_job_executions(max_age=604_800):
    """Удаление старых записей о задачах из базы данных"""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class Command(BaseCommand):
    help = "Запуск APScheduler"

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Еженедельная рассылка
        scheduler.add_job(
            send_weekly_posts,
            trigger="interval",
            weeks=1,
            id="weekly_posts",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача 'send_weekly_posts'.")

        # Удаление старых задач
        scheduler.add_job(
            delete_old_job_executions,
            trigger="interval",
            days=7,
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача 'delete_old_job_executions'.")

        try:
            scheduler.start()
            logger.info("Запущен планировщик.")
        except Exception as e:
            logger.error(f"Ошибка при запуске планировщика: {e}")
            scheduler.shutdown()

        self.stdout.write(self.style.SUCCESS("Планировщик запущен!"))
