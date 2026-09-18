import re
import hashlib
import secrets
import base64
import json
import os
from pathlib import Path

import hashlib
import ctypes
import ctypes.wintypes
import struct


IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

PII_PATTERNS = {
    "cpf": re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'),
    "cnpj": re.compile(r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b'),
    "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "phone": re.compile(r'\b(?:\+?55\s?)?\(?\d{2}\)?\s?-?\d{4,5}-?\d{4}\b'),
    "card": re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
    "cep": re.compile(r'\b\d{5}-?\d{3}\b'),
}


def validate_identifier(name, label="identifier"):
    if not name or not isinstance(name, str):
        raise ValueError(f"Invalid {label}: cannot be empty")
    if not IDENTIFIER_PATTERN.match(name):
        raise ValueError(
            f"Invalid {label}: '{name}' contains forbidden characters. "
            f"Only letters, numbers and underscores are allowed."
        )
    if len(name) > 63:
        raise ValueError(f"Invalid {label}: '{name}' exceeds 63 characters")
    sql_keywords = {
        "select", "insert", "update", "delete", "drop", "alter", "create",
        "truncate", "grant", "revoke", "exec", "execute", "union", "where",
        "and", "or", "not", "in", "between", "like", "having", "group",
        "order", "by", "limit", "offset", "join", "inner", "outer", "left",
        "right", "cross", "on", "as", "into", "values", "set", "from",
        "table", "index", "view", "database", "schema", "role", "user",
        "password", "comment", "null", "is", "true", "false", "case",
        "when", "then", "else", "end", "begin", "commit", "rollback",
        "savepoint", "lock", "explain", "analyze", "vacuum", "reindex",
        "copy", "listen", "notify", "discard", "fetch", "move", "close",
        "declare", "cursor", "prepare", "deallocate", "do", "grant",
        "revoke", "comment", "security", "definer", "invoker", "stable",
        "volatile", "strict", "leakproof", "cost", "rows", "function",
        "trigger", "constraint", "check", "default", "primary", "foreign",
        "key", "references", "unique", "exclude", "deferrable", "initally",
        "deferred", "not", "enforced", "validate", "before", "after",
        "instead", "each", "row", "statement", "sql", "plpgsql", "c",
        "internal", "language", "window", "partition", "over", "exists",
        "all", "any", "some", "distinct", "recursive", "lateral", "only",
    }
    if name.lower() in sql_keywords:
        raise ValueError(f"Invalid {label}: '{name}' is a SQL reserved keyword")
    return name


def mask_pii(text):
    if not isinstance(text, str):
        return text
    masked = text
    for pii_type, pattern in PII_PATTERNS.items():
        if pii_type == "cpf":
            masked = pattern.sub("[CPF_REDACTED]", masked)
        elif pii_type == "cnpj":
            masked = pattern.sub("[CNPJ_REDACTED]", masked)
        elif pii_type == "email":
            masked = pattern.sub("[EMAIL_REDACTED]", masked)
        elif pii_type == "phone":
            masked = pattern.sub("[PHONE_REDACTED]", masked)
        elif pii_type == "card":
            masked = pattern.sub("[CARD_REDACTED]", masked)
        elif pii_type == "cep":
            masked = pattern.sub("[CEP_REDACTED]", masked)
    return masked


def mask_dataframe(df, sensitive_columns=None):
    import pandas as pd
    if df is None or df.empty:
        return df

    df_masked = df.copy()

    if sensitive_columns is None:
        sensitive_keywords = [
            "nome", "name", "email", "telefone", "phone", "cpf", "cnpj",
            "endereco", "address", "cidade", "city", "estado", "state",
            "cep", "zip", "card", "cartao", "senha", "password", "token",
            "secret", "key", "social", "ssn", "birth", "nascimento",
            "cliente", "customer", "user", "usuario", "pessoa", "person",
        ]
        sensitive_columns = []
        for col in df_masked.columns:
            if any(kw in col.lower() for kw in sensitive_keywords):
                sensitive_columns.append(col)

    for col in sensitive_columns:
        if col in df_masked.columns:
            df_masked[col] = df_masked[col].apply(
                lambda x: f"[{col.upper()}_REDACTED]" if pd.notna(x) and str(x).strip() else x
            )

    for col in df_masked.columns:
        if df_masked[col].dtype == object:
            df_masked[col] = df_masked[col].apply(
                lambda x: mask_pii(str(x)) if pd.notna(x) else x
            )

    return df_masked


def mask_dict_list(data_list, sensitive_keys=None):
    if not data_list:
        return data_list

    if sensitive_keys is None:
        sensitive_keywords = [
            "nome", "name", "email", "telefone", "phone", "cpf", "cnpj",
            "endereco", "address", "senha", "password", "token", "secret",
            "cliente", "customer", "user", "usuario",
        ]
        sensitive_keys = set()
        for row in data_list:
            for key in row.keys():
                if any(kw in key.lower() for kw in sensitive_keywords):
                    sensitive_keys.add(key)

    masked_list = []
    for row in data_list:
        masked_row = dict(row)
        for key in sensitive_keys:
            if key in masked_row and masked_row[key] is not None:
                masked_row[key] = f"[{key.upper()}_REDACTED]"
        for key, val in masked_row.items():
            if isinstance(val, str):
                masked_row[key] = mask_pii(val)
        masked_list.append(masked_row)
    return masked_list


class SecureStorage:
    APP_NAME = "DataPulse"

    @staticmethod
    def _get_dpapi():
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData", ctypes.wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

        return ctypes.windll.crypt32, DATA_BLOB

    @staticmethod
    def encrypt(plaintext):
        crypt32, DATA_BLOB = SecureStorage._get_dpapi()
        data = plaintext.encode("utf-8")
        input_blob = DATA_BLOB(len(data), ctypes.create_string_buffer(data, len(data)))
        output_blob = DATA_BLOB()
        if crypt32.CryptProtectData(
            ctypes.byref(input_blob), None, None, None, None, 0, ctypes.byref(output_blob)
        ):
            encrypted = ctypes.string_at(output_blob.pbData, output_blob.cbData)
            ctypes.windll.kernel32.LocalFree(output_blob.pbData)
            return base64.b64encode(encrypted).decode("ascii")
        raise RuntimeError("Failed to encrypt with DPAPI")

    @staticmethod
    def decrypt(encrypted_b64):
        crypt32, DATA_BLOB = SecureStorage._get_dpapi()
        encrypted = base64.b64decode(encrypted_b64)
        input_blob = DATA_BLOB(len(encrypted), ctypes.create_string_buffer(encrypted, len(encrypted)))
        output_blob = DATA_BLOB()
        if crypt32.CryptUnprotectData(
            ctypes.byref(input_blob), None, None, None, None, 0, ctypes.byref(output_blob)
        ):
            decrypted = ctypes.string_at(output_blob.pbData, output_blob.cbData)
            ctypes.windll.kernel32.LocalFree(output_blob.pbData)
            return decrypted.decode("utf-8")
        raise RuntimeError("Failed to decrypt with DPAPI")

    @staticmethod
    def save_credential(key, value):
        storage_path = Path.home() / ".datapulse" / "credentials.enc"
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        store = {}
        if storage_path.exists():
            try:
                store = json.loads(SecureStorage.decrypt(storage_path.read_text()))
            except Exception:
                store = {}
        store[key] = SecureStorage.encrypt(value)
        storage_path.write_text(SecureStorage.encrypt(json.dumps(store)))
        if os.name == "nt":
            ctypes.windll.kernel32.SetFileAttributesW(str(storage_path), 0x02)

    @staticmethod
    def load_credential(key):
        storage_path = Path.home() / ".datapulse" / "credentials.enc"
        if not storage_path.exists():
            return None
        try:
            store = json.loads(SecureStorage.decrypt(storage_path.read_text()))
            encrypted_val = store.get(key)
            if encrypted_val:
                return SecureStorage.decrypt(encrypted_val)
        except Exception:
            return None
        return None

    @staticmethod
    def delete_credential(key):
        storage_path = Path.home() / ".datapulse" / "credentials.enc"
        if not storage_path.exists():
            return
        try:
            store = json.loads(SecureStorage.decrypt(storage_path.read_text()))
            if key in store:
                del store[key]
                storage_path.write_text(SecureStorage.encrypt(json.dumps(store)))
        except Exception:
            pass


def hash_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def generate_salt(length=32):
    return secrets.token_hex(length)


def validate_ssl_mode(mode):
    valid_modes = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}
    if mode not in valid_modes:
        raise ValueError(f"Invalid SSL mode: '{mode}'. Must be one of: {valid_modes}")
    return mode
