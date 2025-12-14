#!/bin/bash

echo "🔧 Updating system..."
sudo apt update -y
sudo apt install -y nodejs npm

echo "🔧 Fixing npm permissions..."
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
export PATH="$HOME/.npm-global/bin:$PATH"

# Add to shell
if ! grep -q "npm-global" ~/.bashrc; then
  echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
fi
source ~/.bashrc

echo "🌟 Installing Cline CLI..."
npm install -g @codeium/cline --registry=https://registry.npmjs.org/

echo "🔍 Checking installation..."
if command -v cline >/dev/null 2>&1; then
  echo "🎉 Cline installed successfully!"
  cline --help
else
  echo "❌ ERROR: Cline not found in PATH."
  echo "Run this manually: export PATH=\"\$HOME/.npm-global/bin:\$PATH\""
fi

