import sys
from friday.friday_assistant import FridayAssistant

def main():
    assistant = FridayAssistant()
    assistant.run_interactive_shell()
    return 0

if __name__ == "__main__":
    sys.exit(main())
