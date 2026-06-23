import sys
print("Python version:", sys.version)

try:
    import cv2
    print("OpenCV version:", cv2.__version__)
except ImportError as e:
    print("Error importing OpenCV:", e)
    sys.exit(1)

try:
    import numpy as np
    print("NumPy version:", np.__version__)
except ImportError as e:
    print("Error importing NumPy:", e)
    sys.exit(1)

try:
    import face_recognition
    print("Face Recognition version:", face_recognition.__version__)
except ImportError as e:
    print("Error importing face_recognition:", e)
    sys.exit(1)

try:
    import mysql.connector
    print("MySQL Connector version:", mysql.connector.__version__)
except ImportError as e:
    print("Error importing mysql.connector:", e)
    sys.exit(1)

try:
    import tkinter as tk
    from tkinter import ttk
    from PIL import Image, ImageTk
except ImportError as e:
    print("Error importing tkinter:", e)
    sys.exit(1)

import os
from datetime import datetime
import time

def initialize_camera():
    print("\nAttempting to open webcam...")
    # Try different backends
    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_ANY, "Any")
    ]
    
    for backend, name in backends:
        print(f"\nTrying {name} backend...")
        cap = cv2.VideoCapture(0 + backend)
        
        if not cap.isOpened():
            print(f"Could not open camera with {name} backend")
            continue
            
        print(f"Successfully opened camera with {name} backend")
        
        # Try to read a frame
        for _ in range(5):  # Try 5 times
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"Successfully read frame with {name} backend")
                # Set camera properties
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
                # Set buffer size to 1 to get the latest frame
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                return cap
            time.sleep(0.5)  # Wait a bit before trying again
            
        print(f"Could not read frame with {name} backend")
        cap.release()
    
    print("\nTroubleshooting tips:")
    print("1. Make sure no other application is using the webcam")
    print("2. Check if your webcam is enabled in Windows settings")
    print("3. Try unplugging and replugging your webcam")
    print("4. Check Device Manager to ensure webcam is working properly")
    print("5. Try running the Windows Camera app to test if your webcam works")
    return None

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'attendance_user',
    'password': 'Password@123',
    'database': 'attendance_db',
    'auth_plugin': 'mysql_native_password',
    'use_pure': True
}

