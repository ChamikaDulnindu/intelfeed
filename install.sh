#!/bin/bash
# intelFEED.sh installer for Kali Linux
set -e

echo ""
echo "  ╔══════════════════════════════════╗"
echo "  ║      intelFEED.sh  installer     ║"
echo "  ╚══════════════════════════════════╝"
echo ""

INSTALL_DIR="$HOME/.local/share/intelfeed"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "[*] Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"

echo "[*] Installing Python dependencies..."
pip3 install feedparser --break-system-packages -q
echo "    ✓ feedparser installed"

echo "[*] Copying app files..."
cp intelfeed.py "$INSTALL_DIR/intelfeed.py"
chmod +x "$INSTALL_DIR/intelfeed.py"

# Create launcher script
cat > "$BIN_DIR/intelfeed" << 'EOF'
#!/bin/bash
python3 "$HOME/.local/share/intelfeed/intelfeed.py" "$@"
EOF
chmod +x "$BIN_DIR/intelfeed"

# Create .desktop file for app menu / right-click launch
cat > "$DESKTOP_DIR/intelfeed.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=intelFEED
Comment=Tech Intelligence Feed - Cyber, CTF, Web3, ML, Linux
Exec=$BIN_DIR/intelfeed
Icon=utilities-terminal
Terminal=false
Categories=Security;Network;News;
Keywords=security;hacking;ctf;web3;linux;ml;
StartupNotify=true
EOF

echo "    ✓ Launcher created at $BIN_DIR/intelfeed"
echo "    ✓ Desktop entry created"

# Add .local/bin to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "[!] $HOME/.local/bin is not in your PATH."
    echo "    Add this to your ~/.zshrc or ~/.bashrc:"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo ""
echo "  ╔══════════════════════════════════╗"
echo "  ║         Install complete!        ║"
echo "  ╚══════════════════════════════════╝"
echo ""
echo "  Run it:"
echo "    intelfeed          (from terminal)"
echo "    Applications menu → intelFEED"
echo ""
