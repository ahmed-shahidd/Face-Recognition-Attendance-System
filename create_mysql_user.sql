-- Drop the user if it exists
DROP USER IF EXISTS 'attendance_user'@'localhost';

-- Create a new user
CREATE USER 'attendance_user'@'localhost' IDENTIFIED BY 'attendance123';

-- Grant privileges to create and manage the database
GRANT ALL PRIVILEGES ON *.* TO 'attendance_user'@'localhost' WITH GRANT OPTION;

-- Apply the changes
FLUSH PRIVILEGES; 