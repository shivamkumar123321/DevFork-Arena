import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection_string = os.getenv("TIGERDATA_CONNECTION_STRING")
        self.connection = None

    async def connect(self):
        """Establish connection to TigerData Postgres"""
        try:
            self.connection = await psycopg.AsyncConnection.connect(
                self.connection_string,
                row_factory=dict_row
            )
            logger.info("Successfully connected to TigerData Postgres")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    async def disconnect(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")

    async def execute_query(self, query: str, params: tuple = None):
        """Execute a query and return results"""
        try:
            async with self.connection.cursor() as cur:
                await cur.execute(query, params)
                if cur.description:
                    return await cur.fetchall()
                return None
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    async def execute_many(self, query: str, params_list: list):
        """Execute multiple queries with different parameters"""
        try:
            async with self.connection.cursor() as cur:
                await cur.executemany(query, params_list)
                await self.connection.commit()
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            raise

# Global database instance
db = Database()
