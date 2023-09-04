from utils import Utilities
from dumper import Dumper

class Secateur(Utilities, Dumper):
    '''
    Doc-string for Secateur class.
    '''

    def drop_schemas(self, schemas: list[str], mode="CASCADE") -> None:
        '''
        Doc-string for drop_schemas() method.
        '''
        for schema in schemas:
            self.execute(f"DROP SCHEMA IF EXISTS {schema} {mode}")

    def truncate_schemas(self, schemas: list[str], ignore_tables: list[str]) -> None:
        '''
        Doc-string for truncate_schemas() method.
        '''
        pass

    def drop_tables(self, tables: list[str], mode="CASCADE") -> None:
        '''
        Doc-string for drop_tables() method.
        '''
        for table in tables:
            self.execute(f"DROP TABLE IF EXISTS {table} {mode}")

    def truncate_tables(self, tables: list[str]) -> None:
        '''
        Doc-string for truncate_tables() method.
        '''
        pass

    def drop_by_mask(self, schemas: list[str], masks: list[str], ignore_tables: list[str]) -> None:
        '''
        Doc-string for drop_by_mask() method.
        '''
        pass

    # def delete_by_condition(self, )

    # delete cascade ???

    # thinout()

    # def refresh_matviews() -> None: 

    # def vacuum() -> None:

# =================================================================================================================== # 

# eng = create_engine('postgresql+psycopg2://postgres:1234@localhost:5432/postgres')
# conn = eng.connect()
# minifier = Secateur(engine=eng, connection=conn, already_exist=True)
minifier = Secateur("postgresql+psycopg2://postgres:1234@localhost:5432/postgres", verbose=True, debug_mode=True)
# pipeline = [
#     minifier.get_table_columns("information_schema.schemata"),
#     minifier.get_schema_tables("information_schema"),
#     minifier.get_count("information_schema.schemata"),
#     minifier.get_dtype("information_schema.schemata", "schema_name"),
#     minifier.execute("SELECT * FROM information_schema.schemata")
# ]
minifier.close()