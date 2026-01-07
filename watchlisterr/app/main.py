import sys
import logging

# Force l'affichage des logs immédiatement
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
sys.stdout.reconfigure(line_buffering=True)

print("-------------------------------------------------------")
print("   WATCHLISTERR - DEMARRAGE DU SERVEUR                 ")
print("-------------------------------------------------------")