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
        ),
    )

    @email_uncaught_exception
    def handle(self, *args, **options):
        self.tenant = options.get('tenant')
        super(Command, self).handle(**options)

    def _save_new_backup(self, database):
        schema = self.connector.set_schema(self.tenant)
        super(Command, self)._save_new_backup(database)