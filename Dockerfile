FROM kalilinux/kali-rolling

LABEL maintainer="muhammed.m.abdelkader@gmail.com"
LABEL description="Docker image for passive reconnaissance tools"

ENV DEBIAN_FRONTEND=noninteractive

# Install tools and dependencies
RUN apt update && apt install -y \
    curl \
    git \
    python3-pip \
    jq \
    dnsutils \
    whois \
    amass \
    subfinder \
    assetfinder \
    theharvester \
    recon-ng \
    && apt clean && rm -rf /var/lib/apt/lists/*

# Install Sublist3r
RUN git clone https://github.com/aboul3la/Sublist3r.git /opt/Sublist3r && \
    pip3 install -r /opt/Sublist3r/requirements.txt && \
    ln -s /opt/Sublist3r/sublist3r.py /usr/local/bin/sublist3r

# Create and set data directory
#RUN mkdir /data
#WORKDIR /data

# Install Python API server deps
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

# Copy API code
COPY app /app
WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

#CMD ["/bin/bash"]
