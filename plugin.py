from calibre.gui2.actions import InterfaceAction
from .main import FluterDownloaderDialog


class FluterDownloaderPlugin(InterfaceAction):

    name = "fluter. Downloader"

    action_spec = (
        "fluter. Downloader",
        None,
        "Open fluter. Downloader window",
        None,
    )

    def genesis(self):
        icon = get_icons("images/icon.png")
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_dialog)

    def show_dialog(self):
        d = FluterDownloaderDialog(
            self.gui,
            self.qaction.icon(),
            self.interface_action_base_plugin.do_user_config,
        )
        d.show()

    def apply_settings(self):
        pass
