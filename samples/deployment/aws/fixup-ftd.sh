#!/bin/sh

pre_install() {
    sudo apt-get update 2>&1
    sudo apt-get install -y qemu parted gnu-fdisk gddrescue 2>&1
    touch /mnt/fixup_pre_done
    
}

do_install() {
    #sudo qemu-img convert -O raw /mnt/image.qcow2 /dev/xvdc 2>&1
    #this is 90% faster, but less tested, should be fine
    qemu-img convert -O raw /mnt/image.qcow2 /mnt/image.raw 2>&1
    dd conv=sparse if=/mnt/image.raw of=/dev/xvdc bs=1M 2>&1
    sync
    sleep 30
    touch /mnt/fixup_install_done
}

post_install() {
    sudo mkdir /aaa 2>&1
    sudo partprobe 2>&1
    sudo mount /dev/xvdc6 /aaa 2>&1
    sudo cat /aaa/etc/shadow | awk 'BEGIN {OFS=FS=":"};/^admin/{printf $1FS"!"FS; for(i=3;i<NF;i++) printf $i FS;print NL};!/^admin/{print}' > /aaa/etc/shadow2
    sudo mv /aaa/etc/shadow2 /aaa/etc/shadow 2>&1
    sudo chown root:root /aaa/etc/shadow 2>&1
    sudo chmod 440 /aaa/etc/shadow 2>&1
    sudo umount /aaa 2>&1
    sync
    touch /mnt/fixup_post_done
}



case "$1" in
'preinstall')
  pre_install
  ;;
'doinstall')
  do_install
  ;;
'postinstall')
  post_install
  ;;
*)
esac

