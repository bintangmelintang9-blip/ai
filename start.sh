#!/bin/bash

python3 bot.py &
sleep 5

cd whatsapp
node index.js

wait
