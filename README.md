# Natural Language Task Manager

A modern task management application that understands natural language input, built with Streamlit and powered by OpenAI's GPT-3.5.

## Features

- 📝 Natural language task input
- 🎯 Automatic task parsing (name, assignee, due date, priority)
- 📊 Priority-based task organization (P1-P4)
- 🗂️ Clean and intuitive task board interface
- ⚡ Real-time updates and editing
- 🔄 Persistent storage with Supabase
- 📋 Transcript parser for handling multiple tasks in a single text

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### 1. Clone the Repository

```bash
git clone <repository-url>
cd natural-language-task-manager
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.streamlit/secrets.toml` file in your project directory:

```toml
OPENAI_API_KEY = "your-openai-api-key"
```

Replace the placeholder with your OpenAI API key.

### 4. Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Usage

### Single Task Input
Enter tasks in natural language format:
- "Call client Rajeev tomorrow 5pm"
- "Finish landing page Aman by 11pm 20th June"
- "Submit report to Sarah by Friday 3pm P1"

### Transcript Input
Paste a transcript containing multiple tasks:
```
Aman you take the landing page by 10pm tomorrow. 
Rajeev you take care of client follow-up by Wednesday. 
Shreya please review the marketing deck tonight p1. 
Keshav call me today at 5pm.
```

### Supported Time Expressions
The application understands various time expressions:
- Absolute times: "5pm", "15:00", "3:30 PM"
- Relative times: "tomorrow", "next week", "today"
- End of day: "end of day", "eod" (defaults to 5:00 PM)
- Evening: "tonight" (defaults to 8:00 PM)
- Specific dates: "20th June", "Friday", "next Monday"

### Priority Levels
Tasks are automatically organized by priority:
- P1: Highest priority (Urgent)
- P2: High priority
- P3: Medium priority (Default)
- P4: Low priority

### Task Management
Each task can be:
- Edited: Change task details, due date, or priority
- Deleted: Remove tasks from the board

## Project Structure

```
natural-language-task-manager/
├── app.py              # Main Streamlit application
├── database.py         # Database operations using Supabase
├── task_parser.py      # Natural language parsing
├── requirements.txt    # Project dependencies
└── .streamlit/
    └── secrets.toml    # Configuration secrets
```

## Dependencies

- streamlit
- openai
- supabase-py
- python-dateutil
- python-dotenv