#!/bin/bash

echo "Starting HusnanAI..."

# Jalankan bot Python di background
python3 bot.py &

# Tunggu API Flask siap
sleep 10

# Jalankan WhatsApp Baileys
cd whatsapp
node index.js

wait
