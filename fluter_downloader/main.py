from PyQt5.Qt import (QDialog, QLabel, QMessageBox, QProgressBar, QPushButton,
                      QVBoxLayout)

from .config import prefs
from .downloader import FluterDownloader


class FluterDownloaderDialog(QDialog):
    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        self.db = gui.current_db

        self.l = QVBoxLayout()
        self.setLayout(self.l)

        self.label = QLabel("This plugin helps download last issues from fluter.de")
        self.l.addWidget(self.label)

        self.setWindowTitle("Unofficial fluter. Downloader")
        self.setWindowIcon(icon)

        self.progress_bar = QProgressBar(self)
        self.l.addWidget(self.progress_bar)

        self.progress_label = QLabel("Waiting to start")
        self.l.addWidget(self.progress_label)

        self.add_button = QPushButton("Download new fluter. issues", self)
        self.add_button.clicked.connect(self.add_fluter)
        self.l.addWidget(self.add_button)

        self.conf_button = QPushButton("Configure", self)
        self.conf_button.clicked.connect(self.config)
        self.l.addWidget(self.conf_button)

        self.about_button = QPushButton("About", self)
        self.about_button.clicked.connect(self.about)
        self.l.addWidget(self.about_button)

        self.resize(self.sizeHint())

    def about(self):
        text = get_resources("about.txt")
        QMessageBox.about(self, "About the fluter. Downloader", text.decode("utf-8"))

    def config(self):
        self.do_user_config(parent=self)

    def add_fluter(self):
        self.progress_bar.reset()
        self.progress_label.setText("")

        downloader = FluterDownloader(
            prefs["max_numbers"], self.db.new_api, reporter=self._report_progress
        )
        downloader.download()
        self.gui.refresh_all()

    def _report_progress(self, value: float, text: str):
        self.progress_label.setText(text)
        self.progress_bar.setValue(int(100.0 * value))
