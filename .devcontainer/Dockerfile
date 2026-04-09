FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install Java, Maven, MySQL client
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk maven mysql-client \
    curl unzip git python3 python3-pip

# Install Flutter SDK
RUN curl -L https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.24.3-stable.tar.xz \
    -o /tmp/flutter.tar.xz && mkdir -p /opt && tar -xf /tmp/flutter.tar.xz -C /opt
ENV PATH="/opt/flutter/bin:${PATH}"

# Optional: install Gradle if needed
RUN apt-get install -y gradle

# Flutter + Android SDK dependencies
RUN apt-get update && apt-get install -y \
    wget unzip clang cmake ninja-build pkg-config libgtk-3-dev \
    google-chrome-stable

# Android SDK setup
RUN mkdir -p /opt/android-sdk/cmdline-tools && \
    cd /opt/android-sdk/cmdline-tools && \
    wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O tools.zip && \
    unzip tools.zip -d latest && rm tools.zip

ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH