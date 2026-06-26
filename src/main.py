# src/main.py
import sys

def main():
    if len(sys.argv) < 2:
        print("Voice Idea Capture CLI")
        print("Usage: python3 src/main.py [run|watch|status]")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    print(f"Command '{command}' is not implemented yet. Let's build it!")

if __name__ == "__main__":
    main()
