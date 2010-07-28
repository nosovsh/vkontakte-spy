from django.core.management.base import NoArgsCommand

from vkontakte_spy.views import run_parsersfuncs


class Command(NoArgsCommand):
    help = "Can be run as a cronjob or directly to run all parsers functions from Timetable."

    def handle_noargs(self, **options):
        run_parsersfuncs()
