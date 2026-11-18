"""
Persistent Incident & Agent Reputation Ledger.
Embedded SQLite audit trail and agent trust score engine.
Zero external dependencies. Pure standard library.
"""

import os
import sqlite3
import time
from typing import List, Dict, Any, Optional

DEFAULT_DB_DIR = os.path.expanduser("~/.aegis")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "ledger.db")


def _get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Get or create SQLite connection with schema initialized."""
    target_path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row

    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                agent_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                target TEXT,
                details TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                agent_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_incidents ON incidents(agent_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_actions ON agent_actions(agent_id)")

    return conn


def record_incident(
    agent_id: str,
    event_type: str,
    severity: str,
    risk_score: int,
    target: str = "",
    details: str = "",
    db_path: Optional[str] = None
) -> int:
    """Record a security violation or risk event to the ledger."""
    conn = _get_connection(db_path)
    now = time.time()
    with conn:
        cursor = conn.execute("""
            INSERT INTO incidents (timestamp, agent_id, event_type, severity, risk_score, target, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (now, agent_id or "unknown_agent", event_type, severity, risk_score, target, details))
        incident_id = cursor.lastrowid

        # Also record in agent_actions
        conn.execute("""
            INSERT INTO agent_actions (timestamp, agent_id, action_type, status)
            VALUES (?, ?, ?, ?)
        """, (now, agent_id or "unknown_agent", event_type, "BLOCKED" if severity == "CRITICAL" else "FLAGGED"))

    conn.close()
    return incident_id


def record_action(
    agent_id: str,
    action_type: str,
    status: str = "CLEAN",
    db_path: Optional[str] = None
) -> int:
    """Record an audited agent action (CLEAN, FLAGGED, or BLOCKED)."""
    conn = _get_connection(db_path)
    now = time.time()
    with conn:
        cursor = conn.execute("""
            INSERT INTO agent_actions (timestamp, agent_id, action_type, status)
            VALUES (?, ?, ?, ?)
        """, (now, agent_id or "unknown_agent", action_type, status))
        action_id = cursor.lastrowid
    conn.close()
    return action_id


def get_agent_reputation(agent_id: Optional[str] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate reputation and trust score (0 to 100) for a given agent or all agents.
    Trust score starts at 100 and scales down based on critical and high-severity violations.
    """
    conn = _get_connection(db_path)
    query_actions = "SELECT COUNT(*) as total FROM agent_actions"
    params_actions = ()
    query_incidents = "SELECT severity, COUNT(*) as cnt FROM incidents"
    params_incidents = ()

    if agent_id:
        query_actions += " WHERE agent_id = ?"
        params_actions = (agent_id,)
        query_incidents += " WHERE agent_id = ? GROUP BY severity"
        params_incidents = (agent_id,)
    else:
        query_incidents += " GROUP BY severity"

    total_actions = conn.execute(query_actions, params_actions).fetchone()["total"]
    incidents = conn.execute(query_incidents, params_incidents).fetchall()

    crit_count = 0
    high_count = 0
    med_count = 0
    low_count = 0

    for row in incidents:
        sev = row["severity"]
        cnt = row["cnt"]
        if sev == "CRITICAL":
            crit_count += cnt
        elif sev == "HIGH":
            high_count += cnt
        elif sev == "MEDIUM":
            med_count += cnt
        else:
            low_count += cnt

    total_violations = crit_count + high_count + med_count + low_count

    # Trust Score Formula: 100 - (crit * 25 + high * 10 + med * 4 + low * 1)
    deduction = (crit_count * 25) + (high_count * 10) + (med_count * 4) + (low_count * 1)
    trust_score = max(0, min(100, 100 - deduction))

    conn.close()
    return {
        "agent_id": agent_id or "ALL",
        "trust_score": trust_score,
        "total_actions": total_actions,
        "clean_actions": max(0, total_actions - total_violations),
        "total_violations": total_violations,
        "breakdown": {
            "CRITICAL": crit_count,
            "HIGH": high_count,
            "MEDIUM": med_count,
            "LOW": low_count
        }
    }


def get_recent_incidents(limit: int = 20, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve recent security incidents from the ledger."""
    conn = _get_connection(db_path)
    rows = conn.execute("""
        SELECT id, timestamp, agent_id, event_type, severity, risk_score, target, details
        FROM incidents
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()

    res = [
        {
            "id": r["id"],
            "timestamp": r["timestamp"],
            "agent_id": r["agent_id"],
            "event_type": r["event_type"],
            "severity": r["severity"],
            "risk_score": r["risk_score"],
            "target": r["target"],
            "details": r["details"]
        }
        for r in rows
    ]
    conn.close()
    return res
