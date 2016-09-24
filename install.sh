#!/bin/bash
mkdir -p ~/.config/stay-dry ~/.local/share/stay-dry/tones ~/.local/share/stay-dry/logs
cp -r stay-dry.py tones ~/.local/share/stay-dry
if [ -e ~/.config/stay-dry/config ]; then
    echo "Existing config file found: not replaced"
else
    cp config ~/.config/stay-dry/
fi
echo "Installed successfully."
