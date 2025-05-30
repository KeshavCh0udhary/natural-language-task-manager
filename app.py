import streamlit as st
from datetime import datetime
from database import init_database, add_task, get_all_tasks, update_task, delete_task
from task_parser import parse_task, parse_transcript

# Page config
st.set_page_config(
    page_title="Natural Language Task Manager",
    page_icon="✅",
    layout="wide"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Task card */
    .task-card {
        background-color: #2b2b2b;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid;
    }
    
    /* Priority colors */
    .priority-P1 { border-left-color: #ff4444; background-color: rgba(255, 68, 68, 0.1); }
    .priority-P2 { border-left-color: #ffbb33; background-color: rgba(255, 187, 51, 0.1); }
    .priority-P3 { border-left-color: #00C851; background-color: rgba(0, 200, 81, 0.1); }
    .priority-P4 { border-left-color: #33b5e5; background-color: rgba(51, 181, 229, 0.1); }
    
    /* Task elements */
    .task-title {
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    
    .task-meta {
        font-size: 0.9rem;
        color: #aaa;
        margin-bottom: 0.5rem;
    }
    
    .task-assignee {
        display: inline-flex;
        align-items: center;
        background-color: rgba(255, 255, 255, 0.1);
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
if 'db_initialized' not in st.session_state:
    init_database()
    st.session_state.db_initialized = True

# Title
st.title("✅ Natural Language Task Manager")

# Input sections
st.markdown("### Add Tasks")

# Create tabs for different input methods
tab1, tab2 = st.tabs(["Single Tasks", "Transcript"])

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        task_input = st.text_area(
            "Enter your tasks (one per line):",
            placeholder="Call client Rajeev tomorrow 5pm\nFinish landing page Aman by 11pm 20th June\netc.",
            help="Enter one task per line. Use natural language to describe what needs to be done.",
            height=100
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        add_task_button = st.button("Add Tasks", type="primary", use_container_width=True)

    # Process new tasks
    if add_task_button and task_input:
        tasks_to_add = [task.strip() for task in task_input.split('\n') if task.strip()]
        
        with st.spinner('Processing tasks...'):
            for task_text in tasks_to_add:
                parsed_task = parse_task(task_text)
                if parsed_task:
                    try:
                        result = add_task(
                            parsed_task['task_name'],
                            parsed_task['assignee'],
                            parsed_task['due_date'],
                            parsed_task['priority']
                        )
                        if result:
                            st.success(f"Added task: {parsed_task['task_name']}")
                    except Exception as e:
                        st.error(f"Error adding task: {str(e)}")
                else:
                    st.warning(f"Could not parse task: {task_text}")

with tab2:
    col1, col2 = st.columns([3, 1])
    with col1:
        transcript_input = st.text_area(
            "Enter your transcript:",
            placeholder="Aman you take the landing page by 10pm tomorrow. Rajeev you take care of client follow-up by Wednesday...",
            help="Enter a transcript containing multiple tasks. The system will automatically parse and extract individual tasks.",
            height=150
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        add_transcript_button = st.button("Process Transcript", type="primary", use_container_width=True)

    # Process transcript
    if add_transcript_button and transcript_input:
        with st.spinner('Processing transcript...'):
            parsed_tasks = parse_transcript(transcript_input)
            if parsed_tasks:
                for task in parsed_tasks:
                    try:
                        result = add_task(
                            task['task_name'],
                            task['assignee'],
                            task['due_date'],
                            task['priority']
                        )
                        if result:
                            st.success(f"Added task: {task['task_name']}")
                    except Exception as e:
                        st.error(f"Error adding task: {str(e)}")
            else:
                st.warning("Could not parse any tasks from the transcript")

# Display tasks
st.markdown("### Task Board")

try:
    tasks = get_all_tasks()
    if tasks:
        # Create columns for different priority levels
        cols = st.columns(4)
        priority_tasks = {'P1': [], 'P2': [], 'P3': [], 'P4': []}
        
        # Group tasks by priority
        for task in tasks:
            priority_tasks[task['priority']].append(task)
        
        # Display tasks in columns
        for i, (priority, tasks_list) in enumerate(priority_tasks.items()):
            with cols[i]:
                st.markdown(f"#### {priority}")
                if not tasks_list:
                    st.markdown("No tasks")
                    continue
                    
                for task in tasks_list:
                    with st.container():
                        # Display task card
                        st.markdown(f"""
                        <div class="task-card priority-{task['priority']}">
                            <div class="task-title">{task['task_name']}</div>
                            <div class="task-meta">
                                <div class="task-assignee">👤 {task['assignee']}</div>
                                <div>🕒 {task['due_date'].strftime('%I:%M %p, %d %B')}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Task actions
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button("✏️", key=f"edit_{task['id']}", help="Edit task"):
                                st.session_state[f"editing_{task['id']}"] = True
                        with col2:
                            if st.button("🗑️", key=f"delete_{task['id']}", help="Delete task"):
                                delete_task(task['id'])
                                st.rerun()
                        
                        # Edit form
                        if st.session_state.get(f"editing_{task['id']}", False):
                            with st.form(key=f"edit_form_{task['id']}"):
                                new_task_name = st.text_input("Task Name", task['task_name'])
                                new_assignee = st.text_input("Assignee", task['assignee'])
                                
                                date_col, time_col = st.columns(2)
                                with date_col:
                                    new_date = st.date_input("Due Date", task['due_date'].date())
                                with time_col:
                                    new_time = st.time_input("Due Time", task['due_date'].time())
                                
                                new_due_date = datetime.combine(new_date, new_time)
                                new_priority = st.selectbox(
                                    "Priority",
                                    ['P1', 'P2', 'P3', 'P4'],
                                    index=['P1', 'P2', 'P3', 'P4'].index(task['priority'])
                                )
                                
                                if st.form_submit_button("Save Changes"):
                                    update_task(task['id'], new_task_name, new_assignee, new_due_date, new_priority)
                                    del st.session_state[f"editing_{task['id']}"]
                                    st.rerun()
    else:
        st.info("No tasks yet. Add your first task above!")
except Exception as e:
    st.error(f"Error loading tasks: {str(e)}") 