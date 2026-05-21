#!/usr/bin/env python3
"""Oracle to PostgreSQL Data Type and SQL Converters"""
import re
from typing import Dict, List
from enum import Enum

class ContentType(Enum):
    ALL = 'ALL'
    METADATA_ONLY = 'METADATA_ONLY'
    DATA_ONLY = 'DATA_ONLY'

class DataTypeConverter:
    TYPE_MAPPINGS = {
        r'VARCHAR2\s*\(\s*(\d+)\s*\)': r'VARCHAR(\1)',
        r'CHAR\s*\(\s*(\d+)\s*\)': r'CHAR(\1)',
        r'NUMBER\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)': r'NUMERIC(\1,\2)',
        r'NUMBER\s*\(\s*(\d+)\s*\)': r'INTEGER',
        r'NUMBER(?!\s*\()': 'NUMERIC',
        r'CLOB': 'TEXT',
        r'BLOB': 'BYTEA',
        r'DATE': 'TIMESTAMP',
        r'RAW\s*\(\s*(\d+)\s*\)': r'BYTEA',
    }
    
    @classmethod
    def convert_type(cls, oracle_type: str) -> str:
        oracle_type = oracle_type.strip()
        for pattern, replacement in cls.TYPE_MAPPINGS.items():
            match = re.search(pattern, oracle_type, re.IGNORECASE)
            if match:
                return re.sub(pattern, replacement, oracle_type, flags=re.IGNORECASE)
        return oracle_type

class FunctionConverter:
    FUNCTION_MAPPINGS = {
        r'\bSUBSTR\s*\(': 'SUBSTRING(',
        r'\bNVL\s*\(': 'COALESCE(',
        r'\bSYSDATE\b': 'CURRENT_DATE',
        r'\bSYSTIMESTAMP\b': 'CURRENT_TIMESTAMP',
    }
    
    @classmethod
    def convert_functions(cls, sql: str) -> str:
        result = sql
        for oracle_func, pg_func in cls.FUNCTION_MAPPINGS.items():
            result = re.sub(oracle_func, pg_func, result, flags=re.IGNORECASE)
        return result

class ConstraintConverter:
    @staticmethod
    def convert_constraint(constraint: Dict) -> str:
        constraint_type = constraint.get('type', '').upper()
        if constraint_type == 'PRIMARY_KEY':
            columns = ', '.join(constraint['columns'])
            return f"PRIMARY KEY ({columns})"
        elif constraint_type == 'UNIQUE':
            columns = ', '.join(constraint['columns'])
            return f"UNIQUE ({columns})"
        elif constraint_type == 'CHECK':
            expression = constraint['expression']
            return f"CHECK ({expression})"
        elif constraint_type == 'FOREIGN_KEY':
            fk_name = constraint.get('name', 'fk_constraint')
            columns = ', '.join(constraint['columns'])
            ref_table = constraint['ref_table']
            ref_columns = ', '.join(constraint['ref_columns'])
            on_delete = constraint.get('on_delete', 'RESTRICT')
            return f"CONSTRAINT {fk_name} FOREIGN KEY ({columns}) REFERENCES {ref_table}({ref_columns}) ON DELETE {on_delete}"
        return ""

class IndexConverter:
    @staticmethod
    def convert_index(index: Dict) -> str:
        index_name = index['name']
        table_name = index['table']
        columns = ', '.join(index['columns'])
        is_unique = index.get('unique', False)
        unique_keyword = "UNIQUE " if is_unique else ""
        return f"CREATE {unique_keyword}INDEX {index_name} ON {table_name}({columns});"

class SequenceConverter:
    @staticmethod
    def convert_sequence_def(sequence: Dict) -> str:
        name = sequence['name']
        schema = sequence.get('schema', 'public')
        start_value = sequence.get('start_value', 1)
        return f"CREATE SEQUENCE {schema}.{name} START {start_value};"

class OracletoPostgreSQL:
    @classmethod
    def convert_create_table(cls, oracle_ddl: str) -> str:
        result = oracle_ddl
        oracle_clauses = [r'TABLESPACE\s+\w+', r'PCTFREE\s+\d+', r'PCTUSED\s+\d+']
        for clause in oracle_clauses:
            result = re.sub(clause, '', result, flags=re.IGNORECASE)
        for pattern, replacement in DataTypeConverter.TYPE_MAPPINGS.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        result = FunctionConverter.convert_functions(result)
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r',\s*\)', ')', result)
        return result.strip()