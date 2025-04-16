# FROM python:3.10-slim

# WORKDIR /app

# COPY . /app

# RUN pip install --no-cache-dir -r requirements.txt

# # Install additional libraries
# RUN pip install --no-cache-dir torch transformers numpy psycopg2-binary pytubefix yt_dlp

# # Create directories for videos and reels if they don't exist
# # RUN mkdir -p /app/videos/reels

# EXPOSE 3100

# ENV NAME content_repurposing_system

# CMD ["python", "app.py"]

FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Install additional libraries
RUN pip install --no-cache-dir numpy pandas

# Define the volume
VOLUME ["/h1/Anjul/times-ooh/chatbot-v1"]


# Add /app to PYTHONPATH
ENV PYTHONPATH=/app

EXPOSE 2150

# CMD ["python", "application/inference.py"]
# CMD ["python", "app.py"]

# Set default shell to bash
SHELL ["/bin/bash", "-c"]

# Keep the container running for manual work
CMD ["sleep", "infinity"]

