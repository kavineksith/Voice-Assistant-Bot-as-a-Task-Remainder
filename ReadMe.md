# Voice Assistant Documentation

## Overview

The `VoiceAssistant` Python script is a sophisticated voice-controlled application designed for managing tasks and reminders. Leveraging speech recognition and text-to-speech technologies, this script allows users to interact with a task management system through voice commands. It integrates a SQLite database to store and manage tasks, enabling functionalities such as adding, updating, deleting, searching, and viewing tasks, as well as setting and checking reminders.

## Features

- **Voice Interaction**: Utilizes `speech_recognition` for understanding voice commands and `pyttsx3` for vocal responses.
- **Task Management**: Supports adding, updating, deleting, and searching tasks with attributes such as due date and priority.
- **Reminders**: Allows users to set reminders with specific texts and times, and checks for upcoming reminders based on task priority.
- **Error Handling**: Implements custom exceptions to handle database errors, task-related issues, and general errors gracefully.
- **Persistent Storage**: Employs an SQLite database for storing task data and a text file for reminders.

## Dependencies

- **SQLite3**: For database operations.
- **SpeechRecognition**: For converting speech into text.
- **pyttsx3**: For converting text into speech.
- **Datetime**: For handling date and time-related operations.
- **Regular Expressions (re)**: For parsing commands.

Ensure the following Python libraries are installed:
```bash
pip install SpeechRecognition pyttsx3
```

## Usage

1. **Setup**: Ensure that the required libraries are installed and accessible.
2. **Running the Script**: Execute the script using Python:
   ```bash
   python voice_assistant.py
   ```
3. **Interaction**: Speak commands into the microphone. The assistant will process these commands and respond verbally.

## Interactive Commands

- **Add Task**:
  - Command Pattern: `add task: <task_description> due by <due_date> priority <priority>`
  - Example: `add task: Buy groceries due by 2024-08-15 priority high`
  - Description: Adds a new task with a description, due date, and priority level.

- **Update Task**:
  - Command Pattern: `update task <task_id> <status>`
  - Example: `update task 3 completed`
  - Description: Updates the status of a specified task by its ID.

- **Delete Task**:
  - Command Pattern: `delete task <task_id>`
  - Example: `delete task 2`
  - Description: Deletes a task identified by its ID.

- **Search Task**:
  - Command Pattern: `search task: <keyword>`
  - Example: `search task: groceries`
  - Description: Searches for tasks containing the specified keyword.

- **View Tasks**:
  - Command Pattern: `view tasks`
  - Description: Lists all tasks in the database.

- **Set Reminder**:
  - Command Pattern: `reminder for <text> at <time>`
  - Example: `reminder for call John at 15:30`
  - Description: Sets a reminder with the specified text and time.

## Special Commands

- **`add_task(command)`**:
  - Parses the command to extract task details and adds it to the database.
  - Raises `VoiceAssistantError` for command errors.

- **`update_task(command)`**:
  - Parses the command to update a task’s status.
  - Raises `TaskNotFoundError` if the task ID does not exist.

- **`delete_task(command)`**:
  - Parses the command to delete a task.
  - Raises `TaskNotFoundError` if the task ID does not exist.

- **`search_task(command)`**:
  - Searches for tasks containing the specified keyword.
  - Returns results and handles errors in search operations.

- **`view_tasks()`**:
  - Retrieves and lists all tasks from the database.

- **`set_reminder(command)`**:
  - Parses the command to set a reminder and stores it in a text file.
  - Handles time format validation and file writing.

- **`check_reminders()`**:
  - Checks for tasks with approaching deadlines and notifies the user based on priority.

## Conclusion

The `VoiceAssistant` script provides a versatile voice-controlled interface for managing tasks and reminders. Its integration of speech recognition and text-to-speech technologies makes it a user-friendly tool for hands-free task management. With robust error handling and a persistent SQLite database, the assistant offers reliable performance and easy access to task-related information. Ensure the script's dependencies are properly installed and configured for optimal functionality.

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## **Disclaimer:**

Kindly note that this project is developed solely for educational purposes, not intended for industrial use, as its sole intention lies within the realm of education. We emphatically underscore that this endeavor is not sanctioned for industrial application. It is imperative to bear in mind that any utilization of this project for commercial endeavors falls outside the intended scope and responsibility of its creators. Thus, we explicitly disclaim any liability or accountability for such usage.