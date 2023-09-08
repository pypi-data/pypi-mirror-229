from __future__ import annotations

from typing import TYPE_CHECKING

from automation_editor.automation_editor_ui.menu.menu_utils import open_web_browser

if TYPE_CHECKING:
    from automation_editor.automation_editor_ui.editor_main.main_ui import AutomationEditor
import sys

from PySide6.QtGui import QAction

from automation_editor.extend.process_executor.file_automation.file_automation_process import call_file_automation_test, \
    call_file_automation_test_with_send, call_file_automation_test_multi_file, \
    call_file_automation_test_multi_file_and_send


def set_automation_file_menu(ui_we_want_to_set: AutomationEditor):
    """
    Build menu include WebRunner feature.
    :param ui_we_want_to_set: main window to add menu.
    :return: None
    """
    ui_we_want_to_set.automation_file_menu = ui_we_want_to_set.menu.addMenu("FileAutomation")
    ui_we_want_to_set.automation_run_file_menu = ui_we_want_to_set.automation_file_menu.addMenu("Run")
    # Run FileAutomation Script
    ui_we_want_to_set.run_file_automation_action = QAction("Run FileAutomation Script")
    ui_we_want_to_set.run_file_automation_action.triggered.connect(
        lambda: call_file_automation_test(
            ui_we_want_to_set,
        )
    )
    ui_we_want_to_set.automation_run_file_menu.addAction(ui_we_want_to_set.run_file_automation_action)
    # Run FileAutomation Script With Send
    ui_we_want_to_set.run_file_automation_action_with_send = QAction("Run FileAutomation With Send")
    ui_we_want_to_set.run_file_automation_action_with_send.triggered.connect(
        lambda: call_file_automation_test_with_send(
            ui_we_want_to_set,
        )
    )
    ui_we_want_to_set.automation_run_file_menu.addAction(
        ui_we_want_to_set.run_file_automation_action_with_send
    )
    # Run Multi FileAutomation Script
    ui_we_want_to_set.run_multi_file_automation_action = QAction("Run Multi FileAutomation Script")
    ui_we_want_to_set.run_multi_file_automation_action.triggered.connect(
        lambda: call_file_automation_test_multi_file(
            ui_we_want_to_set,
        )
    )
    ui_we_want_to_set.automation_run_file_menu.addAction(
        ui_we_want_to_set.run_multi_file_automation_action
    )
    # Run Multi FileAutomation Script With Send
    ui_we_want_to_set.run_multi_file_automation_action_with_send = QAction("Run Multi FileAutomation Script With Send")
    ui_we_want_to_set.run_multi_file_automation_action_with_send.triggered.connect(
        lambda: call_file_automation_test_multi_file_and_send(
            ui_we_want_to_set,
        )
    )
    ui_we_want_to_set.automation_run_file_menu.addAction(
        ui_we_want_to_set.run_multi_file_automation_action_with_send
    )
    ui_we_want_to_set.file_automation_help_menu = ui_we_want_to_set.automation_file_menu.addMenu("HELP")
    # Open Doc
    ui_we_want_to_set.open_file_automation_doc_action = QAction("Open FileAutomation Doc")
    ui_we_want_to_set.open_file_automation_doc_action.triggered.connect(
        lambda: open_web_browser(
            ui_we_want_to_set,
            "https://fileautomation.readthedocs.io/en/latest/",
            "FileAutomation Doc"
        )
    )
    ui_we_want_to_set.file_automation_help_menu.addAction(
        ui_we_want_to_set.open_file_automation_doc_action
    )
    # Open Github
    ui_we_want_to_set.open_file_automation_github_action = QAction("Open FileAutomation GitHub")
    ui_we_want_to_set.open_file_automation_github_action.triggered.connect(
        lambda: open_web_browser(
            ui_we_want_to_set,
            "https://github.com/Integration-Automation/FileAutomation",
            "FileAutomation GitHub"
        )
    )
    ui_we_want_to_set.file_automation_help_menu.addAction(
        ui_we_want_to_set.open_file_automation_github_action
    )
    ui_we_want_to_set.file_automation_project_menu = ui_we_want_to_set.automation_file_menu.addMenu("Project")
    # Create Project
    ui_we_want_to_set.create_web_runner_project_action = QAction("Create FileAutomation Project")
    ui_we_want_to_set.create_web_runner_project_action.triggered.connect(
        create_project
    )
    ui_we_want_to_set.file_automation_project_menu.addAction(
        ui_we_want_to_set.create_web_runner_project_action
    )


def create_project() -> None:
    try:
        import file_automation
        package = file_automation
        if package is not None:
            package.create_project_dir()
    except ImportError as error:
        print(repr(error), file=sys.stderr)
