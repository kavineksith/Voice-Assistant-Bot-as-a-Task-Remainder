import sqlite3
import sys
import speech_recognition as sr
import pyttsx3
import datetime
import re
import time

# Custom Exceptions
class VoiceAssistantError(Exception):
    """Base class for other exceptions"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class TaskNotFoundError(VoiceAssistantError):
    """Raised when a task is not found"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DatabaseError(VoiceAssistantError):
    """Raised when there is an error with the database"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Database Class
class Database:
    def __init__(self, db_name='todo.db'):
        try:
            self.db_name = db_name
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.create_table()
        except sqlite3.Error as e:
            raise DatabaseError(f"Database error: {e}")
    
    def create_table(self):
        try:
            query = '''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                task TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('pending', 'completed')),
                due_date TEXT,
                priority TEXT CHECK(priority IN ('low', 'medium', 'high')),
                reminder_set INTEGER DEFAULT 0
            )
            '''
            self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Error creating table: {e}")
    
    def insert_task(self, task, due_date, priority):
        try:
            query = 'INSERT INTO tasks (task, status, due_date, priority) VALUES (?, ?, ?, ?)'
            self.cursor.execute(query, (task, 'pending', due_date, priority))
            self.conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Error inserting task: {e}")
    
    def update_task(self, task_id, status):
        try:
            query = 'UPDATE tasks SET status = ? WHERE id = ?'
            self.cursor.execute(query, (status, task_id))
            self.conn.commit()
            if self.cursor.rowcount == 0:
                raise TaskNotFoundError(f"Task ID {task_id} not found.")
        except sqlite3.Error as e:
            raise DatabaseError(f"Error updating task: {e}")
    
    def delete_task(self, task_id):
        try:
            query = 'DELETE FROM tasks WHERE id = ?'
            self.cursor.execute(query, (task_id,))
            self.conn.commit()
            if self.cursor.rowcount == 0:
                raise TaskNotFoundError(f"Task ID {task_id} not found.")
        except sqlite3.Error as e:
            raise DatabaseError(f"Error deleting task: {e}")
    
    def search_tasks(self, keyword):
        try:
            query = 'SELECT * FROM tasks WHERE task LIKE ?'
            self.cursor.execute(query, ('%' + keyword + '%',))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise DatabaseError(f"Error searching tasks: {e}")
    
    def view_tasks(self):
        try:
            query = 'SELECT * FROM tasks'
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise DatabaseError(f"Error viewing tasks: {e}")
    
    def __del__(self):
        try:
            self.conn.close()
        except sqlite3.Error as e:
            raise DatabaseError(f"Error closing database connection: {e}")

# Voice Assistant Class
class VoiceAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.db = Database()
    
    def speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.speak("Error with text-to-speech.")
            print(f"Text-to-Speech error: {e}")
    
    def listen(self):
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.recognizer.listen(source)
                command = self.recognizer.recognize_google(audio) # type: ignore
                print(f"You said: {command}")
                return command.lower()
        except sr.UnknownValueError:
            self.speak("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            self.speak("Sorry, there is an issue with the speech service.")
            return None
        except Exception as e:
            self.speak("An unexpected error occurred while listening.")
            print(f"Listening error: {e}")
            return None
    
    def execute_command(self, command):
        try:
            if re.search(r'\b(add|create)\b.*\b(task|to-do)\b', command):
                self.add_task(command)
            elif re.search(r'\b(update|mark)\b.*\b(task)\b', command):
                self.update_task(command)
            elif re.search(r'\b(delete|remove)\b.*\b(task)\b', command):
                self.delete_task(command)
            elif re.search(r'\b(search)\b.*\b(task)\b', command):
                self.search_task(command)
            elif re.search(r'\b(view)\b.*\b(tasks)\b', command):
                self.view_tasks()
            elif re.search(r'\b(reminder)\b', command):
                self.set_reminder(command)
            else:
                self.speak("Sorry, I did not understand that command.")
        except Exception as e:
            self.speak("An unexpected error occurred while executing the command.")
            print(f"Command execution error: {e}")
    
    def add_task(self, command):
        try:
            match = re.search(r'\b(task|to-do)\b: (.*)\s+due\s+by\s+(\d{4}-\d{2}-\d{2})\s+priority\s+(low|medium|high)', command)
            if match:
                task = match.group(2)
                due_date = match.group(3)
                priority = match.group(4)
                self.db.insert_task(task, due_date, priority)
                self.speak(f"Task '{task}' added with due date {due_date} and priority {priority}.")
            else:
                self.speak("Please specify the task, due date in YYYY-MM-DD format, and priority (low, medium, high).")
        except Exception as e:
            self.speak("An error occurred while adding the task.")
            print(f"Add task error: {e}")
    
    def update_task(self, command):
        try:
            match = re.search(r'\b(task)\b\s+(\d+)\s+(completed|pending)', command)
            if match:
                task_id = int(match.group(2))
                status = match.group(3)
                self.db.update_task(task_id, status)
                self.speak(f"Task ID {task_id} marked as {status}.")
            else:
                self.speak("Please specify the task ID and status to update.")
        except TaskNotFoundError as e:
            self.speak(str(e))
        except Exception as e:
            self.speak("An error occurred while updating the task.")
            print(f"Update task error: {e}")
    
    def delete_task(self, command):
        try:
            match = re.search(r'\b(task)\b\s+(\d+)', command)
            if match:
                task_id = int(match.group(2))
                self.db.delete_task(task_id)
                self.speak(f"Task ID {task_id} deleted.")
            else:
                self.speak("Please specify the task ID to delete.")
        except TaskNotFoundError as e:
            self.speak(str(e))
        except Exception as e:
            self.speak("An error occurred while deleting the task.")
            print(f"Delete task error: {e}")
    
    def search_task(self, command):
        try:
            match = re.search(r'\b(task|to-do)\b: (.*)', command)
            if match:
                keyword = match.group(2)
                tasks = self.db.search_tasks(keyword)
                if tasks:
                    response = "Tasks found: " + ', '.join([f"ID {t[0]}: {t[1]} ({t[2]}) due by {t[3]} priority {t[4]}" for t in tasks])
                else:
                    response = "No tasks found."
                self.speak(response)
            else:
                self.speak("Please specify a keyword to search for tasks.")
        except Exception as e:
            self.speak("An error occurred while searching for tasks.")
            print(f"Search task error: {e}")
    
    def view_tasks(self):
        try:
            tasks = self.db.view_tasks()
            if tasks:
                response = "Tasks: " + ', '.join([f"ID {t[0]}: {t[1]} ({t[2]}) due by {t[3]} priority {t[4]}" for t in tasks])
            else:
                response = "No tasks available."
            self.speak(response)
        except Exception as e:
            self.speak("An error occurred while viewing tasks.")
            print(f"View tasks error: {e}")
    
    def set_reminder(self, command):
        try:
            # Extract reminder details from the command
            match = re.search(r'\b(reminder)\b\s+for\s+(.*)\s+at\s+(\d{2}:\d{2})', command)
            if match:
                reminder_text = match.group(2)
                reminder_time = match.group(3)
                
                # Validate time format
                try:
                    reminder_time = datetime.datetime.strptime(reminder_time, "%H:%M").time()
                except ValueError:
                    self.speak("Invalid time format. Please use HH:MM.")
                    return
                
                # Store the reminder in a file
                with open('reminders.txt', 'a') as file:
                    file.write(f"Reminder: {reminder_text} at {reminder_time}\n")
                
                self.speak(f"Reminder set for {reminder_text} at {reminder_time}.")
            else:
                self.speak("Please specify the reminder text and time in the format 'reminder for <text> at HH:MM'.")
        except Exception as e:
            self.speak("An error occurred while setting the reminder.")
            print(f"Set reminder error: {e}")

    def check_reminders(self):
        try:
            current_time = datetime.datetime.now()
            tasks = self.db.view_tasks()
            for task in tasks:
                task_id, task_text, status, due_date, priority, reminder_set = task
                if status == 'pending':
                    due_datetime = datetime.datetime.strptime(due_date, "%Y-%m-%d")
                    if priority == 'low':
                        self.check_low_priority_reminders(current_time, task_id, due_datetime)
                    elif priority == 'medium':
                        self.check_medium_priority_reminders(current_time, task_id, due_datetime)
                    elif priority == 'high':
                        self.check_high_priority_reminders(current_time, task_id, due_datetime)
        except Exception as e:
            self.speak("An error occurred while checking reminders.")
            print(f"Check reminders error: {e}")

    def check_low_priority_reminders(self, current_time, task_id, due_date):
        due_datetime = datetime.datetime.combine(due_date, datetime.time(0))
        time_remaining = due_datetime - current_time
        reminder_intervals = [datetime.timedelta(hours=5), datetime.timedelta(hours=1), datetime.timedelta(minutes=30), datetime.timedelta(minutes=5)]
        for interval in reminder_intervals:
            if time_remaining <= interval:
                self.speak(f"Reminder: Task ID {task_id} is due soon.")
                break

    def check_medium_priority_reminders(self, current_time, task_id, due_date):
        due_datetime = datetime.datetime.combine(due_date, datetime.time(0))
        time_remaining = due_datetime - current_time
        if time_remaining <= datetime.timedelta(days=5):
            self.speak(f"Reminder: Task ID {task_id} is due in {time_remaining.days} days.")
        elif time_remaining <= datetime.timedelta(days=1):
            hours_left = (time_remaining - datetime.timedelta(days=1)).total_seconds() // 3600
            self.speak(f"Reminder: Task ID {task_id} is due in {int(hours_left)} hours.")

    def check_high_priority_reminders(self, current_time, task_id, due_date):
        due_datetime = datetime.datetime.combine(due_date, datetime.time(0))
        time_remaining = due_datetime - current_time
        if time_remaining <= datetime.timedelta(days=10):
            self.speak(f"Reminder: Task ID {task_id} is due in {time_remaining.days} days.")
        elif time_remaining <= datetime.timedelta(days=3):
            hours_left = (time_remaining - datetime.timedelta(days=3)).total_seconds() // 3600
            self.speak(f"Reminder: Task ID {task_id} is due in {int(hours_left)} hours.")
        elif time_remaining <= datetime.timedelta(hours=1):
            self.speak(f"Reminder: Task ID {task_id} is due soon.")

# Main Function
def main():
    assistant = VoiceAssistant()
    while True:
        command = assistant.listen()
        if command:
            assistant.execute_command(command)
            assistant.check_reminders()
        time.sleep(60)  # Check reminders every minute

if __name__ == "__main__":
    main()
    sys.exit(0)
