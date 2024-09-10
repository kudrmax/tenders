DB_TEST_PATH = './test_test.db'
DB_TEST_URL = f'sqlite+aiosqlite:///{DB_TEST_PATH}'
DB_TEST_URL_SYNC = ''.join(DB_TEST_URL.split('+aiosqlite'))
