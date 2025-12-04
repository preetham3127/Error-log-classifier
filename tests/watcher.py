"""
watcher.py

Simple file-watcher that reruns the analysis whenever the sample log changes.
Uses a polling loop (no external dependencies) so it works on plain Python.

Usage:
  python watcher.py            # runs and watches indefinitely (poll every 2s)
  python watcher.py --once     # run analysis once and exit
  python watcher.py -i 5       # poll every 5 seconds

"""