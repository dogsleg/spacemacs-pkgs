# spacemacs-pkgs

This script is written to help with packaging Emacs packages used in Spacemacs for Debian.

See: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=828154

To generate pkg-emacsen-addons first update a package list (make sure that unstable/sid is in your `/etc/apt/sources.list`) with `aptitude update`, then use the following command:

`aptitude search '?maintainer(pkg-emacsen-addons) !?description(Transition)' -F "%p" > pkg-emacsen-addons`
