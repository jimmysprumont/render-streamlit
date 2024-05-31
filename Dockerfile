FROM python:3.12.0-slim

WORKDIR / app

COPY . / app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

# COMMANDES RUN COMBINES, BONNE PRATIQUE

RUN app-get update && apt-get install -y

# Supprimer les caches d'insatllations des packages
Run apt-get clean && rm -rf /var/lib/apt/lists/*

# Supprimer les fichhiers temporaires
Run rm -rf /tmp/*

# Supprimer les logs
Run rm -rf /var/log/*

CMD ['python3', 'main.py']

EXPOSE 8501

ENTRYPOINT ['streamlit', 'run', './app_streamlit.py', '--server.port=8501', '--server.address=0.0.0.0']