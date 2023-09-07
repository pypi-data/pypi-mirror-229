import re
from .utils import Utilities
from .dumper import Dumper

class Secateur(Utilities, Dumper):
    """
    Doc-string for Secateur class.
    """
    
    def drop_schemas(self, schemas: list[str], mode="CASCADE") -> None:
        """
        Doc-string for drop_schemas() method.
        """
        if self.engine.driver in self._Utilities__postgresql_drivers:
            for schema in schemas:
                self.execute(f"DROP SCHEMA IF EXISTS {schema} {mode}")
        elif self.engine.driver in self._Utilities__mysql_drivers:
            pass
        elif self.engine.driver in self._Utilities__oracle_drivers:
            pass
        elif self.engine.driver in self._Utilities__mssql_drivers:
            pass
        elif self.engine.driver in self._Utilities__pysqlite_drivers:
            pass
        else:
            raise ValueError(
                "Unsupported driver! Please create an issue on https://github.com/darentydarenty/secateur"
            )

    def truncate_schemas(self, schemas: list[str], mode="RESTART IDENTITY CASCADE", ignore_tables: list[str] = [None]) -> None:
        """
        Doc-string for truncate_schemas() method.
        """
        if self.engine.driver in self._Utilities__postgresql_drivers:
            for schema in schemas:
                tables = self.get_schema_tables(schema)
                tables = [item for item in tables if item not in ignore_tables]
                for table in tables:
                    self.execute(f"TRUNCATE TABLE {table} {mode}")
        elif self.engine.driver in self._Utilities__mysql_drivers:
            pass
        elif self.engine.driver in self._Utilities__oracle_drivers:
            pass
        elif self.engine.driver in self._Utilities__mssql_drivers:
            pass
        elif self.engine.driver in self._Utilities__pysqlite_drivers:
            pass
        else:
            raise ValueError(
                "Unsupported driver! Please create an issue on https://github.com/darentydarenty/secateur"
            )

    def drop_tables(self, tables: list[str], mode="CASCADE") -> None:
        """
        Doc-string for drop_tables() method.
        """
        if self.engine.driver in self._Utilities__postgresql_drivers:
            for table in tables:
                self.execute(f"DROP TABLE IF EXISTS {table} {mode}")
        elif self.engine.driver in self._Utilities__mysql_drivers:
            pass
        elif self.engine.driver in self._Utilities__oracle_drivers:
            pass
        elif self.engine.driver in self._Utilities__mssql_drivers:
            pass
        elif self.engine.driver in self._Utilities__pysqlite_drivers:
            pass
        else:
            raise ValueError(
                "Unsupported driver! Please create an issue on https://github.com/darentydarenty/secateur"
            )

    def truncate_tables(self, tables: list[str], mode="RESTART IDENTITY CASCADE") -> None:
        """
        Doc-string for truncate_tables() method.
        """
        if self.engine.driver in self._Utilities__postgresql_drivers:
            for table in tables:
                self.execute(f"TRUNCATE TABLE {table} {mode}")
        elif self.engine.driver in self._Utilities__mysql_drivers:
            pass
        elif self.engine.driver in self._Utilities__oracle_drivers:
            pass
        elif self.engine.driver in self._Utilities__mssql_drivers:
            pass
        elif self.engine.driver in self._Utilities__pysqlite_drivers:
            pass
        else:
            raise ValueError(
                "Unsupported driver! Please create an issue on https://github.com/darentydarenty/secateur"
            )

    def drop_by_mask(self, schemas: list[str], masks: list[str], mode: str = "CASCADE", ignore_tables: list[str] = [None]) -> None:
        """
        Doc-string for drop_by_mask() method.
        """
        if self.engine.driver in self._Utilities__postgresql_drivers:
            candidates = []
            for schema in schemas:
                tables = self.get_schema_tables(schema)
                tables = [item for item in tables if item not in ignore_tables]
                for mask in masks:
                    candidates += [item for item in tables if re.match(fr"\b\w*.\b\w*{mask}\w*\b", item)]
            self.drop_tables(candidates, mode)
        elif self.engine.driver in self._Utilities__mysql_drivers:
            pass
        elif self.engine.driver in self._Utilities__oracle_drivers:
            pass
        elif self.engine.driver in self._Utilities__mssql_drivers:
            pass
        elif self.engine.driver in self._Utilities__pysqlite_drivers:
            pass
        else:
            raise ValueError(
                "Unsupported driver! Please create an issue on https://github.com/darentydarenty/secateur"
            )
        
    def delete_by_condition(self, tables: list[str], condition: str) -> None:
        """
        Doc-string for delete_by_condition() method.
        """
        if self.engine.driver in self._Utilities__postgresql_drivers:
            for table in tables:
                self.execute(f"DELETE FROM {table} {condition}")
        elif self.engine.driver in self._Utilities__mysql_drivers:
            pass
        elif self.engine.driver in self._Utilities__oracle_drivers:
            pass
        elif self.engine.driver in self._Utilities__mssql_drivers:
            pass
        elif self.engine.driver in self._Utilities__pysqlite_drivers:
            pass
        else:
            raise ValueError(
                "Unsupported driver! Please create an issue on https://github.com/darentydarenty/secateur"
            )

    def thinout(self, tables: list[str], n: int) -> None:
        """
        Doc-string for thinout() method.
        """
        if self.engine.driver in self._Utilities__postgresql_drivers:
            for table in tables:
                self.execute(f"DELETE FROM {table} WHERE ctid IN (SELECT ctid FROM (SELECT ctid, ROW_NUMBER() OVER () AS row FROM {table}) sub WHERE MOD(row, {n}) = 0)")
        elif self.engine.driver in self._Utilities__mysql_drivers:
            pass
        elif self.engine.driver in self._Utilities__oracle_drivers:
            pass
        elif self.engine.driver in self._Utilities__mssql_drivers:
            pass
        elif self.engine.driver in self._Utilities__pysqlite_drivers:
            pass
        else:
            raise ValueError(
                "Unsupported driver! Please create an issue on https://github.com/darentydarenty/secateur"
            )

    def refresh_matviews(self) -> None:
        """
        Doc-string for refresh_matviews() method.
        """
        if self.engine.driver in self._Utilities__postgresql_drivers:
            matviews = self.execute("SELECT schemaname || '.' || matviewname FROM pg_matviews")
            for view in matviews:
                self.execute(f"REFRESH MATERIALIZED VIEW {view}")
        elif self.engine.driver in self._Utilities__mysql_drivers:
            pass
        elif self.engine.driver in self._Utilities__oracle_drivers:
            pass
        elif self.engine.driver in self._Utilities__mssql_drivers:
            pass
        elif self.engine.driver in self._Utilities__pysqlite_drivers:
            pass
        else:
            raise ValueError(
                "Unsupported driver! Please create an issue on https://github.com/darentydarenty/secateur"
            )

    def reindex(self, obj: str = "DATABASE", mode: str = "", name: str = "") -> None:
        """
        Doc-string for reindex() method.
        """
        if self.engine.driver in self._Utilities__postgresql_drivers:
            self.execute(f"REINDEX {obj} {mode} {name}")
        elif self.engine.driver in self._Utilities__mysql_drivers:
            pass
        elif self.engine.driver in self._Utilities__oracle_drivers:
            pass
        elif self.engine.driver in self._Utilities__mssql_drivers:
            pass
        elif self.engine.driver in self._Utilities__pysqlite_drivers:
            pass
        else:
            raise ValueError(
                "Unsupported driver! Please create an issue on https://github.com/darentydarenty/secateur"
            )

    # Подумать над вакуумом
    def vacuum(self, tables: list[str], mode="FULL") -> None:
        """
        Doc-string for vacuum() method.
        """
        if self.engine.driver in self._Utilities__postgresql_drivers:
            for table in tables:
                self.execute(f"VACUUM {mode} {table}") 
        elif self.engine.driver in self._Utilities__mysql_drivers:
            pass
        elif self.engine.driver in self._Utilities__oracle_drivers:
            pass
        elif self.engine.driver in self._Utilities__mssql_drivers:
            pass
        elif self.engine.driver in self._Utilities__pysqlite_drivers:
            pass
        else:
            raise ValueError(
                "Unsupported driver! Please create an issue on https://github.com/darentydarenty/secateur"
            )