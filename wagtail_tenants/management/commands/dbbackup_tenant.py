from dbbackup.management.commands._base import make_option
from dbbackup.management.commands.dbbackup import Command as dbbackupCommand
from dbbackup.utils import email_uncaught_exception

class Command(dbbackupCommand):
    option_list = dbbackupCommand.option_list + (
        make_option(
            "-t",
            "--tenant",
            dest="tenant",
            default="public",
            help="Specify the tenant schema you want to backup",
        )
    )
    
    @email_uncaught_exception
    def handle(self, **options):
        super(self).handle(**options)