# Face Recognition Attendance System

A modern, automated attendance tracking system that uses facial recognition technology to mark student attendance in real-time. This project combines computer vision with database management to create an efficient, contactless attendance solution.

## Features

- **Real-time Face Recognition**: Uses OpenCV and face_recognition library for accurate face detection and recognition
- **Database Integration**: MySQL database to store and manage student records and attendance data
- **Multiple Camera Backend Support**: Supports different camera backends (DirectShow, Media Foundation) for better compatibility
- **Automatic Attendance Marking**: Automatically records attendance with timestamp when a registered face is recognized
- **Student Management**: Supports adding and managing student records with details like ID, name, and program
- **Error Handling**: Robust error handling for camera initialization and database operations
- **User-friendly Interface**: Real-time video feed with facial recognition boundaries and name display

## Technical Stack

- Python 3.x
- OpenCV (Computer Vision)
- face_recognition library
- MySQL Database
- tkinter (GUI components)
- PIL (Image Processing)

## Prerequisites

- Python 3.x
- MySQL Server
- Webcam
- Required Python packages (see requirements.txt)

## Database Structure

The system uses two main tables:
1. **students**: Stores student information (ID, name, program)
2. **attendance**: Records attendance data with timestamps

## Setup Instructions

1. Install required dependencies
2. Configure MySQL database settings in the script
3. Create a directory named 'ImagesAttendance' and add student photos
4. Run the main script

## Configuration

Update the DB_CONFIG dictionary in the script with your MySQL credentials:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'attendance_user',
    'password': 'Password@123',
    'database': 'attendance_db',
    'auth_plugin': 'mysql_native_password',
    'use_pure': True
}
```

## Usage

1. Add student photos to the ImagesAttendance directory
2. Run the script
3. The system will automatically detect faces and mark attendance
4. Press 'q' to quit the application

## Error Handling

The system includes comprehensive error handling for:
- Camera initialization issues
- Database connection problems
- Face detection and recognition errors
- Image processing failures

## Contributing

Feel free to fork this project and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
