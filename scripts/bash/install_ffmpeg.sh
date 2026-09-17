#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

platform="$(bash "$SCRIPT_DIR/platform.sh")"

install_ffmpeg() {
    local pkg_mngr="$1"
    local dep=()
    local up=""
    local install=""

    # Already installed?
    if command -v ffmpeg >/dev/null 2>&1; then
        echo "ffmpeg already installed."
        return 0
    fi

    case "$pkg_mngr" in
        deb/ubu)
            up="sudo apt update -y"
            install="sudo apt install -y ffmpeg"
            ;;
        fedora)
            echo "fedora does not include ffmpeg in its default repos. To install, RPM Fusion must be enabled."
            echo "if RPM Fusion is already enabled, nothing will happen."
            read -rp "continue (y/n)? " answer
            [[ "$answer" == "y" ]] || return 0
            dep+=("sudo dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-\$(rpm -E %fedora).noarch.rpm")
            install="sudo dnf install -y ffmpeg"
            ;;
        rhel)
            echo "RHEL based distro do not include ffmpeg in its default repos. To install, RPM Fusion must be enabled."
            echo "if RPM Fusion is already enabled, nothing will happen."
            read -rp "continue (y/n)? " answer
            [[ "$answer" == "y" ]] || return 0
            dep+=("sudo dnf install -y --nogpgcheck https://download1.rpmfusion.org/free/el/rpmfusion-free-release-\$(rpm -E %rhel).noarch.rpm")
            dep+=("sudo dnf install -y --nogpgcheck https://download1.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-\$(rpm -E %rhel).noarch.rpm")
            install="sudo dnf install -y ffmpeg"
            ;;
        arch)
            install="sudo pacman -S --noconfirm ffmpeg"
            ;;
        suse)
            install="sudo zypper install -y ffmpeg"
            ;;
        mac)
            if ! command -v brew >/dev/null 2>&1; then
                echo "Homebrew is not installed. Install it first:"
                echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                return 1
            fi
            install="brew install ffmpeg"
            ;;
        *)
            echo "unsupported platform. cannot auto-install ffmpeg."
            return 1
            ;;
    esac

    echo "the following commands will be executed:"
    if [[ ${#dep[@]} -gt 0 ]]; then
        printf '  %s\n' "${dep[@]}"
    fi
    [[ -n "$up" ]]      && echo "  $up"
    [[ -n "$install" ]] && echo "  $install"

    read -rp "continue (y/n)? " answer
    [[ "$answer" == "y" ]] || return 0

    for cmd in "${dep[@]}"; do
        eval "$cmd"
    done

    [[ -n "$up" ]]      && eval "$up"
    [[ -n "$install" ]] && eval "$install"
}

main() {
    local pkg_mngr="${1:-}"
    if [[ -z "$pkg_mngr" ]]; then
        pkg_mngr="${platform}"
        echo "detected platform: $pkg_mngr"
    fi
    install_ffmpeg "$pkg_mngr"

    read -n 1 -s -r -p "installion complete. press any key to continue..."
    echo ""
    return 0
}

main "$@"