FROM debian:bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends sasl2-bin \
 && rm -rf /var/lib/apt/lists/*

# test user — password is "testpass"
RUN useradd -m testuser && echo "testuser:testpass" | chpasswd

RUN mkdir -p /var/run/saslauthd

# -a pam  use PAM as the auth backend
# -d      foreground / debug
# -n 2    worker threads
CMD ["saslauthd", "-a", "pam", "-d", "-n", "2", "-m", "/var/run/saslauthd"]
