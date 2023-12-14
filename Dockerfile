# Dockerfile to create image with cron services
FROM ubuntu:latest
LABEL maintainer "@kuklobund"

#Install Cron
RUN apt-get update
RUN apt-get -y install cron python3 python3-pip run-one
RUN pip3 install requests influxdb-client

ARG cron_file_name

# Add the script to the Docker Image
COPY get_data.py /app/
# Copy hello-cron file to the cron.d directory
COPY cron_files/$cron_file_name /etc/cron.d/$cron_file_name
 
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/$cron_file_name

# Apply cron job
RUN crontab /etc/cron.d/$cron_file_name
 
# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Add the cron job
#RUN crontab -l | { cat; echo "*/10 * * * * run-one python3 /app/get_data.py"; } | crontab -

# Run the command on container startup
#CMD ["cron", "-f"]
CMD cron && tail -f /var/log/cron.log