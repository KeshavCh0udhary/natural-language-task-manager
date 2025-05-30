import psycopg2
import streamlit as st
from datetime import datetime

def get_database_connection():
    """Get a connection to the database using the configured URL."""
    return psycopg2.connect("postgresql://postgres:%40Password9%23@db.wcvfghkffyktywzemkhp.supabase.co:5432/postgres")

def init_database():
    """Initialize the database by creating the tasks table if it doesn't exist."""
    conn = get_database_connection()
    cur = conn.cursor()
    
    try:
        # Create tasks table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                assignee TEXT NOT NULL,
                due_date TIMESTAMP NOT NULL,
                priority TEXT NOT NULL DEFAULT 'P3',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        st.error(f"Error initializing database: {str(e)}")
    finally:
        cur.close()
        conn.close()

def add_task(task_name, assignee, due_date, priority='P3'):
    """Add a new task to the database."""
    conn = get_database_connection()
    cur = conn.cursor()
    
    try:
        # Check for duplicate task
        cur.execute("""
            SELECT id FROM tasks 
            WHERE title = %s 
            AND assignee = %s 
            AND due_date = %s 
            AND priority = %s
        """, (task_name, assignee, due_date, priority))
        
        if cur.fetchone():
            st.warning(f"Task already exists: {task_name}")
            return False
            
        # Insert new task
        cur.execute("""
            INSERT INTO tasks (title, assignee, due_date, priority)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (task_name, assignee, due_date, priority))
        
        task_id = cur.fetchone()[0]
        conn.commit()
        return task_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_all_tasks():
    """Get all tasks ordered by due date."""
    conn = get_database_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT 
                id,
                title as task_name,
                assignee,
                due_date,
                priority
            FROM tasks
            ORDER BY due_date ASC
        """)
        
        tasks = []
        for row in cur.fetchall():
            tasks.append({
                'id': row[0],
                'task_name': row[1],
                'assignee': row[2],
                'due_date': row[3],
                'priority': row[4]
            })
        
        return tasks
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return []
    finally:
        cur.close()
        conn.close()

def update_task(task_id, task_name, assignee, due_date, priority):
    """Update an existing task."""
    conn = get_database_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE tasks
            SET title = %s,
                assignee = %s,
                due_date = %s,
                priority = %s
            WHERE id = %s
        """, (task_name, assignee, due_date, priority, task_id))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def delete_task(task_id):
    """Delete a task by its ID."""
    conn = get_database_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close() 