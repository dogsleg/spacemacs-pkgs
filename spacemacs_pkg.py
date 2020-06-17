#!/usr/bin/python3
###############################################################################
# spacemacs-pkgs -- get a list of Emacs packages from Spacemacs and
# Doom Emacs source.
###############################################################################
# This script is written to help with packaging Emacs packages used in
# Spacemacs for Debian.
#
# See: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=828154e
###############################################################################
# Copyright (C) 2017-2020 Lev Lamberov <dogsleg@debian.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

import argparse
import glob
import os
import re
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime

from apt.debfile import DebPackage
from jinja2 import Environment, FileSystemLoader

from cache import Cache

__version__ = '0.1.2'


def strip_comments(strings):
    """
    Drop all comments.

    Input:  list of strings
    Output: list of string
    """
    comment = re.compile(r'\s*;;.*')
    result = []
    for i in strings:
        if not comment.match(i):
            result.append(i.strip())
    return result


def get_pkgs_list(names, path):
    """
    Return a list of dictionaries, each of which has a form
    {package_name: [layers]}.

    Input:  list of strings, string
    Output: dictionary or None
    """
    if not names:
        return None
    else:
        pkgs_list = dict()
        for pkg in names:
            pkgs_list[pkg] = '/'.join(path.split('/')[5:-1])
        return pkgs_list


def finalize_dict(lst, builtins):
    """
    Make flat dictionary a list of dictionaries and drop built-in packages.

    Input:  list of dictionaries, list of strings
    Output: dictionary
    """
    result = {}
    for dict_ in lst:
        if dict_:
            for k in dict_.keys():
                if k in builtins:
                    continue
                result[k] = dict_[k]
    return result


def prepare_sources(url, flavor):
    """
    Download and extract sources in the current directory.

    Input: string, string
    """
    if flavor == 'spacemacs':
        flavor = 'Spacemacs'
        filename = 'spacemacs.zip'
    else:
        flavor = 'Doom Emacs'
        filename = 'doomemacs.zip'
    print(f'Downloading {flavor} source...')
    with urllib.request.urlopen(url) as response, open(filename,
                                                       'wb') as out_file:
        data = response.read()
        out_file.write(data)
        with zipfile.ZipFile(filename) as zip_archive:
            print(f'Extracting {flavor} source...')
            zip_archive.extractall(path=tmpdirname)


def clean_pkg_emacsen_lst(lst):
    """
    Return a list with `dh-elpa`, `dh-make-elpa`, `*-doc` removed, and `elpa-`
    part stripped.

    Input:  list
    Output: list
    """
    clear_lst = []
    elpa = re.compile("elpa-.*")
    doc = re.compile(".*-doc")
    for i in lst:
        if i == 'dh-elpa' or i == 'dh-make-elpa' or doc.match(i):
            continue
        elif not elpa.match(i):
            clear_lst.append(i)
        else:
            clear_lst.append(i[5:])
    return clear_lst


def get_builtin():
    """
    Get the full package name of emacs-el in unstable, download it and get
    names of built-in packages.

    Output: list of strings
    """
    emacs_page = urllib.request.urlopen('https://packages.debian.org/sid/all/emacs-el/download').read().decode()
    emacs_pkgname = re.findall(r'(emacs-el_.+_all.deb)', emacs_page)[0]
    url = 'http://ftp.us.debian.org/debian/pool/main/e/emacs/' + emacs_pkgname
    print(f'Downloading {emacs_pkgname}...')
    with urllib.request.urlopen(url) as response, open(emacs_pkgname,
                                                       'wb') as out_file:
        data = response.read()
        out_file.write(data)
        emacs_package = DebPackage(emacs_pkgname)
        builtins = []
        for pkg in emacs_package.filelist:
            if '.el' in pkg:
                builtin = pkg.split('/')[-1]
                builtins.append(builtin.split('.')[0])
        return builtins


def get_packaged():
    """
    Generate a list of ELPA packages already in Debian.

    Output: list
    """
    if os.path.isfile('pkg-emacsen-addons'):
        with open('pkg-emacsen-addons') as f:
            packaged = f.read()[:-1].split('\n')
            return clean_pkg_emacsen_lst(packaged)
    else:
        sys.stdout.write("Please, generate pkg-emacsen-addons first.\n")
        sys.exit(1)


def traverse_dir(path):
    """
    Recursively walk through path and run parse functions to get package names.

    Input:  string
    Output: list
    """
    pkgs_in_layers = []
    for fname in glob.iglob(path, recursive=True):
        with open(fname) as f:
            content = f.read().split('\n')
        pkg_names = re.findall(r'\(use-package!?\s([\w-]+)',
                               '\n'.join(strip_comments(content)))
        pkgs_list = get_pkgs_list(pkg_names, fname)
        pkgs_in_layers.append(pkgs_list)
    return pkgs_in_layers


def combine_dicts(dict_fst, dict_snd):
    """
    Combine two dictionaries saving values as tuples.

    Input: dictionary, dictionary
    Output: list of dictionaries
    """
    combined = []
    for k in dict_fst:
        if k in dict_snd:
            combined.append({'pkg': k,
                             'status': 'todo',
                             'spacemacs': dict_fst[k],
                             'doomemacs': dict_snd[k]})
        else:
            combined.append({'pkg': k,
                             'status': 'todo',
                             'spacemacs': dict_fst[k],
                             'doomemacs': ''})
    for k in [key for key in set(dict_snd) - set(dict_fst)]:
        combined.append({'pkg': k,
                         'status': 'todo',
                         'spacemacs': '',
                         'doomemacs': dict_snd[k]})
    return combined


def mark_as_done(lst, packaged):
    done = 0
    for k in lst:
        if k['pkg'] in packaged:
            k['status'] = 'DONE'
            done += 1
    pkgs_sorted = sorted(lst, key=lambda k: k['pkg'])
    return (pkgs_sorted, done)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="output file")
    args = parser.parse_args()

    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    template = env.get_template('index.template')

    packaged = get_packaged()

    space_url = 'https://github.com/syl20bnr/spacemacs/archive/develop.zip'
    doom_url = 'https://github.com/hlissner/doom-emacs/archive/develop.zip'

    with tempfile.TemporaryDirectory() as tmpdirname:
        print('Created temporary directory:', tmpdirname)
        current_dir = os.getcwd()
        os.chdir(tmpdirname)
        builtins = get_builtin()
        prepare_sources(space_url, 'spacemacs')
        prepare_sources(doom_url, 'doomemacs')
        os.chdir(current_dir)

        space_path = tmpdirname + '/spacemacs-develop/layers/**/packages.el'
        doom_path = tmpdirname + '/doom-emacs-develop/modules/**/config.el'

        pkgs_in_space = finalize_dict(traverse_dir(space_path), builtins)
        pkgs_in_doom = finalize_dict(traverse_dir(doom_path), builtins)

    all_pkgs, done_pkgs = mark_as_done(combine_dicts(pkgs_in_space,
                                                     pkgs_in_doom), packaged)

    statistics = {'spacemacs': len(pkgs_in_space),
                  'doomemacs': len(pkgs_in_doom),
                  'done': done_pkgs}

    output = template.render(pkgs=all_pkgs,
                             statistics=statistics,
                             date=datetime.utcnow(),
                             version=__version__)

    if args.output:
        with open(args.output, 'w') as f:
            print(f'Writing output to {args.output}')
            f.write(output)
    else:
        print(output)
