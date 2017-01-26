#!/usr/bin/python3
################################################################################
# spacemacs-pkgs -- get a list of Emacs packages from Spacemacs source.
################################################################################
# This script is written to help with packaging Emacs packages used in
# Spacemacs for Debian.
#
# See: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=828154
################################################################################
# Copyright (C) 2017 Lev Lamberov
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
################################################################################

__version__ = '0.0.1'

import re

def count_parens(string):
    """
    Return a spread between open and close parens in a given string.

    Input:  string
    Output: integer
    """
    parens = 0
    for c in string:
        if c == '(':
            parens += 1
        elif c == ')':
            parens -= 1
    return parens

def strip_comments(strings):
    """
    Return all the strings except comment lines.

    Input:  list of strings
    Output: list of strings
    """
    comment = re.compile("\s*;;.*")
    result = []
    for i in strings:
        if not comment.match(i):
            result.append(i.strip())
    return result

def get_pkg_declaration(strings):
    """
    Return a list containing a packages declaration.

    Input:  list of strings
    Output: list of strings
    """
    pkgs_list = re.compile("\(setq [a-z\-]+-package.*")
    pkg_declaration = []
    started = 0
    parens_balance = 0
    for i in strip_comments(content):
        if pkgs_list.match(i):
            started = 1
        if started:
            pkg_declaration.append(i)
            parens_balance += count_parens(i)
            if not parens_balance:
                break
    return pkg_declaration

def check_built_in(string):
    """
    Return True if a package in a given string is built-in, False otherwise.

    Input:  string
    Output: boolean
    """
    if ':location built-in' in string:
        built_in = True
    else:
        built_in = False
    return built_in

def get_layer(path):
    """
    Return layer name (e. g. '+emacs/org').

    Input:  string
    Output: string
    """
    path_lst = path.split('/')
    c = 0
    while c < len(path_lst):
        if '+' in path_lst[c]:
            return "/".join(path_lst[c:-1])
        c += 1

def parse_complex_pkgs_list(string, path):
    """
    Return a dictionary with package name as a key and a list containing
    boolean representing built-in status and layer name as the key's value.

    Input:  string, string
    Output: dictionary
    """
    return {string.split()[0].strip('('):
            [check_built_in(string), get_layer(path)]}

def get_pkgs_list(strings, path):
    """
    Return a list of dictionaries, each of which has a form
    {package_name: [built-in_status, layer]}.

    Input:  list of strings, string
    Output: list of dictionaries
    """
    if len(strings) == 1:
        return [{strings[0][strings[0].find("'"):].strip("'()"):
                [check_built_in(strings), get_layer(path)]}]
    else:
        pkgs_list = []
        multiline = ''
        alpha = re.compile("[a-z0-9\-]")
        for i in strings[2:-1]:
            if alpha.match(i[0]):
                pkgs_list.append(parse_complex_pkgs_list(i, path))
            if i[0] == '(' and not count_parens(i):
                pkgs_list.append(parse_complex_pkgs_list(i, path))
            if i[0] == '(' and count_parens(i):
                multiline += i
            elif multiline and count_parens(i):
                multiline += ' ' + i
                pkgs_list.append(parse_complex_pkgs_list(multiline, path))
                multiline = ''
            elif multiline:
                multiline += ' ' + i
        return pkgs_list

def flat_list(lst):
    """
    Return flat dictionary produced from a list of lists of dictionaries.
    Duplicates are cleverly removed.

    Input:  list
    Output: dictionary
    """
    result = {}
    keys_in_result = []
    for sublst in lst:
        if sublst:
            for item in sublst:
                pkg = list(item.keys())[0]
                if pkg in keys_in_result:
                    result[pkg] = [result[pkg][0] or item[pkg][0],
                                   result[pkg][1] + ', ' + item[pkg][1]]
                else:
                    keys_in_result.append(pkg)
                    result = {**result, **item}
    return result


if __name__ == '__main__':
    import argparse
    import glob

    # Parsing command-line arguments
    cl_parser = argparse.ArgumentParser(description='Get a list of Emacs \
                                        packages from Spacemacs source.')
    cl_parser.add_argument('path', help='path to Spacemacs source code')
    args = cl_parser.parse_args()

    path = args.path + 'layers/**/packages.el'
    pkgs_in_layers = []
    for fname in glob.iglob(path, recursive=True):
        with open(fname) as f: content = f.read().split('\n')
        pkg_declaration = get_pkg_declaration(strip_comments(content))
        pkgs_list = get_pkgs_list(pkg_declaration, fname)
        pkgs_in_layers.append(pkgs_list)

    all_pkgs = flat_list(pkgs_in_layers)
    print('[[!table  data="""')
    print('Package|Built-in|Layers')
    for item in sorted(list(all_pkgs)):
        print(item + '|' + str(all_pkgs[item][0]) + '|' + all_pkgs[item][1])
    print('"""]]')
