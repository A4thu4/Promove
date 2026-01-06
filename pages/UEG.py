import streamlit as st
import sys
import os

# Isso garante que o Python encontre os arquivos dentro da pasta Sistema_A
sys.path.append(os.path.abspath("sistema_ueg"))

# Importa a função principal do seu app original
# Supondo que seu app original tenha uma função chamada 'main' ou 'run'
from sistema_ueg.main import main 

if __name__ == "__main__":
    main()