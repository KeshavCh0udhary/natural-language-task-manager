from datetime import datetime, timedelta
from dateutil import parser
import re
from openai import OpenAI
import streamlit as st
import json

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def parse_task(text):
    """Parse a natural language task into structured data using OpenAI."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": """Parse the task and return a JSON response with these components:
                {
                    "task_name": "the main task description",
                    "assignee": "the person assigned to the task",
                    "due_date": "the due date and time",
                    "priority": "P1, P2, P3, or P4 (default to P3 if not specified)"
                }

                Example inputs and expected extractions:
                1. "Finish landing page Aman by 11pm 20th June"
                   - task_name: "Finish landing page"
                   - assignee: "Aman"
                   - due_date: "11pm 20th June"
                
                2. "Call client Rajeev tomorrow 5pm"
                   - task_name: "Call client"
                   - assignee: "Rajeev"
                   - due_date: "tomorrow 5pm"

                Rules:
                - Extract task name without the assignee and time information
                - Keep date/time in original format
                - Default to P3 if priority not specified
                - Look for assignee near words like 'to', 'by', 'for', or at the end of task name"""},
                {"role": "user", "content": text}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        parsed_data = json.loads(response.choices[0].message.content)
        
        # Convert the date string to datetime object
        if parsed_data.get('due_date'):
            try:
                date_text = parsed_data['due_date'].lower()
                current_time = datetime.now()
                
                if 'tomorrow' in date_text:
                    base_date = current_time + timedelta(days=1)
                elif 'next week' in date_text:
                    base_date = current_time + timedelta(weeks=1)
                else:
                    base_date = parser.parse(date_text, fuzzy=True)
                
                # Extract time if specified (e.g., "3pm", "15:00")
                time_pattern = r'(\d{1,2})(?::(\d{1,2}))?\s*(am|pm|AM|PM)?'
                time_match = re.search(time_pattern, date_text)
                
                if time_match:
                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2)) if time_match.group(2) else 0
                    period = time_match.group(3)
                    
                    if period and period.lower() == 'pm' and hour != 12:
                        hour += 12
                    elif period and period.lower() == 'am' and hour == 12:
                        hour = 0
                    
                    parsed_data['due_date'] = base_date.replace(
                        hour=hour,
                        minute=minute,
                        second=0,
                        microsecond=0
                    )
                else:
                    # Default to 9 AM if no time specified
                    parsed_data['due_date'] = base_date.replace(
                        hour=9,
                        minute=0,
                        second=0,
                        microsecond=0
                    )
            except Exception as e:
                st.error(f"Could not parse date: {parsed_data['due_date']} - {str(e)}")
                return None
        
        # Ensure priority is valid
        if 'priority' in parsed_data:
            priority = parsed_data['priority'].upper()
            if priority not in ['P1', 'P2', 'P3', 'P4']:
                priority = 'P3'
            parsed_data['priority'] = priority
        else:
            parsed_data['priority'] = 'P3'
            
        # Clean up and validate
        task_name = parsed_data.get('task_name', '').strip()
        assignee = parsed_data.get('assignee', '').strip()
        
        if not task_name or not assignee or not parsed_data.get('due_date'):
            return None
            
        return {
            'task_name': task_name,
            'assignee': assignee,
            'due_date': parsed_data['due_date'],
            'priority': parsed_data['priority']
        }
    except Exception as e:
        st.error(f"Error parsing task: {str(e)}")
        return None