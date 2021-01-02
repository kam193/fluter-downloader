from calibre.customize import InterfaceActionBase


class FluterDownloader(InterfaceActionBase):
    name = "fluter. Downloader"
    description = "Download fluter. Magazine"
    supported_platforms = ["windows", "osx", "linux"]
    author = "Kamil Mańkowski"
    version = (0, 0, 1)
    minimum_calibre_version = (5, 0, 1)

    actual_plugin = "calibre_plugins.fluter_downloader.plugin:FluterDownloaderPlugin"

    def is_customizable(self):
        return True

    def config_widget(self):
        from .config import ConfigWidget

        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()

        if self.actual_plugin_ is not None:
            self.actual_plugin_.apply_settings()