#!/bin/bash
#
#    Freeze Kernel To Keep Our Basebox Functional After Update,
# if kernel is allowed to progress provider tools become unusable.
# A recompile of GuestAdditions is required, but as no mounts can
# take place this process can not be automated. Forcing A Static 
# kernel avoids these problems while allowing other packages to 
# progress. 
#

/bin/echo "linux-generic hold" | /usr/bin/dpkg --set-selections
/bin/echo "linux-image-generic hold" | /usr/bin/dpkg --set-selections
/bin/echo "linux-headers-generic hold" | /usr/bin/dpkg --set-selections
/bin/echo "linux-restricted-modules-generic hold" | /usr/bin/dpkg --set-selections

#for pkg in linux-image-generic linux-headers-generic linux-generic linux-restricted-modules-generic; do
#    /bin/echo "$pkg hold" | /usr/bin/dpkg --set-selections
#done
