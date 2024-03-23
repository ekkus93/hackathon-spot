# Use a base image with necessary dependencies
FROM ghcr.io/merklebot/hackathon-arm-image:master as build

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone AprilTag repository
#WORKDIR /usr/src
#RUN git clone git@github.com:ekkus93/apriltag.git

# Build AprilTag library
#WORKDIR /usr/src/apriltag
#RUN cmake -B build -DCMAKE_BUILD_TYPE=Release
#RUN cmake --build build --target install

# Install Python bindings (optional)
# WORKDIR /usr/src/apriltag/python
# RUN python3 setup.py install

# Copy your application code
WORKDIR /app
COPY . .

# Install Python dependencies
RUN python3.8 -m pip install -r requirements.txt

RUN cd apriltag-master && make -B build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build --target install \\
    && python3 setup.py install

# Command to run your application
CMD ["python3.8", "main.py"]
