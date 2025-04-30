import sqlite3
import threading
from datetime import datetime
import json
import logging

# ==== Configuración de logging ====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SqliteManager(threading.Thread):
    def __init__(self, rs232, stop_event):
        super().__init__()
        self.rs232 = rs232
        self.stop_event = stop_event
        self.current_validation_index = 0

        self.uuid = "idprueba"
        self.place = "Parada de prueba"
        self.lat = "0.0"
        self.lon = "0.0"

        self._create_tables()

    def run(self):
        logger.info("SqliteManager thread started")
        while not self.stop_event.is_set():
            with self.rs232.lock:
                if self.rs232.validation and self.rs232.n_validations != self.current_validation_index:
                    try:
                        self._register_transaction()
                        self.current_validation_index = self.rs232.n_validations
                    except Exception as e:
                        logger.error(f"Failed to register transaction: {e}")

    def _register_transaction(self):
        raw_data = str(self.rs232.data[1:-1])
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        try:
            card_code = raw_data[25:34]
            card_type = int(raw_data[14:18])
            card_date = f"{raw_data[6:8]}/{raw_data[8:10]}/{raw_data[10:14]}"
            card_time = f"{raw_data[0:2]}:{raw_data[2:4]}:{raw_data[4:6]}"
            cost = float(int(raw_data[46:54]) / 100)
            prev_balance = float(int(raw_data[38:46]) / 100)
            curr_balance = float(int(raw_data[-8:]) / 100)
        except (ValueError, IndexError) as e:
            raise ValueError("Error parsing card data") from e

        data = (
            card_code, card_type, card_date, card_time,
            self.place, cost, prev_balance, curr_balance,
            self.uuid, self.lat, self.lon, timestamp
        )
        self._insert_transaction(data)
        logger.info(f"Transaction successful! CODE: {card_code}")

    def _create_tables(self):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY, 
                code TEXT NOT NULL,
                type TEXT NOT NULL,
                date_card TEXT NOT NULL,
                time_card TEXT NOT NULL,
                place TEXT NOT NULL,
                cost REAL NOT NULL,
                previous REAL NOT NULL,
                balance REAL NOT NULL,
                uuid TEXT NOT NULL,
                lat TEXT NOT NULL,
                lon TEXT NOT NULL,
                loaded BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS parameters (
                id INTEGER PRIMARY KEY,
                place TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                bus_station_id TEXT NOT NULL,
                lat TEXT NOT NULL,
                lon TEXT NOT NULL
            );
            """
        ]

        try:
            with sqlite3.connect("app.db") as conn:
                cursor = conn.cursor()
                for query in queries:
                    cursor.execute(query)
                conn.commit()
            logger.info("Tables created or verified successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")

    def _insert_transaction(self, data):
        query = """
            INSERT INTO transactions (
                code, type, date_card, time_card,
                place, cost, previous, balance,
                uuid, lat, lon, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with sqlite3.connect("app.db") as conn:
                cursor = conn.cursor()
                cursor.execute(query, data)
                conn.commit()
                logger.debug(f"Inserted transaction ID: {cursor.lastrowid}")
        except sqlite3.Error as e:
            logger.error(f"Error inserting transaction: {e}")

    def _insert_parameter(self, data):
        query = """
            INSERT INTO parameters (
                place, created_at, bus_station_id, lat, lon
            ) VALUES (?, ?, ?, ?, ?)
        """
        try:
            with sqlite3.connect("app.db") as conn:
                cursor = conn.cursor()
                cursor.execute(query, data)
                conn.commit()
                logger.debug(f"Inserted parameter ID: {cursor.lastrowid}")
        except sqlite3.Error as e:
            logger.error(f"Error inserting parameter: {e}")

    def get_all_transactions(self):
        return self._query_results("SELECT * FROM transactions")

    def get_last_transactions(self, limit=10):
        return self._query_results(f"SELECT * FROM transactions ORDER BY created_at DESC LIMIT {limit}")

    def get_all_parameters(self):
        data = self._query_results("SELECT * FROM parameters")
        return json.dumps(data, indent=4)

    def get_current_parameters(self):
        try:
            with sqlite3.connect("app.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM parameters ORDER BY id DESC LIMIT 1")
                return cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"Error fetching current parameter: {e}")

    def _query_results(self, query):
        try:
            with sqlite3.connect("app.db") as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Query failed: {e}")
            return []
