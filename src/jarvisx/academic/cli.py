"""Academic Sentinel CLI.

Command line interface for student academic management:
- status: prints all tracked homework and assessments
- scan: triggers immediate sweep across all 7 channels
- solve: solves a specific task or all pending tasks
- daemon: runs the background autonomous sentinel cycle
"""

from __future__ import annotations
import argparse
import json
import sys
from tabulate import tabulate

from jarvisx.academic.sentinel_daemon import AcademicSentinelDaemon
from jarvisx.academic.models import TaskStatus


def main():
    parser = argparse.ArgumentParser(description="Jarvis X Academic & Homework Sentinel CLI")
    subparsers = parser.add_subparsers(dest="command", help="Academic commands")

    # status
    subparsers.add_parser("status", help="Display all active academic tasks and statuses")

    # scan
    subparsers.add_parser("scan", help="Scan all channels for new homework or deadlines")

    # solve
    solve_parser = subparsers.add_parser("solve", help="Solve pending assignments")
    solve_parser.add_argument("--task-id", help="Specific task ID to solve")

    # daemon
    daemon_parser = subparsers.add_parser("daemon", help="Run the autonomous sentinel daemon")
    daemon_parser.add_argument("--once", action="store_true", help="Execute single cycle then exit")

    args = parser.parse_args()

    daemon = AcademicSentinelDaemon()

    if args.command == "status":
        tasks = daemon.persistence.get_all_tasks()
        if not tasks:
            print("No academic tasks currently tracked in database.")
            return

        table_data = []
        for t in tasks:
            table_data.append([
                t.task_id,
                t.channel.value,
                t.course_code,
                t.title[:30],
                f"{t.hours_remaining:.1f}h",
                t.priority.value,
                t.status.value,
            ])
        headers = ["Task ID", "Channel", "Course", "Title", "Remaining", "Priority", "Status"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

    elif args.command == "scan" or (args.command == "daemon" and args.once):
        print("Executing autonomous academic cycle across all 7 channels...")
        summary = daemon.execute_cycle()
        print(f"Cycle completed in {summary['duration_seconds']}s.")
        print(f"Tasks Ingested: {summary['tasks_ingested']} | Solved: {summary['tasks_solved']} | Submitted: {summary['tasks_submitted']}")

    elif args.command == "solve":
        tasks = daemon.persistence.get_all_tasks()
        target_tasks = [t for t in tasks if not args.task_id or t.task_id == args.task_id]
        for t in target_tasks:
            print(f"Solving {t.task_id} - {t.title}...")
            t = daemon.solver.solve_task(t)
            t = daemon.compiler.compile_task(t)
            daemon.persistence.save_task(t)
            print(f"Compiled DOCX: {t.compiled_docx}")
            print(f"Compiled PDF: {t.compiled_pdf}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
