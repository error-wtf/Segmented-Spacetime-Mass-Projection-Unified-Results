# Quick Fix für Linux-System (wo die Tests laufen)
# Option 1: System-wide install (falls root)
sudo apt install python3-pyarrow
# ODER mit pip:
pip install pyarrow>=10.0.0

# Option 2: Virtual Environment (EMPFOHLEN!)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest scripts/tests/test_ssz_invariants.py -v
