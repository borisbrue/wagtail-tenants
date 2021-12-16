from dbbackup.management.commands._base import make_option
from dbbackup.management.commands.dbbackup import Command as dbbackupCommand


class Command(dbbackupCommand):

    option_list = dbbackupCommand.option_list + (
        make_option(
            "-tenant",
            "--schema",
            default="public",
            help="Specify the tenant schema you want to backup",
        )
    )
