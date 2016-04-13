@echo off
set DBNAME=leds
set DBHOST=localhost
set DBPASS=
set DBUSER=
@echo on
start python main.py
cd webapp\TonsleyLED\tonsleyled
start pserve production.ini