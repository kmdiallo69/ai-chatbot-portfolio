# Use the official PostgreSQL image as base
FROM postgres:15

# Set environment variables
ENV POSTGRES_DB=chatbot
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_HOST_AUTH_METHOD=trust

# Copy initialization script
COPY init.sql /docker-entrypoint-initdb.d/

# Create a healthcheck
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD pg_isready -U postgres || exit 1

# Expose PostgreSQL port
EXPOSE 5432

# The postgres image already has the correct entrypoint
# so we don't need to specify a CMD 