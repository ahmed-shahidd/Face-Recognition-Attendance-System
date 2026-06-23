import cv2
import time

# print("OpenCV version:", cv2.version)

def try_camera(index):
    print(f"\nTrying camera index {index}...")
    # Try different backends
    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_ANY, "Any")
    ]
    
    for backend, name in backends:
        print(f"\nTrying {name} backend...")
        cap = cv2.VideoCapture(index + backend)
        
        if not cap.isOpened():
            print(f"Could not open camera with {name} backend")
            continue
            
        print(f"Successfully opened camera with {name} backend")
        
        # Try to read a frame
        for _ in range(5):  # Try 5 times
            ret, frame = cap.read()
            if ret:
                print(f"Successfully read frame with {name} backend")
                cv2.imshow(f'Camera {index} - {name}', frame)
                cv2.waitKey(2000)  # Show for 2 seconds
                cap.release()
                cv2.destroyAllWindows()
                return True
            time.sleep(0.5)  # Wait a bit before trying again
            
        print(f"Could not read frame with {name} backend")
        cap.release()
    
    return False

print("\nTesting webcam access...")
print("This will try different methods to access your webcam")
print("Please wait while we test each method...")

# Try first 2 camera indices
for i in range(2):
    if try_camera(i):
        print(f"\nFound working camera at index {i}")
        print("You can use this index in the attendance system")
        break
else:
    print("\nNo working camera found!")
    print("\nTroubleshooting steps:")
    print("1. Make sure your webcam is not being used by any other application")
    print("2. Try restarting your computer")
    print("3. Check if your webcam works in Windows Camera app")
    print("4. Update your webcam drivers")

print("\nTest completed")