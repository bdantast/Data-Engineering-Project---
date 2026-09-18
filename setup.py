import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Instalando dependencias...")
os.system(f"{sys.executable} -m pip install -r requirements.txt")
print("Dependencias instaladas!")
print()
print("Para configurar:")
print("1. Copie .env.example para .env")
print("2. Configure sua senha do Neon Tech no .env")
print("3. Configure sua API key do Groq (gratuita) no .env")
print()
print("Para executar:")
print(f"  {sys.executable} main.py")
print()
