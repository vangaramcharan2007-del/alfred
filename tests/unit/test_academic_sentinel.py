"""Unit Tests for Jarvis X Academic & Homework Sentinel."""

import json
import os
import shutil
import tempfile
import time
import unittest

from jarvisx.academic.models import (
    AcademicTask,
    AlertEvent,
    ChannelSource,
    StudentProfile,
    TaskPriority,
    TaskStatus,
    TaskType,
)
from jarvisx.academic.normalizer import AssignmentNormalizer
from jarvisx.academic.solver_engine import AcademicSolverEngine
from jarvisx.academic.document_compiler import AcademicDocumentCompiler
from jarvisx.academic.alert_dispatcher import AcademicAlertDispatcher
from jarvisx.academic.submission_engine import AcademicSubmissionEngine
from jarvisx.academic.persistence import AcademicPersistenceManager
from jarvisx.academic.channel_hub import ChannelHub
from jarvisx.academic.sentinel_daemon import AcademicSentinelDaemon


class TestAcademicSentinel(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_academic.db")
        self.profile = StudentProfile()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_normalizer_priority_and_parsing(self):
        """Test urgency categorization and course extraction from raw notice."""
        body = "URGENT: Banker's safety algorithm assignment due tomorrow by 11:59 PM. Q1. Implement safety check."
        task = AssignmentNormalizer.normalize_message(
            channel=ChannelSource.GCR,
            sender="Prof. Natarajan",
            subject="21CSC202J Operating Systems Assignment",
            body=body,
        )
        self.assertEqual(task.channel, ChannelSource.GCR)
        self.assertEqual(task.course_code, "21CSC202J")
        self.assertIn(task.priority, [TaskPriority.URGENT, TaskPriority.EMERGENCY])
        self.assertTrue(len(task.questions) >= 1)

    def test_step_java_solver(self):
        """Test SRM STEP Program Java track solution generation and code deliverables."""
        task = AcademicTask(
            task_id="TEST-STEP-01",
            channel=ChannelSource.SRM_STEP_JAVA,
            course_code="STEP-JAVA",
            course_name="SRM STEP Program (Java Track)",
            title="Polymorphic Banking System Challenge",
            description="Implement BankAccount, SavingsAccount, CurrentAccount with custom exceptions and Streams.",
            deadline_epoch=time.time() + 36000,
            priority=TaskPriority.EMERGENCY,
            task_type=TaskType.JAVA_CODING_CHALLENGE,
        )
        solver = AcademicSolverEngine()
        solved = solver.solve_task(task)

        self.assertEqual(solved.status, TaskStatus.SOLVED)
        self.assertIn("BankAccount.java", solved.generated_code)
        self.assertIn("BankManager.java", solved.generated_code)
        self.assertIn("SavingsAccount.java", solved.generated_code)
        self.assertIn("CurrentAccount.java", solved.generated_code)
        self.assertIn("Exceptions.java", solved.generated_code)
        self.assertIn("InsufficientBalanceException", solved.generated_code["Exceptions.java"])
        self.assertIn("Streams", solved.solution_text)

    def test_nptel_mcq_solver(self):
        """Test NPTEL weekly assignment MCQ solver."""
        task = AcademicTask(
            task_id="TEST-NPTEL-01",
            channel=ChannelSource.NPTEL,
            course_code="NPTEL-CS06",
            course_name="DSA in Python",
            title="Week 5 Assignment: Heaps",
            description="Solve heap complexity MCQs.",
            deadline_epoch=time.time() + 86400,
            priority=TaskPriority.NORMAL,
            task_type=TaskType.NPTEL_ASSIGNMENT,
            questions=[
                {"q_id": "Q1", "text": "What is the time complexity to build a heap of n elements?"}
            ]
        )
        solver = AcademicSolverEngine()
        solved = solver.solve_task(task)
        self.assertEqual(solved.status, TaskStatus.SOLVED)
        self.assertIn("O(n)", solved.solution_text)
        self.assertEqual(solved.score_achieved, 100.0)

    def test_document_compiler(self):
        """Test DOCX and PDF document synthesis with student credentials."""
        task = AcademicTask(
            task_id="TEST-DOC-01",
            channel=ChannelSource.EMAIL,
            course_code="21MAB201T",
            course_name="Transforms & Boundary Value Problems",
            title="Fourier Series Worksheet",
            description="Calculate Fourier Series of x^2.",
            deadline_epoch=time.time() + 36000,
            priority=TaskPriority.URGENT,
            task_type=TaskType.WORKSHEET,
            solution_text="Fourier Series evaluated to pi^2 / 3 + 4 sum((-1)^n / n^2 cos(nx)).",
            generated_code={"main.c": "#include <stdio.h>\nint main(){return 0;}"}
        )
        compiler = AcademicDocumentCompiler(output_dir=os.path.join(self.test_dir, "docs"), profile=self.profile)
        compiled = compiler.compile_task(task)

        self.assertEqual(compiled.status, TaskStatus.COMPILED)
        self.assertTrue(os.path.exists(compiled.compiled_docx))
        self.assertTrue(os.path.exists(compiled.compiled_pdf))
        self.assertTrue(os.path.getsize(compiled.compiled_docx) > 500)
        self.assertTrue(os.path.getsize(compiled.compiled_pdf) > 500)

    def test_alert_dispatcher(self):
        """Test alert formatting, Windows toast invocation, and spoken text generation."""
        task = AcademicTask(
            task_id="TEST-ALERT-01",
            channel=ChannelSource.WHATSAPP,
            course_code="21CSC201J",
            course_name="Data Structures and Algorithms",
            title="Lab Record Submission Due Tonight",
            description="Submit BST operations worksheet.",
            deadline_epoch=time.time() + 7200,
            priority=TaskPriority.EMERGENCY,
        )
        alerter = AcademicAlertDispatcher(enable_voice=False, enable_toast=False)
        event = alerter.dispatch_task_alert(task, is_solved=False)

        self.assertTrue(event.delivered)
        self.assertIn("EMERGENCY", event.title)
        self.assertIn("Data Structures and Algorithms", event.spoken_text)

    def test_submission_engine_step_java_packaging(self):
        """Test STEP Java deliverable zip packaging."""
        task = AcademicTask(
            task_id="STEP-JAVA-PKG",
            channel=ChannelSource.SRM_STEP_JAVA,
            course_code="STEP-JAVA",
            course_name="SRM STEP Program (Java Track)",
            title="Banking Challenge",
            description="OOP solution",
            deadline_epoch=time.time() + 10000,
            task_type=TaskType.JAVA_CODING_CHALLENGE,
            generated_code={"BankAccount.java": "public class BankAccount {}"},
        )
        engine = AcademicSubmissionEngine(profile=self.profile)
        submitted = engine.process_submission(task)

        self.assertEqual(submitted.status, TaskStatus.SUBMITTED)
        self.assertTrue(os.path.exists(submitted.submission_link))
        self.assertTrue(submitted.submission_link.endswith(".zip"))

    def test_persistence_crud(self):
        """Test SQLite persistence of tasks and alerts."""
        pm = AcademicPersistenceManager(self.db_path)
        task = AcademicTask(
            task_id="TASK-PERSIST-01",
            channel=ChannelSource.TEAMS,
            course_code="21CSC201J",
            course_name="DSA",
            title="Double Hashing",
            description="Test hashing",
            deadline_epoch=time.time() + 50000,
            priority=TaskPriority.NORMAL,
        )
        pm.save_task(task)
        loaded = pm.get_task("TASK-PERSIST-01")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.title, "Double Hashing")
        self.assertEqual(loaded.channel, ChannelSource.TEAMS)

    def test_full_sentinel_cycle(self):
        """Test complete autonomous cycle across all 7 channels."""
        daemon = AcademicSentinelDaemon(
            db_path=self.db_path,
            enable_voice=False,
            enable_toast=False,
            profile=self.profile
        )
        summary = daemon.execute_cycle()
        self.assertTrue(summary["tasks_ingested"] >= 6)
        self.assertTrue(summary["tasks_solved"] >= 6)
        self.assertTrue(summary["tasks_submitted"] >= 6)

    def test_mail_watcher_detection(self):
        """Test AcademicMailWatcher scanning and task extraction."""
        from jarvisx.academic.mail_watcher import AcademicMailWatcher
        watcher = AcademicMailWatcher(self.profile)
        res = watcher.check_inbox()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("discovered_tasks", res)
        self.assertTrue(res["total_emails_inspected"] >= 1)

    def test_step_java_curriculum_all_weeks(self):
        """Test StepJavaCurriculumSolver generation across all Weeks 1 to 6."""
        from jarvisx.academic.step_solver import StepJavaCurriculumSolver
        solver = StepJavaCurriculumSolver()
        
        expected_files = {
            1: ["PrimeOperations.java", "MatrixCompute.java", "Week1Test.java"],
            2: ["Employee.java", "SalariedEmployee.java", "HourlyEmployee.java", "PayrollManager.java", "Week2PayrollTest.java"],
            3: ["PaymentGateway.java", "Refundable.java", "UPIPayment.java", "CreditCardPayment.java", "Week3PaymentTest.java"],
            4: ["BankAccount.java", "SavingsAccount.java", "CurrentAccount.java", "Exceptions.java", "BankManager.java", "Week4BankingTest.java"],
            5: ["Student.java", "StudentAnalyticsEngine.java", "Week5AnalyticsTest.java"],
            6: ["Order.java", "OrderProcessorPool.java", "Week6ConcurrencyTest.java"],
        }
        for week_num, fnames in expected_files.items():
            week_data = solver.solve_week(week_num)
            self.assertEqual(week_data["week"], week_num)
            self.assertEqual(week_data["package"], f"com.srm.step.week{week_num}")
            for fname in fnames:
                self.assertIn(fname, week_data["files"], f"Missing {fname} in week {week_num}")


if __name__ == "__main__":
    unittest.main()
