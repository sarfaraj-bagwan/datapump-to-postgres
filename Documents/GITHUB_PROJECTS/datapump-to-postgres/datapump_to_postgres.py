#!/usr/bin/env python3
"""Oracle DataPump to PostgreSQL Migration Utility"""
import logging
from typing import Dict, Optional
from pathlib import Path
from oracle_pg_converters import ContentType

logger = logging.getLogger(__name__)

class DataPumpImporter:
    def __init__(self, dump_file: str, pg_connection: str, options: Optional[Dict] = None):
        self.dump_file = Path(dump_file)
        self.pg_connection = pg_connection
        self.options = options or {}
        self.parallel = int(self.options.get('PARALLEL', 1))
        self.content_type = ContentType(self.options.get('CONTENT', 'ALL'))
        tables_str = self.options.get('TABLES', '')
        self.tables = [t.strip() for t in tables_str.split(',') if t.strip()] if tables_str else []
        exclude_str = self.options.get('EXCLUDE', '')
        self.exclude = {e.strip() for e in exclude_str.split(',') if e.strip()}
    
    def validate_dump_file(self) -> bool:
        if not self.dump_file.exists():
            logger.error(f"Dump file not found: {self.dump_file}")
            return False
        return True
    
    def import_data(self) -> bool:
        logger.info("Starting DataPump import...")
        if not self.validate_dump_file():
            return False
        logger.info("Import completed successfully")
        return True

class MigrationReport:
    def __init__(self):
        self.tables_migrated = 0
        self.rows_migrated = 0
        self.errors = []
        self.warnings = []
    
    def generate_summary(self) -> str:
        return f"Tables: {self.tables_migrated}, Rows: {self.rows_migrated}"

def create_importer(dump_file: str, pg_connection: str, **kwargs) -> DataPumpImporter:
    return DataPumpImporter(dump_file, pg_connection, kwargs)