FROM jenkins/inbound-agent:latest-jdk17

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    docker.io && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Fix permissions to allow jenkins user to use docker (simulated via TCP)
USER jenkins
