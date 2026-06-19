"""SQLite schema and shared database helpers for the PBM application.

This module owns the database location, schema creation, lightweight migrations,
and a few read helpers used by the API, audit logger, and dashboard.
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

DB_PATH = Path(__file__).resolve().parents[2] / "pbm.db"


def current_timestamp() -> str:
    """Return a UTC timestamp string suitable for SQLite storage."""

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_connection() -> sqlite3.Connection:
    """Create a fresh SQLite connection configured for row-based access."""

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    """Convert a SQLite row into a JSON-friendly dictionary."""

    if row is None:
        return None

    return {key: row[key] for key in row.keys()}


def table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    """Return the set of columns that currently exist on a SQLite table."""

    cursor = connection.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}


def ensure_columns(
    connection: sqlite3.Connection,
    table_name: str,
    columns: Dict[str, str],
) -> None:
    """Add any missing columns to an existing table without dropping data."""

    existing_columns = table_columns(connection, table_name)
    for column_name, column_definition in columns.items():
        if column_name not in existing_columns:
            connection.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
            )


def generate_tracking_id() -> str:
    """Create a collision-safe tracking identifier for status lookups."""

    return f"TRK-{datetime.now(timezone.utc):%Y%m%d%H%M%S}-{uuid.uuid4().hex[:10].upper()}"


def _seed_dummy_dataset(connection: sqlite3.Connection) -> None:
    """Top up demo rows so local testing always has at least 10 examples."""

    timestamp = current_timestamp()

    demo_prescriptions = [
        {
            "prescription_id": "RX-DEMO-001",
            "tracking_id": "TRK-DEMO-001",
            "patient_id": "PAT-DEMO-001",
            "drug_name": "Amoxicillin",
            "dosage": "500mg",
            "prescribing_doctor": "Dr. Lee",
            "notes": "Take after meals",
            "status": "SUBMITTED",
            "decision": None,
            "confidence_score": None,
            "reasoning": None,
            "modification_description": None,
            "doctor_response_action": None,
            "doctor_response_description": None,
            "submitted_at": timestamp,
            "updated_at": timestamp,
            "orchestrator_decided_at": None,
            "doctor_responded_at": None,
        },
        {
            "prescription_id": "RX-DEMO-002",
            "tracking_id": "TRK-DEMO-002",
            "patient_id": "PAT-DEMO-002",
            "drug_name": "Metformin",
            "dosage": "850mg",
            "prescribing_doctor": "Dr. Patel",
            "notes": "Diabetes maintenance",
            "status": "NEEDS_REVIEW",
            "decision": "NEEDS_REVIEW",
            "confidence_score": 0.78,
            "reasoning": "Dose requires clinician review",
            "modification_description": None,
            "doctor_response_action": None,
            "doctor_response_description": None,
            "submitted_at": timestamp,
            "updated_at": timestamp,
            "orchestrator_decided_at": timestamp,
            "doctor_responded_at": None,
        },
        {
            "prescription_id": "RX-DEMO-003",
            "tracking_id": "TRK-DEMO-003",
            "patient_id": "PAT-DEMO-003",
            "drug_name": "Atorvastatin",
            "dosage": "20mg",
            "prescribing_doctor": "Dr. Brown",
            "notes": "Evening dose",
            "status": "APPROVED",
            "decision": "APPROVED",
            "confidence_score": 0.94,
            "reasoning": "Covered and clinically appropriate",
            "modification_description": None,
            "doctor_response_action": None,
            "doctor_response_description": None,
            "submitted_at": timestamp,
            "updated_at": timestamp,
            "orchestrator_decided_at": timestamp,
            "doctor_responded_at": None,
        },
        {
            "prescription_id": "RX-DEMO-004",
            "tracking_id": "TRK-DEMO-004",
            "patient_id": "PAT-DEMO-004",
            "drug_name": "Lisinopril",
            "dosage": "10mg",
            "prescribing_doctor": "Dr. Kim",
            "notes": "Blood pressure control",
            "status": "REJECTED",
            "decision": "REJECTED",
            "confidence_score": 0.66,
            "reasoning": "Plan restriction applies",
            "modification_description": None,
            "doctor_response_action": None,
            "doctor_response_description": None,
            "submitted_at": timestamp,
            "updated_at": timestamp,
            "orchestrator_decided_at": timestamp,
            "doctor_responded_at": None,
        },
        {
            "prescription_id": "RX-DEMO-005",
            "tracking_id": "TRK-DEMO-005",
            "patient_id": "PAT-DEMO-005",
            "drug_name": "Gabapentin",
            "dosage": "300mg",
            "prescribing_doctor": "Dr. Singh",
            "notes": "Neuropathic pain",
            "status": "MODIFIED",
            "decision": "NEEDS_REVIEW",
            "confidence_score": 0.73,
            "reasoning": "Requires dosage adjustment",
            "modification_description": "Reduce frequency to twice daily",
            "doctor_response_action": "modify",
            "doctor_response_description": "Reduce frequency to twice daily",
            "submitted_at": timestamp,
            "updated_at": timestamp,
            "orchestrator_decided_at": timestamp,
            "doctor_responded_at": timestamp,
        },
        {
            "prescription_id": "RX-DEMO-006",
            "tracking_id": "TRK-DEMO-006",
            "patient_id": "PAT-DEMO-006",
            "drug_name": "Sertraline",
            "dosage": "50mg",
            "prescribing_doctor": "Dr. Ahmed",
            "notes": "Daily morning dose",
            "status": "SUBMITTED",
            "decision": None,
            "confidence_score": None,
            "reasoning": None,
            "modification_description": None,
            "doctor_response_action": None,
            "doctor_response_description": None,
            "submitted_at": timestamp,
            "updated_at": timestamp,
            "orchestrator_decided_at": None,
            "doctor_responded_at": None,
        },
        {
            "prescription_id": "RX-DEMO-007",
            "tracking_id": "TRK-DEMO-007",
            "patient_id": "PAT-DEMO-007",
            "drug_name": "Omeprazole",
            "dosage": "40mg",
            "prescribing_doctor": "Dr. Garcia",
            "notes": "Before breakfast",
            "status": "APPROVED",
            "decision": "APPROVED",
            "confidence_score": 0.91,
            "reasoning": "Prior authorization not needed",
            "modification_description": None,
            "doctor_response_action": None,
            "doctor_response_description": None,
            "submitted_at": timestamp,
            "updated_at": timestamp,
            "orchestrator_decided_at": timestamp,
            "doctor_responded_at": None,
        },
        {
            "prescription_id": "RX-DEMO-008",
            "tracking_id": "TRK-DEMO-008",
            "patient_id": "PAT-DEMO-008",
            "drug_name": "Albuterol",
            "dosage": "2 puffs",
            "prescribing_doctor": "Dr. Nguyen",
            "notes": "As needed",
            "status": "NEEDS_REVIEW",
            "decision": "NEEDS_REVIEW",
            "confidence_score": 0.81,
            "reasoning": "Clarify inhaler frequency",
            "modification_description": None,
            "doctor_response_action": None,
            "doctor_response_description": None,
            "submitted_at": timestamp,
            "updated_at": timestamp,
            "orchestrator_decided_at": timestamp,
            "doctor_responded_at": None,
        },
        {
            "prescription_id": "RX-DEMO-009",
            "tracking_id": "TRK-DEMO-009",
            "patient_id": "PAT-DEMO-009",
            "drug_name": "Levothyroxine",
            "dosage": "75mcg",
            "prescribing_doctor": "Dr. Wilson",
            "notes": "Empty stomach",
            "status": "ACCEPTED",
            "decision": "APPROVED",
            "confidence_score": 0.97,
            "reasoning": "Accepted by doctor",
            "modification_description": None,
            "doctor_response_action": "accept",
            "doctor_response_description": None,
            "submitted_at": timestamp,
            "updated_at": timestamp,
            "orchestrator_decided_at": timestamp,
            "doctor_responded_at": timestamp,
        },
        {
            "prescription_id": "RX-DEMO-010",
            "tracking_id": "TRK-DEMO-010",
            "patient_id": "PAT-DEMO-010",
            "drug_name": "Hydrochlorothiazide",
            "dosage": "25mg",
            "prescribing_doctor": "Dr. Lopez",
            "notes": "Morning dose",
            "status": "SUBMITTED",
            "decision": None,
            "confidence_score": None,
            "reasoning": None,
            "modification_description": None,
            "doctor_response_action": None,
            "doctor_response_description": None,
            "submitted_at": timestamp,
            "updated_at": timestamp,
            "orchestrator_decided_at": None,
            "doctor_responded_at": None,
        },
    ]

    existing_prescriptions = {
        row["prescription_id"]
        for row in connection.execute("SELECT prescription_id FROM prescriptions").fetchall()
    }
    missing_prescriptions = [row for row in demo_prescriptions if row["prescription_id"] not in existing_prescriptions]

    if not missing_prescriptions:
        return

    if len(existing_prescriptions) >= 10:
        return

    connection.executemany(
        """
        INSERT INTO prescriptions (
            prescription_id,
            tracking_id,
            patient_id,
            drug_name,
            dosage,
            prescribing_doctor,
            doctor_id,
            notes,
            status,
            decision,
            confidence_score,
            reasoning,
            modification_description,
            doctor_response_action,
            doctor_response_description,
            submitted_at,
            updated_at,
            orchestrator_decided_at,
            doctor_responded_at
        )
        VALUES (:prescription_id, :tracking_id, :patient_id, :drug_name, :dosage, :prescribing_doctor, :prescribing_doctor, :notes, :status, :decision, :confidence_score, :reasoning, :modification_description, :doctor_response_action, :doctor_response_description, :submitted_at, :updated_at, :orchestrator_decided_at, :doctor_responded_at)
        """,
        missing_prescriptions,
    )

    connection.executemany(
        """
        INSERT INTO ai_recommendations (
            prescription_id,
            recommended_drug,
            policy_score,
            clinical_score,
            financial_score,
            final_ai_decision,
            ai_notes,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            ("RX-DEMO-001", "Generic Amoxicillin", 0.90, 0.88, 0.91, "APPROVE", "Low-risk and covered", timestamp),
            ("RX-DEMO-002", "Generic Metformin", 0.87, 0.90, 0.84, "REVIEW", "Dose needs clinician verification", timestamp),
            ("RX-DEMO-003", "Generic Atorvastatin", 0.95, 0.93, 0.89, "APPROVE", "Meets policy and clinical rules", timestamp),
            ("RX-DEMO-004", "Alternative ACE inhibitor", 0.55, 0.61, 0.57, "REJECT", "Formulary restriction", timestamp),
            ("RX-DEMO-005", "Generic Gabapentin", 0.76, 0.79, 0.74, "REVIEW", "Frequency adjustment required", timestamp),
            ("RX-DEMO-006", "Generic Sertraline", 0.88, 0.86, 0.85, "APPROVE", "Covered and clinically suitable", timestamp),
            ("RX-DEMO-007", "Generic Omeprazole", 0.92, 0.91, 0.90, "APPROVE", "Standard GI therapy", timestamp),
            ("RX-DEMO-008", "Rescue inhaler", 0.67, 0.72, 0.69, "REVIEW", "Clarify use instructions", timestamp),
            ("RX-DEMO-009", "Generic Levothyroxine", 0.97, 0.95, 0.94, "APPROVE", "High confidence approval", timestamp),
            ("RX-DEMO-010", "Generic Hydrochlorothiazide", 0.89, 0.87, 0.86, "APPROVE", "Routine maintenance medication", timestamp),
        ],
    )

    connection.executemany(
        """
        INSERT INTO reviewer_decisions (
            prescription_id,
            reviewer_action,
            reviewer_comments,
            reviewed_at
        )
        VALUES (?, ?, ?, ?)
        """,
        [
            ("RX-DEMO-001", "PENDING", "Awaiting pharmacist submission review", timestamp),
            ("RX-DEMO-002", "REVIEWED", "Needs manual review before approval", timestamp),
            ("RX-DEMO-003", "APPROVED", "Approved by PBM reviewer", timestamp),
            ("RX-DEMO-004", "REJECTED", "Plan exclusion applies", timestamp),
            ("RX-DEMO-005", "MODIFIED", "Dose adjusted before approval", timestamp),
            ("RX-DEMO-006", "PENDING", "Queued for intake processing", timestamp),
            ("RX-DEMO-007", "APPROVED", "Preferred therapy accepted", timestamp),
            ("RX-DEMO-008", "REVIEWED", "Need clarification from doctor", timestamp),
            ("RX-DEMO-009", "APPROVED", "Final approval recorded", timestamp),
            ("RX-DEMO-010", "PENDING", "New case waiting for processing", timestamp),
        ],
    )

    connection.executemany(
        """
        INSERT INTO audit_log (
            prescription_id,
            event_type,
            previous_status,
            new_status,
            details,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (row["prescription_id"], "seed", None, row["status"], f"Seeded demo state: {row['status']}", timestamp)
            for row in missing_prescriptions
        ],
    )

    connection.executemany(
        """
        INSERT INTO doctor_response_log (
            prescription_id,
            action,
            description,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        [
            ("RX-DEMO-005", "modify", "Reduce dose before dispensing", timestamp),
            ("RX-DEMO-009", "accept", None, timestamp),
        ] if {row["prescription_id"] for row in missing_prescriptions}.intersection({"RX-DEMO-005", "RX-DEMO-009"}) else [],
    )


def _upsert_missing_tracking_ids(connection: sqlite3.Connection) -> None:
    """Backfill tracking IDs for legacy prescription rows if they are missing."""

    cursor = connection.execute(
        """
        SELECT id, tracking_id
        FROM prescriptions
        WHERE tracking_id IS NULL OR tracking_id = ''
        """
    )
    rows = cursor.fetchall()

    for row in rows:
        tracking_id = generate_tracking_id()
        connection.execute(
            "UPDATE prescriptions SET tracking_id = ?, updated_at = ? WHERE id = ?",
            (tracking_id, current_timestamp(), row["id"]),
        )


def _sync_prescription_fields(connection: sqlite3.Connection) -> None:
    """Bring legacy prescription rows in line with the new workflow columns."""

    cursor = connection.execute(
        """
        SELECT id, doctor_id, prescribing_doctor, submitted_at, updated_at, status
        FROM prescriptions
        """
    )
    rows = cursor.fetchall()

    for row in rows:
        updates: Dict[str, Any] = {}
        doctor_id = row["doctor_id"] if "doctor_id" in row.keys() else None
        prescribing_doctor = row["prescribing_doctor"] if "prescribing_doctor" in row.keys() else None

        if not prescribing_doctor and doctor_id:
            updates["prescribing_doctor"] = doctor_id
        if not doctor_id and prescribing_doctor:
            updates["doctor_id"] = prescribing_doctor
        if not row["submitted_at"]:
            updates["submitted_at"] = current_timestamp()
        if not row["updated_at"]:
            updates["updated_at"] = current_timestamp()
        if not row["status"]:
            updates["status"] = "SUBMITTED"

        if updates:
            update_clause = ", ".join(f"{column} = ?" for column in updates)
            connection.execute(
                f"UPDATE prescriptions SET {update_clause} WHERE id = ?",
                (*updates.values(), row["id"]),
            )


def initialize_database() -> None:
    """Create the required tables and migrate any legacy rows in place."""

    connection = get_connection()
    try:
        connection.execute("PRAGMA foreign_keys = ON")

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id TEXT UNIQUE,
                tracking_id TEXT UNIQUE,
                patient_id TEXT,
                drug_name TEXT,
                dosage TEXT,
                prescribing_doctor TEXT,
                doctor_id TEXT,
                notes TEXT,
                status TEXT,
                decision TEXT,
                confidence_score REAL,
                reasoning TEXT,
                modification_description TEXT,
                doctor_response_action TEXT,
                doctor_response_description TEXT,
                submitted_at TEXT,
                updated_at TEXT,
                orchestrator_decided_at TEXT,
                doctor_responded_at TEXT
            )
            """
        )

        ensure_columns(
            connection,
            "prescriptions",
            {
                "tracking_id": "TEXT",
                "prescribing_doctor": "TEXT",
                "notes": "TEXT",
                "decision": "TEXT",
                "confidence_score": "REAL",
                "reasoning": "TEXT",
                "modification_description": "TEXT",
                "doctor_response_action": "TEXT",
                "doctor_response_description": "TEXT",
                "submitted_at": "TEXT",
                "updated_at": "TEXT",
                "orchestrator_decided_at": "TEXT",
                "doctor_responded_at": "TEXT",
            },
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id TEXT,
                event_type TEXT,
                previous_status TEXT,
                new_status TEXT,
                details TEXT,
                created_at TEXT
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS doctor_response_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id TEXT,
                action TEXT,
                description TEXT,
                created_at TEXT
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id TEXT,
                recommended_drug TEXT,
                policy_score REAL,
                clinical_score REAL,
                financial_score REAL,
                final_ai_decision TEXT,
                ai_notes TEXT,
                created_at TEXT
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reviewer_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_id TEXT,
                reviewer_action TEXT,
                reviewer_comments TEXT,
                reviewed_at TEXT
            )
            """
        )

        _upsert_missing_tracking_ids(connection)
        _sync_prescription_fields(connection)
        _seed_dummy_dataset(connection)

        connection.commit()
    finally:
        connection.close()


