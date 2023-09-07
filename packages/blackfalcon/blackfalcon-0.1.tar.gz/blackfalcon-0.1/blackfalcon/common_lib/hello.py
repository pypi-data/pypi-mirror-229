import os
def greet():
    print("Hello from the blackfalcon package!")

def version():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    version_file_path = os.path.join(current_directory, "version.txt")
    
    with open(version_file_path, "r") as file:
        print(file.read())
