#!/bin/bash
rm -rf ~/.local/share/stay-dry ~/.config/stay-dry
mkdir -p ~/.config/stay-dry ~/.local/share/stay-dry/tones ~/.local/share/stay-dry/logs
cp -r stay-dry.py tones ~/.local/share/stay-dry
cp config ~/.config/stay-dry
echo "Installed successfully."