def fetch_prescription_by_tracking_id(tracking_id: str) -> Optional[Dict[str, Any]]:
    """Return a prescription record using the public tracking identifier."""

    connection = get_connection()
    try:
        cursor = connection.execute(
            "SELECT * FROM prescriptions WHERE tracking_id = ?",
            (tracking_id,),
        )
        return row_to_dict(cursor.fetchone())
    finally:
        connection.close()


def fetch_prescription_by_prescription_id(prescription_id: str) -> Optional[Dict[str, Any]]:
    """Return a prescription record using the internal prescription identifier."""

    connection = get_connection()
    try:
        cursor = connection.execute(
            "SELECT * FROM prescriptions WHERE prescription_id = ?",
            (prescription_id,),
        )
        return row_to_dict(cursor.fetchone())
    finally:
        connection.close()


def list_prescriptions_by_status(statuses: Iterable[str], limit: int = 100) -> List[Dict[str, Any]]:
    """List prescriptions whose status matches any of the provided values."""

    status_list = list(statuses)
    if not status_list:
        return []

    placeholders = ", ".join("?" for _ in status_list)
    connection = get_connection()
    try:
        cursor = connection.execute(
            f"SELECT * FROM prescriptions WHERE status IN ({placeholders}) ORDER BY updated_at DESC, id DESC LIMIT ?",
            (*status_list, limit),
        )
        return [row_to_dict(row) for row in cursor.fetchall() if row is not None]
    finally:
        connection.close()


def list_pending_prescriptions(limit: int = 100) -> List[Dict[str, Any]]:
    """Return prescriptions that still require pharmacist or doctor attention."""

    return list_prescriptions_by_status(
        ["SUBMITTED", "NEEDS_REVIEW", "UNDER_REVIEW"],
        limit=limit,
    )


def update_prescription_fields(
    prescription_id: str,
    fields: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Update a prescription row and return the refreshed record."""

    if not fields:
        return fetch_prescription_by_prescription_id(prescription_id)

    connection = get_connection()
    try:
        update_columns = ", ".join(f"{column} = ?" for column in fields)
        parameters = list(fields.values())
        parameters.extend([current_timestamp(), prescription_id])
        connection.execute(
            f"UPDATE prescriptions SET {update_columns}, updated_at = ? WHERE prescription_id = ?",
            parameters,
        )
        connection.commit()
    finally:
        connection.close()

    return fetch_prescription_by_prescription_id(prescription_id)


# Run the schema bootstrap when the module is imported so the API starts ready.
initialize_database()