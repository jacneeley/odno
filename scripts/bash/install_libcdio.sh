#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

platform="$(bash "$SCRIPT_DIR/platform.sh")"

install_libcdio(){
    local pkg_mngr="$1"
    local install=()
    case "$pkg_mngr" in 
        deb/ubu)
            install+=("sudo apt install python-dev-is-python3")
            install+=("sudo apt install libcdio-dev")
            install+=("sudo apt install libiso9660-dev")
            install+=("sudo apt install swig pkg-config")
            ;;
        fedora)
            install+=("sudo dnf install python3-devel libcdio-devel libiso9660-devel swig pkgconf")
            ;;
        rhel)
            install=("sudo dnf install python3-devel libcdio-devel libiso9660-devel swig pkgconf")
            ;;
        arch)
            install=("sudo pacman -S python libcdio swig pkgconf")
            ;;
        suse)
            install=("sudo zypper install python3-devel libcdio-devel libiso9660-devel swig pkg-config")
            ;;
        mac)
            if ! command -v brew >/dev/null 2>&1; then
                echo "Homebrew is not installed. Install it first:"
                echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                return 1
            fi
            install+=("brew install python libcdio swig pkg-config")
            ;;
        *)
            echo "unsupported platform"
            echo "try installing dependencies manually or building from source"
            echo "for more visit: https://pypi.org/project/pycdio/"
            return 1
            ;;   
    esac

    echo "the following will be installed:"
    if [[ ${#install[@]} -gt 0 ]]; then
        printf '    %s\n' "${install[@]}"
    fi

    read -rp "continue (y/n)?" ans
    [[ "$ans" == "y" ]] || return 0

    for cmd in "${install[@]}"; do
        eval "$cmd"
    done
}

main () {
    local pkg_mngr="${1:-}"
    if [[ -z "$pkg_mngr" ]]; then
        pkg_mngr="${platform}"
        echo "detected platform: $pkg_mngr"
    fi

    install_libcdio "$pkg_mngr"

    read -n 1 -s -r -p "installation complete. press any key to continue..."
    echo ""
    return 0

}

main "$@"
