#!/usr/bin/python3
import subprocess
import sys
import datetime
import json

LOG_FILE = "C:\\Program Files (x86)\\ossec-agent\\active-response\\active-responses.log"

def write_debug_file(ar_name, msg):
    with open(LOG_FILE, mode="a") as log_file:
        log_file.write(str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')) + " " + ar_name + ": " + msg + "\n")

def setup_and_check_message(argv):
    input_str = ""
    for line in sys.stdin:
        input_str = line
        break

    write_debug_file(argv[0], f"Raw input received: {input_str}")

    try:
        data = json.loads(input_str)
    except ValueError:
        write_debug_file(argv[0], 'Decoding JSON has failed, invalid input format')
        sys.exit(-1)

    return data

def extract_subject_username(data):
    try:
        username = data.get("parameters", {}).get("alert", {}).get("data", {}).get("win", {}).get("eventdata", {}).get("subjectUserName")
        if not username:
            raise ValueError("subjectUserName not found in alert data")
        return username
    except Exception as e:
        write_debug_file("disable_account", f"Failed to extract subjectUserName: {str(e)}")
        sys.exit(-1)

def disable_account(username):
    try:
        command = ["net", "user", username, "/active:no"]
        write_debug_file("disable_account", f"Running command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            write_debug_file("disable_account", f"Account {username} has been disabled successfully.")
        else:
            write_debug_file("disable_account", f"Failed to disable account {username}. Exit status: {result.returncode}")
            write_debug_file("disable_account", f"Command output: {result.stdout.strip()}")
            write_debug_file("disable_account", f"Command error: {result.stderr.strip()}")
    except Exception as e:
        write_debug_file("disable_account", f"Exception occurred while disabling account {username}: {str(e)}")

def logoff_user():
    try:
        # Først forsøg med query user
        try:
            result = subprocess.check_output(["query", "user"], shell=True, text=True)
            write_debug_file("logoff_user", f"Query user output: {result}")
            sessions = parse_query_user(result)
        except subprocess.CalledProcessError as e:
            write_debug_file("logoff_user", f"Query user failed. Return code: {e.returncode}. Falling back to qwinsta.")
            result = subprocess.check_output(["qwinsta"], shell=True, text=True)
            write_debug_file("logoff_user", f"Qwinsta output: {result}")
            sessions = parse_qwinsta(result)

        # Log brugere af
        if sessions:
            for username, session_id in sessions:
                write_debug_file("logoff_user", f"Attempting to log off user {username} with session ID {session_id}")
                success = logoff_user_via_session(session_id)
                if success:
                    write_debug_file("logoff_user", f"Successfully logged off user {username}")
                else:
                    write_debug_file("logoff_user", f"Failed to log off user {username}")
        else:
            write_debug_file("logoff_user", "No active user sessions found.")
    except Exception as e:
        write_debug_file("logoff_user", f"Exception occurred: {str(e)}")

def parse_qwinsta(output):
    """
    Parser output fra `qwinsta` og returnerer en liste af (brugernavn, session-ID).
    """
    sessions = []
    try:
        for line in output.splitlines()[1:]:  # Spring overskriftslinjen over
            parts = line.split()
            if len(parts) >= 3 and parts[0] != '>' and 'Disc' not in parts:  # Filtrer gyldige sessioner
                username = parts[1]  # Brugernavn er typisk andet felt
                session_id = parts[2]  # Session-ID er typisk tredje felt
                sessions.append((username, session_id))
    except Exception as e:
        write_debug_file("parse_qwinsta", f"Error parsing qwinsta output: {str(e)}")
    return sessions

def parse_query_user(query_output):
    """
    Parser output fra `query user` og returnerer en liste af (brugernavn, session-ID).
    """
    sessions = []
    try:
        for line in query_output.splitlines()[1:]:  # Spring overskriftslinjen over
            parts = line.split()
            if len(parts) >= 3:  # Forvent at brugernavn og session-ID er til stede
                username = parts[0]
                session_id = parts[2]
                sessions.append((username, session_id))
    except Exception as e:
        write_debug_file("parse_query_user", f"Error parsing query user output: {str(e)}")
    return sessions

def logoff_user_via_session(session_id):
    """
    Logger en bruger af via session-ID.
    """
    try:
        result = subprocess.call(["logoff", session_id], shell=True)
        return result == 0
    except Exception as e:
        write_debug_file("logoff_user_via_session", f"Error logging off session {session_id}: {str(e)}")
        return False

def main(argv):
    write_debug_file("disable_account", "Started")

    data = setup_and_check_message(argv)

    username = extract_subject_username(data)
    write_debug_file("disable_account", f"Username received: {username}")

    if username.startswith("DESKTOP"):
        write_debug_file("disable_account", "System account detected. Skipping action.")
        sys.exit(0)

    disable_account(username)
    logoff_user()

    write_debug_file("disable_account", "Ended")
    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)
