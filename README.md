# spacemacs-pkgs

This script is written to help with packaging Emacs packages used in Spacemacs and Doom Emacs for Debian. It downloads zip files with the current develop branches of Spacemacs and Doom Emacs to a temrorary directory, scans the source code and outputs DSV list of the following form:

```
[[!table  data="""
Package|Packaged by pkg-emacsen-addons?|Spacemacs|Doom Emacs
vmd-mode|todo|+lang/markdown|
volatile-highlights|todo|+spacemacs/spacemacs-editing-visual|ui/ophints
xref-js2|todo||lang/javascript
"""]]
```

Homepage: https://salsa.debian.org/dogsleg/spacemacs-pkgs

For motivation, see: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=828154

## Usage

1. Make sure that unstable/sid is in your `/etc/apt/sources.list`. Your `/etc/apt/sources.list` should contain something like as follows: `deb [arch=amd64,i386] https://deb.debian.org/debian unstable main`
2. Update your packages list: `sudo aptitude update`
3. Generate list of Emacs packages in Debian, which use dh-elpa: `aptitude search '?maintainer(pkg-emacsen-addons~|debian-emacsen) !?description(Transition)' -F "%p" > pkg-emacsen-addons`
4. Run the script: `./spacemacs_pkg.py
