import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# Initialize Supabase client
supabase: Client = create_client(
    "https://wcvfghkffyktywzemkhp.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndjdmZnaGtmZnlrdHl3emVta2hwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg1MTAwMzcsImV4cCI6MjA2NDA4NjAzN30.Y5W3tF5lOx0X_VHa_EDFvY1bpaygsH3XOcHK3_w5DYg"
)

def init_database():
    """Initialize the database by creating the tasks table if it doesn't exist."""
    try:
        # Create tasks table if it doesn't exist
        supabase.table('tasks').select('*').limit(1).execute()
    except Exception as e:
        st.error(f"Error initializing database: {str(e)}")

def add_task(task_name, assignee, due_date, priority='P3'):
    """Add a new task to the database."""
    try:
        # Check for duplicate task
        response = supabase.table('tasks').select('id').eq('title', task_name).eq('assignee', assignee).eq('due_date', due_date.isoformat()).eq('priority', priority).execute()
        
        if response.data:
            st.warning(f"Task already exists: {task_name}")
            return False
            
        # Insert new task
        response = supabase.table('tasks').insert({
            'title': task_name,
            'assignee': assignee,
            'due_date': due_date.isoformat(),
            'priority': priority
        }).execute()
        
        return response.data[0]['id']
        
    except Exception as e:
        raise e

def get_all_tasks():
    """Get all tasks ordered by due date."""
    try:
        response = supabase.table('tasks').select('*').order('due_date').execute()
        
        tasks = []
        for row in response.data:
            tasks.append({
                'id': row['id'],
                'task_name': row['title'],
                'assignee': row['assignee'],
                'due_date': datetime.fromisoformat(row['due_date']),
                'priority': row['priority']
            })
        
        return tasks
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return []

def update_task(task_id, task_name, assignee, due_date, priority):
    """Update an existing task."""
    try:
        supabase.table('tasks').update({
            'title': task_name,
            'assignee': assignee,
            'due_date': due_date.isoformat(),
            'priority': priority
        }).eq('id', task_id).execute()
    except Exception as e:
        raise e

def delete_task(task_id):
    """Delete a task by its ID."""
    try:
        supabase.table('tasks').delete().eq('id', task_id).execute()
    except Exception as e:
        raise e 