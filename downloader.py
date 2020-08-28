import os
import re
import tempfile
import urllib.request
import zipfile
from multiprocessing import Process


class Downloader():
    def __init__(self):
        github = 'https://github.com/'
        self.space_url = github + 'syl20bnr/spacemacs/archive/develop.zip'
        self.doom_url = github + 'hlissner/doom-emacs/archive/develop.zip'

        deb_pkgs = 'https://packages.debian.org/'
        self.deb_emacs_el = deb_pkgs + 'sid/all/emacs-el/download'

        deb_repo = 'https://deb.debian.org/debian/'
        self.deb_download_link = deb_repo + 'pool/main/e/emacs/'
        self.deb_uploaders = deb_repo + 'indices/Uploaders'

        self.temp_directory = tempfile.TemporaryDirectory()

    def download(self):
        """
        Download everything using several processes.
        """
        os.chdir(self.temp_directory.name)

        runners = [Process(target=self._download_flavor,
                           args=(self.space_url,)),
                   Process(target=self._download_flavor,
                           args=(self.doom_url,)),
                   Process(target=self._download_builtins, args=()),
                   Process(target=self._download_uploaders, args=())]

        for r in runners:
            r.start()

        for r in runners:
            r.join()

    def _download_flavor(self, url):
        """
        Download and extract current flavors snapshots in the temporary
        directory.
        """
        if 'spacemacs' in url:
            flavor = 'Spacemacs'
            filename = 'spacemacs.zip'
        elif 'doom-emacs' in url:
            flavor = 'Doom Emacs'
            filename = 'doomemacs.zip'
        print(f'Downloading {flavor} source...')
        with urllib.request.urlopen(url) as response, open(filename,
                                                           'wb') as out_file:
            data = response.read()
            out_file.write(data)
            with zipfile.ZipFile(filename) as zip_archive:
                print(f'Extracting {flavor} source...')
                zip_archive.extractall(path=self.temp_directory.name)

    def _download_builtins(self):
        """
        Get the full package name of emacs-el in unstable and download it.
        """
        emacs_page = urllib.request.urlopen(self.deb_emacs_el).read().decode()
        emacs_pkgname = re.findall(r'(emacs-el_.+_all.deb)', emacs_page)[0]
        url = self.deb_download_link + emacs_pkgname
        print(f'Downloading {emacs_pkgname}...')
        with urllib.request.urlopen(url) as response, open(emacs_pkgname,
                                                           'wb') as out_file:
            data = response.read()
            out_file.write(data)

    def _download_uploaders(self):
        """
        Download current Debian archive index (unstable).
        """
        print('Downloading Uploaders...')
        with urllib.request.urlopen(self.deb_uploaders) as response, open(
                'Uploaders', 'wb') as out_file:
            data = response.read()
            out_file.write(data)
