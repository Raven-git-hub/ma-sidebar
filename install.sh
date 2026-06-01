#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# MA Sidebar — installer
# Tested on Pop!_OS and Ubuntu (GNOME)
# ─────────────────────────────────────────────────────────────

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

info()    { echo -e "${BLUE}▸${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warn()    { echo -e "${YELLOW}⚠${NC} $1"; }
error()   { echo -e "${RED}✗${NC} $1"; }
header()  { echo -e "\n${BOLD}$1${NC}"; }

echo ""
echo -e "${BLUE}${BOLD}  MA Sidebar — Installer${NC}"
echo -e "  Music Assistant on your Linux desktop"
echo ""

header "Checking system"

if ! command -v apt &>/dev/null; then
    error "This installer requires apt (Debian/Ubuntu based distro)."
    exit 1
fi
success "apt found"

if ! command -v python3 &>/dev/null; then
    error "Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
success "Python $PYTHON_VERSION found"

header "Installing apt dependencies"

info "Running apt update..."
sudo apt update -qq

APT_PACKAGES=(
    python3-gi
    python3-gi-cairo
    gir1.2-ayatanaappindicator3-0.1
    libxcb-cursor0
)

for pkg in "${APT_PACKAGES[@]}"; do
    info "Installing $pkg..."
    sudo apt install -y "$pkg" -qq
    success "$pkg installed"
done

header "Installing Python dependencies"

info "Installing PyQt6..."
pip3 install PyQt6 PyQt6-WebEngine --user --quiet
success "PyQt6 installed"

header "Verifying Python modules"

check_import() {
    local module="$1"
    local label="$2"
    if python3 -c "import $module" &>/dev/null; then
        success "$label"
    else
        error "$label — import failed"
        return 1
    fi
}

check_import "gi"                                  "gi (GTK bindings)"
check_import "gi.repository.AyatanaAppIndicator3"  "AyatanaAppIndicator3"
check_import "PyQt6.QtWidgets"                     "PyQt6"
check_import "PyQt6.QtWebEngineWidgets"            "PyQt6 WebEngine"

header "Checking GNOME extensions"

INDICATOR_EXT="ubuntu-appindicators@ubuntu.com"

if command -v gnome-extensions &>/dev/null; then
    if gnome-extensions list --enabled 2>/dev/null | grep -q "$INDICATOR_EXT"; then
        success "AppIndicator extension is enabled"
    else
        warn "AppIndicator extension is not enabled."
        echo ""
        echo -e "  MA Sidebar needs this extension to show its tray icon."
        echo -e "  Enable it with:"
        echo -e "  ${BOLD}gnome-extensions enable $INDICATOR_EXT${NC}"
        echo -e "  Or install it from: https://extensions.gnome.org/extension/615/"
        echo ""
    fi
else
    warn "Could not check GNOME extensions (gnome-extensions not found)."
fi

header "Checking session type"

SESSION="${XDG_SESSION_TYPE:-unknown}"

if [ "$SESSION" = "x11" ]; then
    success "X11 session detected"
elif [ "$SESSION" = "wayland" ]; then
    warn "Wayland session detected."
    echo ""
    echo -e "  MA Sidebar works on Wayland via XWayland."
    echo -e "  Panel transparency is not supported on Wayland."
    echo ""
else
    warn "Could not detect session type."
fi

echo ""
echo -e "${GREEN}${BOLD}  Installation complete!${NC}"
echo ""
echo -e "  Run MA Sidebar with:"
echo -e "  ${BOLD}python3 src/main.py${NC}"
echo ""
echo -e "  On first launch you'll be walked through setup."
echo ""
