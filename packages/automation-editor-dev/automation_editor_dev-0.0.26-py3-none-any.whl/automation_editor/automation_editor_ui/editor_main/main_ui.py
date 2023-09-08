import sys
from typing import List, Dict, Type

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QWidget
from je_editor import EditorMain
from qt_material import apply_stylesheet

from automation_editor.automation_editor_ui.complete.complete_extend import complete_extend_package
from automation_editor.automation_editor_ui. \
    menu.api_testka_menu.build_api_testka_menu import set_apitestka_menu
from automation_editor.automation_editor_ui. \
    menu.auto_control_menu.build_autocontrol_menu import set_autocontrol_menu
from automation_editor.automation_editor_ui.menu.automation_file_menu.build_automation_file_menu import \
    set_automation_file_menu
from automation_editor.automation_editor_ui.menu.install_menu.build_install_menu import set_install_menu
from automation_editor.automation_editor_ui.menu. \
    load_density_menu.build_load_density_menu import set_load_density_menu
from automation_editor.automation_editor_ui.menu.mail_thunder_menu.build_mail_thunder_menu import set_mail_thunder_menu
from automation_editor.automation_editor_ui \
    .menu.web_runner_menu.build_webrunner_menu import set_web_runner_menu
from automation_editor.automation_editor_ui.syntax.syntax_extend import \
    syntax_extend_package

EDITOR_EXTEND_TAB: Dict[str, Type[QWidget]] = {}


class AutomationEditor(EditorMain):

    def __init__(self, debug_mode: bool = False):
        super().__init__()
        self.current_run_code_window: List[QWidget] = list()
        self.help_menu.deleteLater()
        set_autocontrol_menu(self)
        set_apitestka_menu(self)
        set_load_density_menu(self)
        set_web_runner_menu(self)
        set_automation_file_menu(self)
        set_mail_thunder_menu(self)
        set_install_menu(self)
        syntax_extend_package(self)
        complete_extend_package(self)
        # System tray change
        self.system_tray.main_window = self
        self.system_tray.setToolTip("Automation Editor")
        # Tab
        for widget_name, widget in EDITOR_EXTEND_TAB.items():
            self.tab_widget.addTab(widget(), widget_name)
        # Title
        self.setWindowTitle("Automation Editor")
        if debug_mode:
            close_timer = QTimer(self)
            close_timer.setInterval(10000)
            close_timer.timeout.connect(self.debug_close)
            close_timer.start()

    def closeEvent(self, event) -> None:
        for widget in self.current_run_code_window:
            widget.close()
        super().closeEvent(event)

    @classmethod
    def debug_close(cls) -> None:
        """
        Use to run CI test.
        :return: None
        """
        sys.exit(0)


def start_editor(debug_mode: bool = False, **kwargs) -> None:
    """
    Start editor instance
    :return: None
    """
    new_editor = QApplication(sys.argv)
    window = AutomationEditor(debug_mode, **kwargs)
    apply_stylesheet(new_editor, theme="dark_amber.xml")
    window.showMaximized()
    try:
        window.startup_setting()
    except Exception as error:
        print(repr(error))
    sys.exit(new_editor.exec())
