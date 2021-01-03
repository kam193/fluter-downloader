import re
from contextlib import suppress
from dataclasses import dataclass
from typing import Callable, List

import mechanize
from calibre import browser as calibre_browser
from calibre import random_user_agent
from calibre.ebooks.metadata.pdf import get_metadata
from calibre.ptempfile import PersistentTemporaryDirectory


@dataclass
class Heft:
    number: int
    title: str
    link: mechanize.Link
    pdf_link: mechanize.Link = None


heft_link_matcher = re.compile(r"^\/heft([0-9]+)$")


class FluterDownloader:
    pdf_name_template = "Fluter_{heft.number}.pdf"
    title_template = "fluter Nr. {heft.number} - {heft.title}"

    def __init__(self, max_downloaded: int, db, reporter: Callable = None) -> None:
        self._max_downloaded = max_downloaded
        self._dir = PersistentTemporaryDirectory()
        self._db = db
        self._reporter = reporter

    def report_progress(self, value, text):
        if self._reporter:
            self._reporter(value, text)

    def get_browser(self) -> mechanize.Browser:
        browser = calibre_browser(user_agent=random_user_agent(allow_ie=False))
        browser.addheaders += [("Accept", "*/*")]
        return browser

    def _get_heft_list(self, browser) -> List[Heft]:
        browser.open("https://fluter.de/hefte")

        hefts = []
        for link in browser.links():
            if link.text and (match := re.search(heft_link_matcher, link.url)):
                with suppress(TypeError, ValueError):
                    heft = Heft(int(match.group(1)), link.text, link)
                    hefts.append(heft)
        return hefts

    def _get_pdf_link(self, heft: Heft, browser: mechanize.Browser) -> mechanize.Link:
        browser.follow_link(heft.link)
        pdf_link = browser.find_link(text_regex="Herunterladen")

        if not pdf_link or not isinstance(pdf_link, mechanize.Link):
            raise Exception("Link to the PDF not found")

        return pdf_link

    def _download_heft(self, heft: Heft, browser: mechanize.Browser):
        filename = self.pdf_name_template.format(heft=heft)
        pdf_data = browser.follow_link(heft.pdf_link)
        with open(f"{self._dir}/{filename}", "bw+") as pdf_file:
            pdf_file.write(pdf_data.read())
        browser.back()
        return f"{self._dir}/{filename}"

    def _parse_index(self, browser: mechanize.Browser) -> List[Heft]:
        self.report_progress(0, "Listing magazines")
        hefts = self._get_heft_list(browser)
        self.report_progress(0.1, f"Found {len(hefts)} issues of Fluter")

        hefts.sort(key=lambda k: k.number, reverse=True)
        selected_len = min(len(hefts), self._max_downloaded)

        for idx, heft in enumerate(hefts[:selected_len]):
            progress = 0.2 + 0.1 * ((idx + 1) / selected_len)
            self.report_progress(
                progress, f"Processing {idx+1} of {selected_len} newest"
            )
            heft.pdf_link = self._get_pdf_link(heft, browser)

        return list(hefts[:selected_len])

    def _add_heft_to_db(self, heft: Heft, pdf_file: str):
        with open(pdf_file, "rb") as file:
            mi = get_metadata(file)
        mi.title = self.title_template.format(heft=heft)
        mi.authors = ["fluter Redaktion"]
        mi.languages = ["Deutsch"]
        mi.publisher = "Bundeszentrale für politische Bildung (bpb)"
        mi.series = "fluter"
        mi.series_index = heft.number

        ids, dups = self._db.add_books([(mi, {"PDF": pdf_file})], add_duplicates=False)

        return len(ids)

    def download(self):
        browser = self.get_browser()
        hefts = self._parse_index(browser)

        added = 0
        for idx, heft in enumerate(hefts):
            progress = 0.3 + (0.69 * ((idx + 1) / len(hefts)))
            self.report_progress(progress, f"Downloading Fluter {heft.number}")
            file_path = self._download_heft(heft, browser)
            added += self._add_heft_to_db(heft, file_path)

        self.report_progress(1, f"{added} new issues added to Calibre")
