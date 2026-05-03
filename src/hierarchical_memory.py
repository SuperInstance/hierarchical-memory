#!/usr/bin/env python3
"""
hierarchical-memory v1.0.0 — CCC Reference Implementation
3-tier agent memory: Working → Short-Term → Long-Term
"""

import sqlite3, json, hashlib, time, os
from typing import Optional, List, Dict

class HierarchicalMemory:
    def __init__(self, path: str = "memory.db"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS working (
                key TEXT PRIMARY KEY,
                value TEXT,
                created REAL DEFAULT (unixepoch())
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS short_term (
                id INTEGER PRIMARY KEY,
                query TEXT,
                response TEXT,
                session_id TEXT,
                embedding TEXT,
                created REAL DEFAULT (unixepoch())
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS long_term (
                id INTEGER PRIMARY KEY,
                category TEXT,
                content TEXT,
                importance REAL DEFAULT 0.5,
                created REAL DEFAULT (unixepoch())
            )
        """)
        self.conn.commit()
    
    # Working Memory: Key-value, ephemeral
    def working_set(self, key: str, value: str):
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO working (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()
    
    def working_get(self, key: str) -> Optional[str]:
        c = self.conn.cursor()
        row = c.execute("SELECT value FROM working WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None
    
    def working_clear(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM working")
        self.conn.commit()
    
    # Short-Term Memory: Session history with simple similarity
    def short_term_store(self, query: str, response: str, session_id: str = "default"):
        c = self.conn.cursor()
        emb = self._simple_embed(query)
        c.execute(
            "INSERT INTO short_term (query, response, session_id, embedding) VALUES (?, ?, ?, ?)",
            (query, response, session_id, json.dumps(emb))
        )
        self.conn.commit()
    
    def short_term_recall(self, query: str, k: int = 3) -> List[Dict]:
        c = self.conn.cursor()
        qemb = self._simple_embed(query)
        rows = c.execute("SELECT query, response, embedding FROM short_term ORDER BY id DESC LIMIT 100").fetchall()
        scored = []
        for row in rows:
            emb = json.loads(row["embedding"])
            sim = sum(a*b for a,b in zip(qemb, emb)) / (sum(a*a for a in qemb)**.5 * sum(b*b for b in emb)**.5 + 1e-9)
            scored.append((sim, row["query"], row["response"]))
        scored.sort(reverse=True)
        return [{"query": q, "response": r, "similarity": round(s, 3)} for s, q, r in scored[:k]]
    
    def _simple_embed(self, text: str) -> List[float]:
        """Simple character-ngram embedding. Not SOTA but zero-deps."""
        text = text.lower()
        grams = [text[i:i+3] for i in range(len(text)-2)]
        vocab = sorted(set(grams))
        vec = [grams.count(g) for g in vocab[:64]]
        while len(vec) < 64: vec.append(0)
        mag = sum(x*x for x in vec)**.5 or 1
        return [x/mag for x in vec]
    
    # Long-Term Memory: Consolidated knowledge
    def long_term_store(self, category: str, content: str, importance: float = 0.5):
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO long_term (category, content, importance) VALUES (?, ?, ?)",
            (category, content, importance)
        )
        self.conn.commit()
    
    def long_term_recall(self, category: str = None, min_importance: float = 0.0) -> List[Dict]:
        c = self.conn.cursor()
        if category:
            rows = c.execute(
                "SELECT category, content, importance, created FROM long_term WHERE category = ? AND importance >= ? ORDER BY importance DESC",
                (category, min_importance)
            ).fetchall()
        else:
            rows = c.execute(
                "SELECT category, content, importance, created FROM long_term WHERE importance >= ? ORDER BY importance DESC",
                (min_importance,)
            ).fetchall()
        return [{"category": r["category"], "content": r["content"], "importance": r["importance"], "created": r["created"]} for r in rows]
    
    def consolidate(self, session_id: str = None):
        """Move important short-term memories to long-term."""
        c = self.conn.cursor()
        if session_id:
            rows = c.execute("SELECT query, response FROM short_term WHERE session_id = ?", (session_id,)).fetchall()
        else:
            rows = c.execute("SELECT query, response FROM short_term").fetchall()
        for row in rows:
            content = f"Q: {row['query']}\nA: {row['response']}"
            self.long_term_store("consolidated_session", content, importance=0.6)
        c.execute("DELETE FROM short_term WHERE session_id = ?" if session_id else "DELETE FROM short_term", (session_id,) if session_id else ())
        self.conn.commit()
    
    def stats(self) -> Dict:
        c = self.conn.cursor()
        w = c.execute("SELECT COUNT(*) FROM working").fetchone()[0]
        s = c.execute("SELECT COUNT(*) FROM short_term").fetchone()[0]
        l = c.execute("SELECT COUNT(*) FROM long_term").fetchone()[0]
        return {"working": w, "short_term": s, "long_term": l}


def demo():
    mem = HierarchicalMemory(":memory:")
    
    # Working memory
    mem.working_set("current_task", "fleet audit 2026-05-04")
    mem.working_set("plato_url", "http://147.224.38.131:8847")
    print("Working:", mem.working_get("current_task"))
    
    # Short-term memory
    mem.short_term_store("What is PLATO?", "A shared knowledge lattice for agent fleets.", "session-1")
    mem.short_term_store("What is a tile?", "A unit of knowledge with question, answer, confidence.", "session-1")
    mem.short_term_store("How to submit tiles?", "POST to /submit with question, answer, agent, room.", "session-1")
    
    recall = mem.short_term_recall("how do I submit knowledge?", k=2)
    print("\nShort-term recall:")
    for r in recall:
        print(f"  sim={r['similarity']} | {r['query']}")
    
    # Consolidate
    mem.consolidate("session-1")
    print("\nAfter consolidation:", mem.stats())
    
    # Long-term memory
    mem.long_term_store("fleet_architecture", "The fleet has 4 vessels: Oracle1, FM, JC1, CCC.", 0.9)
    mem.long_term_store("plato_gate", "PLATO Gate accepts tiles at port 8847.", 0.8)
    
    lt = mem.long_term_recall(min_importance=0.8)
    print("\nLong-term (importance >= 0.8):")
    for item in lt:
        print(f"  [{item['category']}] {item['content'][:60]}...")
    
    print("\nFinal stats:", mem.stats())

if __name__ == "__main__":
    demo()