def setup_database():
    try:
        # First try to connect without database
        print("Attempting to connect to MySQL server...")
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            auth_plugin=DB_CONFIG['auth_plugin'],
            use_pure=DB_CONFIG['use_pure']
        )
        print("Successfully connected to MySQL server!")
        
        cursor = conn.cursor()
        print("Creating database if it doesn't exist...")
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        print(f"Database '{DB_CONFIG['database']}' created/selected successfully!")

        # Create students table
        print("Creating students table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                program VARCHAR(100) NOT NULL
            )
        """)

        # Create attendance table with name column
        print("Creating attendance table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(20),
                student_name VARCHAR(100),
                date DATE,
                time TIME,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        """)

        conn.commit()
        print("Database and tables created successfully!")
        return True
    except mysql.connector.Error as err:
        if err.errno == 1045:  # Access denied error
            print("\nError: Could not connect to MySQL. Please check your username and password.")
            print("Current configuration:")
            print(f"Username: {DB_CONFIG['user']}")
            print(f"Password: {'*' * len(DB_CONFIG['password'])}")
            print("\nPlease make sure:")
            print("1. MySQL server is running")
            print("2. The user 'attendance_user' exists in MySQL")
            print("3. The password is correct")
            print("4. The user has proper privileges")
        elif err.errno == 2059:  # Authentication plugin error
            print("\nError: Authentication plugin issue. Please make sure:")
            print("1. MySQL server is running")
            print("2. The user is created with mysql_native_password authentication")
            print("3. MySQL Connector/Python is properly installed")
            print("\nTry running these SQL commands in MySQL Workbench:")
            print("ALTER USER 'attendance_user'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Password@123';")
            print("FLUSH PRIVILEGES;")
        else:
            print(f"Error setting up database: {err}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            auth_plugin=DB_CONFIG['auth_plugin'],
            use_pure=DB_CONFIG['use_pure']
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == 1045:  # Access denied error
            print("\nError: Could not connect to MySQL. Please check your username and password.")
        elif err.errno == 2059:  # Authentication plugin error
            print("\nError: Authentication plugin issue. Please make sure the user is created with mysql_native_password authentication.")
        else:
            print(f"Error connecting to database: {err}")
        return None

def markAttendance(name):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to connect to database. Please check your MySQL credentials.")
            return False

        cursor = conn.cursor()
        
        # Get current date and time
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        # Get student ID from name
        student_id = name_to_id.get(name)
        if not student_id:
            print(f"Warning: No ID mapping found for {name}")
            return False
            
        # Check if attendance already marked for today
        cursor.execute("""
            SELECT COUNT(*) FROM attendance 
            WHERE student_id = %s AND date = %s
        """, (student_id, date_str))
        
        if cursor.fetchone()[0] == 0:
            # Insert new attendance record
            cursor.execute("""
                INSERT INTO attendance (student_id, student_name, date, time)
                VALUES (%s, %s, %s, %s)
            """, (student_id, name, date_str, time_str))
            
            conn.commit()
            print(f"Marked attendance for {name} at {time_str}")
        else:
            print(f"Attendance already marked for {name} today")
            
        return True

    except mysql.connector.Error as err:
        print(f"Error marking attendance: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def add_student(student_id, name, program):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to connect to database. Please check your MySQL credentials.")
            return False

        cursor = conn.cursor()
        
        # Check if student already exists
        cursor.execute("SELECT COUNT(*) FROM students WHERE student_id = %s", (student_id,))
        if cursor.fetchone()[0] > 0:
            print(f"Student {name} (ID: {student_id}) already exists in database")
            return True

        # Insert new student
        cursor.execute("""
            INSERT INTO students (student_id, name, program)
            VALUES (%s, %s, %s)
        """, (student_id, name, program))
        
        conn.commit()
        print(f"Added student {name} (ID: {student_id}) to database")
        return True

    except mysql.connector.Error as err:
        print(f"Error adding student: {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Add sample students (you can modify these or add more)
students = [
    ("23108153", "Ahmed Shahid", "Artificial Intelligence"),
    ("23108155", "Bhavaish", "Artificial Intelligence"),
    ("23108172", "Rahul", "Artificial Intelligence"),
    ("23108180", "Waleed", "Artificial Intelligence"),
    ("23108182", "Ahmed", "Artificial Intelligence"),
    ("23108183", "Fawad", "Artificial Intelligence"),
    ("23108184", "Hasnain", "Artificial Intelligence"),
    ("23108185", "Imad", "Artificial Intelligence"),
    ("23108164", "Ahmed Rayyan", "Artificial Intelligence"),
    ("23108186", "Zain", "Artificial Intelligence"),
    ("23108161", "Imad", "Artificial Intelligence"),
    ("23108178", "Hamza", "Artificial Intelligence"),
    ("23108183", "Umar", "Artificial Intelligence"),
    ("23108154", "Ali Naseer", "Artificial Intelligence"),
    
]

# Setup database first
print("\nSetting up database...")
if not setup_database():
    print("Failed to setup database. Exiting...")
    sys.exit(1)

# Add students to database
print("\nAdding students to database...")
for student_id, name, program in students:
    if not add_student(student_id, name, program):
        print(f"Failed to add student {name}. Please check your MySQL connection.")
        sys.exit(1)

print("\nStarting face recognition system...")

# Check if ImagesAttendance directory exists
path = 'ImagesAttendance'
if not os.path.exists(path):
    print(f"Error: {path} directory not found!")
    sys.exit(1)

# List and load images
images = []
classNames = []
studentIds = []  # New list to store student IDs
myList = os.listdir(path)
print("Found images:", myList)

# Create name to ID mapping
name_to_id = {
    'AHMED SHAHID': '23108153',
    'BHAVAISH': '23108155',
    'RAHUL': '23108172',
    'WALEED': '23108180',
    'AHMED': '23108182',
    'FAWAD': '23108183',
    'HASNAIN': '23108184',
    'IMAD': '23108185',
    'AHMED RAYYAN': '23108164',
    'ZAIN': '23108186',
    'IMAD': '23108161',
    'HAMZA': '23108178',
    'UMAR': '23108183',
    'ALI NASEER': '23108154'
}

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    if curImg is not None:
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
print("Loaded names:", classNames)

def findEncodings(images):
    encodeList = []
    for idx, img in enumerate(images):
        try:
            # Convert to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Detect faces
            face_locations = face_recognition.face_locations(img)
            if not face_locations:
                print(f"Warning: No face detected in image {classNames[idx]}")
                continue
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(img, face_locations)
            if not face_encodings:
                print(f"Warning: Could not encode face in image {classNames[idx]}")
                continue
                
            encode = face_encodings[0]
            encodeList.append(encode)
            print(f"Successfully encoded face for {classNames[idx]}")
            
        except Exception as e:
            print(f"Error processing image {classNames[idx]}: {str(e)}")
            continue
    
    if not encodeList:
        print("Error: No faces could be encoded! Please check your images.")
        sys.exit(1)
    
    print(f"Successfully encoded {len(encodeList)} faces out of {len(images)} images")
    return encodeList

print("\nEncoding faces...")
encodeListKnown = findEncodings(images)
print("Encoding Complete")

print("\nInitializing camera...")
cap = initialize_camera()

if cap is None:
    print("\nError: Could not open camera with any backend!")
    sys.exit(1)

print("\nStarting main loop...")
print("Press 'q' to quit")

try:
    while True:
        success, img = cap.read()
        
        if not success or img is None:
            print("Failed to grab frame, reinitializing camera...")
            cap.release()
            cap = initialize_camera()
            if cap is None:
                print("Failed to reinitialize camera. Exiting...")
                break
            continue

        # Resize image for faster face recognition processing
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        # Find faces in current frame
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                if name in name_to_id:
                    student_id = name_to_id[name]
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    markAttendance(name)
                else:
                    print(f"Warning: No ID mapping found for {name}")

        cv2.imshow('Webcam', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    if 'cap' in globals():
        cap.release()
    cv2.destroyAllWindows()
    print("\nProgram ended")
