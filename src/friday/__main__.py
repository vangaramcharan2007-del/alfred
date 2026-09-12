import sys
from friday.friday_assistant import FridayAssistant

USAGE = """friday - print today's executive dashboard

Usage:
  friday              show today's schedule, CGPA plan, assignments, health
                      reminders, habits, goals, proactive alerts and exam
                      readiness
  friday -h, --help   show this message

There is no interactive mode. This command prints the dashboard once and exits.
"""


def main():
    if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
        print(USAGE)
        return 0
    # `friday` was ignoring argv entirely, so --help launched the dashboard.
    # Unknown flags are rejected rather than silently treated as "show the
    # dashboard", because a typo'd flag that appears to succeed is worse than
    # one that reports itself.
    unknown = [a for a in sys.argv[1:] if a.startswith("-")]
    if unknown:
        print(f"friday: unknown option {' '.join(unknown)}\n", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        return 2
    FridayAssistant().show_dashboard()
    return 0

if __name__ == "__main__":
    sys.exit(main())
