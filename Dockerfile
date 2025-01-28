#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\venv\Scripts\activate

#commando para criar uma imagem
#docker build -t meu_projeto .

#commando para Executar o Container
#docker run -d --name meu_projeto_container meu_projeto

# Usar a imagem base do Python
FROM python:3.12-slim

# Diretório de trabalho
WORKDIR /app

# Copiar os arquivos do projeto para o container
COPY . /app

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta (se necessário)
EXPOSE 5000

# Comando para executar o script
CMD ["python", "script.py"]
