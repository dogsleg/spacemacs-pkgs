# spacemacs-pkgs

This script is written to help with packaging Emacs packages used in Spacemacs and Doom Emacs for Debian. It downloads zip files with the current develop branches of Spacemacs and Doom Emacs to a temrorary directory, scans the source code and outputs HTML file with the list of packages and their status:

Homepage: https://salsa.debian.org/dogsleg/spacemacs-pkgs

For motivation, see: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=828154

## Usage

1. Make sure that unstable/sid is in your `/etc/apt/sources.list`. Your `/etc/apt/sources.list` should contain something like as follows: `deb [arch=amd64,i386] https://deb.debian.org/debian unstable main`
2. Update your packages list: `sudo aptitude update`
3a. Generate list of Emacs packages in Debian, which are maintained by Debian Emacsen team: `aptitude search '?maintainer(pkg-emacsen-addons~|debian-emacsen) !?description(Transition)' -F "%p" > pkg-emacsen-addons`
3b. Alternatively, generate list of ELPA packages in Debian: `apt-cache search ^elpa- | cut --delimiter=' ' -f 1 > pkg-emacsen-addons` (should be elpa-packages)
4. Run the script: `./spacemacs_pkg.py
