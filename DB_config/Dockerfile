FROM postgres:15

# Set environment variables
ENV POSTGRES_USER=chatbot_user
ENV POSTGRES_PASSWORD=chatbot_password
ENV POSTGRES_DB=chatbot_db

# Expose the PostgreSQL port
EXPOSE 5439

# Define the volume to persist data
VOLUME ["/h1/Anjul/times-ooh/chatbot-v1/DB_config"]

# The default command will run PostgreSQL
CMD ["postgres"]
