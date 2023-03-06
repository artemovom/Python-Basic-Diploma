# Use the official Python image as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the working directory
COPY . .

# Install the application dependencies
RUN pip install -r requirements.txt

CMD ["python", "main.py"]

# Setting a port for your app communications with Telegram servers.
EXPOSE 80/tcp
