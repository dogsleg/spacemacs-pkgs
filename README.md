# spacemacs-pkgs

This script is written to help with packaging Emacs packages used in Spacemacs for Debian. It scans Spacemacs source code and outputs DSV list of the following form:

[[!table  data="""
Package|Packaged by pkg-emacsen-addons?|Layers
zonokai-theme|todo|+themes/themes-megapack
"""]]

Homepage: https://pkg-emacsen.alioth.debian.org/spacemacs/

For motivation, see: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=828154

## Usage

0. Make sure that you have up-to-date Spacemacs source code
1. Make sure that unsable/sid is in your `/etc/apt/sources.list`. Your `/etc/apt/sources.list` should contain something like as follows: `deb [arch=amd64,i386] https://deb.debian.org/debian unstable main`
2. Update your packages list: `sudo aptitude update`
3. Generate list of Emacs packages in Debian, which use dh-elpa: `sudo aptitude search '?maintainer(pkg-emacsen-addons) !?description(Transition)' -F "%p" > pkg-emacsen-addons`
4. Run the script with path to Spacemacs source code as an argument: `./spacemacs_pkg.py ../spacemacs/`
