import pandas as pd
import sys
sys.path.append('/Users/artbrare/Documents/Morant/py_morant/src')


from pymorant import llm # noqa

file_path = 'tests/k_escucha_muestra.xlsx'
openai_api_key = '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'
columna = 'body'
modelo = 'gpt-4'

# texto = "ola k ase, Jesú anda chanveando duro, te invitamos a la fiesta de cumpleaños de mi sobrino juan. Habrá muchos regalos"

# answer = llm.generar_categorias(texto, 2, modelo, openai_api_key)
# print(answer)