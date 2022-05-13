from dbbackup.db.postgresql import PgDumpBinaryConnector
from dbbackup.utils import filename_generate

from wagtail_tenants.customers.models import ClientBackup


class TenantPgDumpBinaryConnector(PgDumpBinaryConnector):
    """
    PostgreSQL connector, it uses pg_dump`` to create an SQL text file
    and ``pg_restore`` for restore it.
    """

    extension = "psql.bin"
    dump_cmd = "pg_dump"
    restore_cmd = "pg_restore"
    single_transaction = True
    drop = True
    tenant = "public"

    def _create_dump(self):
        cmd = "{} {}".format(self.dump_cmd, self.settings["NAME"])
        if self.settings.get("HOST"):
            cmd += " --host={}".format(self.settings["HOST"])
        if self.settings.get("PORT"):
            cmd += " --port={}".format(self.settings["PORT"])
        if self.settings.get("USER"):
            cmd += " --user={}".format(self.settings["USER"])
        cmd += " --no-password"
        cmd += " --format=custom"
        cmd += " --schema={}".format(self.tenant)
        for table in self.exclude:
            cmd += " --exclude-table={}".format(table)
        cmd = "{} {} {}".format(self.dump_prefix, cmd, self.dump_suffix)
        stdout, stderr = self.run_command(cmd, env=self.dump_env)
        return stdout

    def _restore_dump(self, dump):
        cmd = "{} --dbname={}".format(self.restore_cmd, self.settings["NAME"])
        if self.settings.get("HOST"):
            cmd += " --host={}".format(self.settings["HOST"])
        if self.settings.get("PORT"):
            cmd += " --port={}".format(self.settings["PORT"])
        if self.settings.get("USER"):
            cmd += " --user={}".format(self.settings["USER"])
        cmd += " --no-password"
        if self.single_transaction:
            cmd += " --single-transaction"
        if self.drop:
            cmd += " --clean"
        cmd = "{} {} {}".format(self.restore_prefix, cmd, self.restore_suffix)
        stdout, stderr = self.run_command(cmd, stdin=dump, env=self.restore_env)
        return stdout, stderr

    def generate_filename(self, server_name=None):
        self.database_name = self.database_name + "-" + self.tenant
        return filename_generate(self.extension, self.database_name, server_name)

    def set_schema(self, schema):
        self.tenant = schema
        return schema
