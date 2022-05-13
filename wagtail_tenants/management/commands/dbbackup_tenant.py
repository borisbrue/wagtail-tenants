from dbbackup import utils
from dbbackup.management.commands._base import make_option
from dbbackup.management.commands.dbbackup import Command as dbbackupCommand

from wagtail_tenants.customers.models import Client, ClientBackup


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

    @utils.email_uncaught_exception
    def handle(self, *args, **options):
        self.tenant = options.get("tenant")
        super(Command, self).handle(**options)

    def _save_new_backup(self, database):
        schema = self.connector.set_schema(self.tenant)

        client = Client.objects.get(schema_name=schema)
        """
        Save a new backup file.
        """
        self.logger.info("Backing Up Tenant Database: %s", database["NAME"])
        # Get backup and name
        filename = self.connector.generate_filename(self.servername)
        outputfile = self.connector.create_dump()
        # Apply trans
        if self.compress:
            compressed_file, filename = utils.compress_file(outputfile, filename)
            outputfile = compressed_file
        if self.encrypt:
            encrypted_file, filename = utils.encrypt_file(outputfile, filename)
            outputfile = encrypted_file
        # Set file name
        filename = self.filename if self.filename else filename
        self.logger.debug("Backup size: %s", utils.handle_size(outputfile))
        # Store backup
        outputfile.seek(0)
        if self.path is None:
            self.write_to_storage(outputfile, filename)
        else:
            self.write_local_file(outputfile, self.path)

        backup = ClientBackup.objects.create(client=client, filename=filename)
        backup.save()
