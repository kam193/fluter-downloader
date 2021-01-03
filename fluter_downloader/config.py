from calibre.utils.config import JSONConfig
from PyQt5.Qt import QHBoxLayout, QLabel, QSpinBox, QWidget

prefs = JSONConfig("plugins/fluter_downloader")

prefs.defaults["max_numbers"] = 2


class ConfigWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.l = QHBoxLayout()
        self.setLayout(self.l)

        self.label = QLabel("Max number of last issues to download:")
        self.l.addWidget(self.label)

        self.max_number = QSpinBox(self)
        self.max_number.setValue(prefs["max_numbers"])
        self.max_number.setMinimum(0)
        self.l.addWidget(self.max_number)
        self.label.setBuddy(self.max_number)

    def save_settings(self):
        prefs["max_numbers"] = self.max_number.value()
        prefs.commit()
