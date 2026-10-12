FROM ubuntu:22.04 
LABEL maintainer="Tim Chaubet"
VOLUME ["/mnt/vrising/server", "/mnt/vrising/persistentdata"]

ARG DEBIAN_FRONTEND="noninteractive"
RUN apt update -y && \
    apt-get upgrade -y && \
    apt-get install -y  apt-utils && \
    apt-get install -y  software-properties-common \
                        tzdata && \
    add-apt-repository multiverse && \
    dpkg --add-architecture i386 && \
    apt update -y && \
    apt-get upgrade -y 
RUN useradd -m steam && cd /home/steam && \
    echo steam steam/question select "I AGREE" | debconf-set-selections && \
    echo steam steam/license note '' | debconf-set-selections && \
    apt purge steam steamcmd && \
    apt install -y gdebi-core  \
                   libgl1-mesa-glx:i386 \
                   wget && \
    apt install -y steam \
                   steamcmd && \
    ln -s /usr/games/steamcmd /usr/bin/steamcmd

# Swapped out winetricks for cabextract
RUN apt install -y wine \
                   winbind \
                   cabextract \
                   xserver-xorg \
                   xvfb \
                   jq

# --- V RISING 1.0 MODDING SUPPORT ---
# Fetch the latest winetricks to support modern .NET
RUN wget https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks -O /usr/local/bin/winetricks && \
    chmod +x /usr/local/bin/winetricks

RUN mkdir -p /home/steam/.wine && chown -R steam:steam /home/steam/.wine
USER steam
ENV WINEPREFIX=/home/steam/.wine
ENV WINEARCH=win64
RUN wineboot -u && winetricks -q dotnet6
USER root
# ------------------------------------

RUN rm -rf /var/lib/apt/lists/* && \
    apt clean && \
    apt autoremove -y

COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
