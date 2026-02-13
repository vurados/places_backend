FROM jenkins/inbound-agent:latest-jdk17

USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    curl -L https://download.docker.com/linux/static/stable/x86_64/docker-26.1.4.tgz | tar -xz -C /tmp && \
    mv /tmp/docker/docker /usr/local/bin/docker && \
    rm -rf /tmp/docker && \
    apt-get purge -y curl && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Fix permissions to allow jenkins user to use docker (simulated via TCP)
USER jenkins
