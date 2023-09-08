import unittest
from src.umbitlib import db_connections
from src.umbitlib.db_connections import SecurityHandler, DatabaseEngine, SqlHandler


class TestSecurityHandler(unittest.TestCase):
    def test_valid_service_name(self):
        # Test if initializing with a valid destination doesn't raise an exception
        valid_service_name = 'oracle'
        sec_io = SecurityHandler(valid_service_name)
        self.assertEqual(sec_io.service_name, valid_service_name)

    def test_invalid_service_name(self):
        # Test if initializing with an invalid service_name raises a ValueError
        invalid_service_name = 'invalid_service_name'
        with self.assertRaises(ValueError):
            db_connections.SecurityHandler(invalid_service_name)


class TestDatabaseEngine(unittest.TestCase):
    def testDatabaseEngine(self):
        orc = DatabaseEngine('oracle')
        self.assertIsNotNone(orc)


class TestSqlHandler(unittest.TestCase):
    def testConnectOracle(self):
        oracle = SqlHandler('oracle')
        conn = oracle.connect()
        self.assertIsNotNone(conn)
        conn.close()

    def testConnectPostgres(self):
        pg = SqlHandler('postgres_dev')
        conn = pg.connect()
        self.assertIsNotNone(conn)
        conn.close()

    def testQueryOracle(self):
        query_str = """
                SELECT NAME
                FROM CLARITY_REPORT.ZC_STATE
                WHERE ABBR = 'AK'
                """
        oracle = SqlHandler('oracle')
        df = oracle.query(query_str)
        self.assertEqual(df['name'][0], 'Alaska')

    def testQueryPg(self):
        query_str = """
                SELECT * FROM public.pages_glossary where id = 41
                """
        pg = SqlHandler('postgres_dev')
        df = pg.query(query_str)
        self.assertEqual(df['id'][0], 41)

    def testUploadDfTrunc(self):
        orc = SqlHandler('oracle')
        pg = SqlHandler('postgres_dev')
        df = orc.query('select * from clarity_report.zc_state')
        pg.upload_df(df, 'umbitlib_test_table', 'truncate')
        pgdf = pg.query("select * from public.umbitlib_test_table where state_c = '1'")
        self.assertEqual(pgdf['abbr'][0], 'AL')

    def testUploadDfReplace(self):
        orc = SqlHandler('oracle')
        pg = SqlHandler('postgres_dev')
        df = orc.query('select * from clarity_report.zc_state')
        pg.upload_df(df, 'umbitlib_test_table', 'replace')
        pgdf = pg.query("select * from public.umbitlib_test_table where state_c = '1'")
        self.assertEqual(pgdf['abbr'][0], 'AL')