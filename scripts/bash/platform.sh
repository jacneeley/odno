#!/usr/bin/env bash

detect_platform() {
    # Returns one of: deb/ubu, fedora, rhel, arch, suse, mac, unknown
    local uname_s
    uname_s="$(uname -s)"

    case "$uname_s" in
        Darwin)
            echo "mac"
            return 0
            ;;
        Linux)
            ;;
        *)
            echo "unknown"
            return 0
            ;;
    esac

    if [[ -r /etc/os-release ]]; then
        . /etc/os-release
        local id_like=" ${ID_LIKE:-} "
        case " ${ID:-} " in
            *" debian "*|*" ubuntu "*|*" linuxmint "*|*" pop "*|*" elementary "*)
                echo "deb/ubu"; return 0 ;;
            *" fedora "*)
                echo "fedora"; return 0 ;;
            *" rhel "*|*" centos "*|*" rocky "*|*" alma "*)
                echo "rhel"; return 0 ;;
            *" arch "*|*" manjaro "*|*" endeavouros "*)
                echo "arch"; return 0 ;;
            *" opensuse "*|*" suse "*|*" sles "*)
                echo "suse"; return 0 ;;
        esac
        case "$id_like" in
            *" debian "*|*" ubuntu "*) echo "deb/ubu"; return 0 ;;
            *" fedora "*|*" rhel "*)   echo "fedora"; return 0 ;;
            *" arch "*)                echo "arch";   return 0 ;;
            *" suse "*|*" opensuse "*) echo "suse";   return 0 ;;
        esac
    fi

    if command -v apt >/dev/null 2>&1;   then echo "deb/ubu"; return 0; fi
    if command -v dnf >/dev/null 2>&1;   then echo "fedora";  return 0; fi
    if command -v pacman >/dev/null 2>&1; then echo "arch";   return 0; fi
    if command -v zypper >/dev/null 2>&1; then echo "suse";   return 0; fi

    echo "unknown"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    detect_platform
fi
