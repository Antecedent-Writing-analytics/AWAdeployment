import re
import yaml
import requests
import xml.etree.ElementTree as ET
import time
import subprocess
import os

import secrets
import string


class ConfigAntecedent:
    def __init__(self):
        self.db_cache_size = 2
        self.REACT_APP_COLLABORA_HOST = (
            "https://editor.antecedentwriting.com/browser/9091043/cool.html?"
        )
        self.db_password = ""
        self.jwt_secret = ""
        self.hostname = ""
        self.db_pass = ""
        self.jwt_secret = ""
        self.ssl_email = ""
        self.discovery_url = "http://localhost/hosting/discovery"
        self.config = {
            "version": "3",
            "services": {},
            "volumes": {
                "certbot-etc": {"driver": "local"},
                "certbot-www": {"driver": "local"},
            },
        }

        self.volume_created = False
        self.smtp_host = ""
        self.smtp_user = ""
        self.smtp_password = ""
        self.smtp_port = 587
        self.forward_email = ""

    def __set_smtp_config(self):
        while True:
            self.smtp_host = input("Enter the SMTP host (e.g., smtp.gmail.com): ")
            if self.__validate_smtp_host(self.smtp_host):
                break  # Valid SMTP host, break out of loop
            else:
                print("Invalid SMTP host format. Please try again.")

        # Get SMTP user and validate it as an email

        while True:
            self.smtp_user = input("Enter the SMTP user (must be a valid email): ")
            if self.__validate_email(self.smtp_user):
                break  # Valid email, break out of loop
            else:
                print("Invalid email format for SMTP user. Please try again.")

        # Get SMTP password (must be provided by the user)
        while True:
            self.smtp_password = input("Enter the SMTP password: ")
            if self.smtp_password:
                break  # Continue only if password is not empty
            else:
                print("Password cannot be empty. Please enter a valid password.")

        # Get SMTP port, default to 587 if blank
        while True:
            smtp_port_input = input(
                "Enter the SMTP port (leave blank for default 587): "
            )
            if not smtp_port_input:
                self.smtp_port = 587
                break
            try:
                self.smtp_port = int(smtp_port_input)
                break  # Valid integer, break out of loop
            except ValueError:
                print("Invalid port. Please enter a valid number.")

        # Get forwarding email, default to smtp_user if blank
        self.forward_email = input(
            "Enter the forwarding email (leave blank to use SMTP user): "
        )
        if not self.forward_email:
            self.forward_email = self.smtp_user
        elif not self.__validate_email(self.forward_email):
            print(
                "Invalid email format for forwarding email. Using SMTP user as the forwarding email."
            )
            self.forward_email = self.smtp_user

        print(
            f"SMTP config set: user={self.smtp_user}, port={self.smtp_port}, forward_email={self.forward_email}"
        )

    # Helper method to validate email format
    def __validate_email(self, email):
        # Simple regex for email validation
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(pattern, email) is not None

    def __validate_smtp_host(self, host):
        pattern = r"^smtp\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, host) is not None

    def __update_server_name(self):
        # Read the Nginx config file
        with open("nginx-conf/ngconfig.conf", "r") as file:
            config = file.read()

        # Use a regex to replace the server_name line
        updated_config = re.sub(
            r"server_name\s+[\S]+;", f"server_name {self.hostname};", config
        )

        # Write the updated config back to the file
        with open("nginx-conf/ngconfig.conf", "w") as file:
            file.write(updated_config)

        print(f"Updated server_name to {self.hostname} in nginx-conf/ngconfig.conf")

    def __set_host_name(self):
        raw_hostname = input("Enter the hostname for the service: ")

        # Remove protocol (http:// or https://) using regex
        hostname = re.sub(r"^https?://", "", raw_hostname)

        # Remove trailing slash if it exists
        hostname = hostname.rstrip("/")

        # Set the processed hostname
        self.hostname = hostname

        print(f"Hostname set to: {self.hostname}")

    def __set_db_password(self):
        user_input = input(
            "Enter the database password (leave blank to generate one): "
        )

        # If the user input is blank, generate a random password
        if not user_input:
            characters = string.ascii_letters + string.digits
            self.db_password = "".join(
                secrets.choice(characters) for _ in range(12)
            )  # 12-character password
            print(f"Generated random password: {self.db_password}")
        else:
            self.db_password = user_input
            print("Database password set.")

    def __set_jwt_secret(self):
        user_input = self.jwt_secret = input(
            "Enter the JWT secret(Leave blank to generate automatically): "
        )

        # If the user input is blank, generate a random password
        if not user_input:
            characters = string.ascii_letters + string.digits
            self.jwt_secret = "".join(
                secrets.choice(characters) for _ in range(96)
            )  # 12-character password
            print(f"Generated random JWT: {self.jwt_secret}")
        else:
            self.jwt_secret = user_input
            print("Database password set.")

    def __config_step_one(self):
        service_config = {
            "webserver": {
                "image": "nginx:1.15.12-alpine",
                "container_name": "webserver",
                "restart": "unless-stopped",
                "ports": ["80:80"],
                "volumes": [
                    "./nginx-conf/:/etc/nginx/conf.d",
                    "certbot-etc:/etc/letsencrypt",
                    "certbot-www:/var/www/certbot",
                ],
            },
            "certbot": {
                "image": "certbot/certbot",
                "container_name": "certbot",
                "volumes": [
                    "certbot-etc:/etc/letsencrypt",
                    "certbot-www:/var/www/certbot",
                ],
                "command": f"certonly --webroot --webroot-path=/var/www/certbot --email {self.ssl_email} --agree-tos --no-eff-email -d {self.hostname}",
            },
            "COLLABORA": {
                "container_name": "collabora",
                "image": "collabora/code",
                "restart": "always",
                "ports": ["9980:9980"],
                "environment": {
                    "server_name": self.hostname,
                    "domain": f"https://{self.hostname}",
                },
                "env_file": ["./vars/.collabora.env"],
                "volumes": ["./python:/opt/collaboraoffice/share/Scripts/python"],
            },
        }
        self.config["services"].update(service_config)

    def __save_step_one(self):
        with open("docker-compose.yml", "w") as file:
            yaml.dump(self.config, file, default_flow_style=False)
        print("docker-compose.yml has been created!")

    def get_first_urlsrc(self):
        while True:
            try:
                # Make the request to the discovery URL
                response = requests.get(self.discovery_url)

                # Check if the request was successful
                if response.status_code == 200:
                    # Parse the XML content
                    root = ET.fromstring(response.content)

                    # Find the first 'action' element with a 'urlsrc' attribute
                    first_action = root.find(".//action[@urlsrc]")
                    if first_action is not None:
                        urlsrc = first_action.get("urlsrc")
                        print(f"Found urlsrc: {urlsrc}")
                        return urlsrc
                    else:
                        print("No 'urlsrc' found. Retrying...")
                else:
                    print(
                        f"Request failed with status code: {response.status_code}. Retrying..."
                    )

            except Exception as e:
                print(f"An error occurred: {str(e)}. Retrying...")

            # Wait for a bit before retrying
            time.sleep(5)

    def run_docker_compose(self):
        try:
            # Run the docker compose up -d command
            result = subprocess.run(
                ["docker", "compose", "up", "-d"],
                check=True,
                capture_output=True,
                text=True,
            )

            # Print the output
            print("Docker Compose Output:")
            print(result.stdout)

        except subprocess.CalledProcessError as e:
            # Print the error if the command fails
            print("An error occurred while running docker compose up:")
            print(e.stderr)

    def __config_step_two(self):
        service_config = {
            "webserver": {
                "image": "nginx:1.15.12-alpine",
                "container_name": "webserver",
                "restart": "unless-stopped",
                "ports": ["80:80"],
                "volumes": [
                    "./nginx-conf/:/etc/nginx/conf.d",
                    "certbot-etc:/etc/letsencrypt",
                    "certbot-www:/var/www/certbot",
                ],
            },
            "certbot": {
                "image": "certbot/certbot",
                "container_name": "certbot",
                "volumes": [
                    "certbot-etc:/etc/letsencrypt",
                    "certbot-www:/var/www/certbot",
                ],
                "command": f"certonly --webroot --webroot-path=/var/www/certbot --email {self.ssl_email} --agree-tos --no-eff-email -d {self.hostname}",
            },
            "COLLABORA": {
                "container_name": "collabora",
                "image": "collabora/code",
                "restart": "always",
                "ports": ["9980:9980"],
                "environment": {
                    "server_name": self.hostname,
                    "domain": f"https://{self.hostname}",
                },
                "env_file": ["./vars/.collabora.env"],
                "volumes": ["./python:/opt/collaboraoffice/share/Scripts/python"],
            },
            "mongodb": {
                "container_name": "mongodb",
                "image": "mongo",
                "restart": "always",
                "environment": {
                    "MONGO_INITDB_ROOT_USERNAME": "root",
                    "MONGO_INITDB_ROOT_PASSWORD": self.db_password,
                },
                "volumes": ["./mongo-data:/data/db", "./backups:/backups"],
                "command": f"mongod --wiredTigerCacheSizeGB {self.db_cache_size}",
            },
            "AWAWP": {
                "container_name": "awawp",
                "image": "awawp",
                "restart": "always",
                "env_file": ["./vars/.awawp.env"],
                "depends_on": ["mongodb"],
                "environment": {
                    "MONGO_SECRET": self.db_password,
                },
            },
            "ANTECEDENT": {
                "container_name": "antecedent",
                "image": "antecedent",
                "restart": "always",
                "ports": ["8080:8080"],
                "env_file": ["./vars/.antecedent.env"],
                "environment": {
                    "spring.data.mongodb.password": self.db_password,
                    "Antecedent.app.jwtSecret": self.jwt_secret,
                    "spring.mail.host": self.smtp_host,
                    "spring.mail.port": self.smtp_port,
                    "spring.mail.username": self.smtp_user,
                    "spring.mail.password": self.smtp_password,
                    "Antecedent.app.Email.From": self.forward_email,
                    "Antecedent.app.ui": f"https://{self.hostname}/",
                    "Antecedent.app.url": f"https://{self.hostname}/",
                },
                "depends_on": ["mongodb"],
            },
            "AWAUI": {
                "container_name": "awaui",
                "image": "awaui",
                "restart": "always",
                "ports": ["3000:3000"],
                "env_file": ["./vars/.awaui.env"],
                "environment": {
                    "REACT_APP_API_URL": f"http://{self.hostname}",
                    "REACT_APP_COLLABORA_HOST": self.REACT_APP_COLLABORA_HOST,
                    "REACT_APP_EDITOR_URL": f"{self.REACT_APP_COLLABORA_HOST}WOPISrc=http://{self.hostname}/wopi/files/",
                    "REACT_APP_INS_EDITOR_URL": f"{self.REACT_APP_COLLABORA_HOST}WOPISrc=http://{self.hostname}/wopi/files/",
                    "REACT_APP_EDU_EDITOR_URL": f"{self.REACT_APP_COLLABORA_HOST}WOPISrc=http://{self.hostname}/shadow/wopi/files/",
                    "REACT_APP_ADMIN_EDITOR_URL": f"{self.REACT_APP_COLLABORA_HOST}WOPISrc=http://{self.hostname}/admin/wopi/files/",
                    "REACT_APP_PEERREVIEW": f"{self.REACT_APP_COLLABORA_HOST}WOPISrc=http://{self.hostname}/review/wopi/files/",
                },
            },
            "spellcheck": {
                "container_name": "spellcheck",
                "image": "collabora/languagetool",
                "restart": "unless-stopped",
            },
        }
        self.config["services"].update(service_config)

    def __save_step_two(self):
        with open("docker-compose.yml", "w") as file:
            yaml.dump(self.config, file, default_flow_style=False)
        print("docker-compose.yml has been created!")

    def __add_volume_directory(self):

        folder_path = "./mongo-data"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Folder '{folder_path}' created.")
            self.volume_created = True
        else:
            print(f"Folder '{folder_path}' already exists.")

    def __ask_db_cache_size(self):
        while True:
            cache_size = input(
                "Enter the database cache size (GB, leave blank for default 2GB): "
            )
            if not cache_size:
                return

            try:
                # Try to convert the input to a float
                self.db_cache_size = float(cache_size)
                return
            except ValueError:
                print("Invalid input. Please enter a numeric value (e.g., 2 or 2.5).")

    def __db_restore(self):
        try:
            # Run the docker compose up -d command
            if self.volume_created:
                command = [
                    "docker",
                    "compose",
                    "exec",
                    "-it",
                    "mongodb",
                    "mongorestore",
                    "-u",
                    "root",
                    "-p",
                    self.db_password,
                    "--authenticationDatabase=admin",
                    "--gzip",
                    "--archive=./backups/initdata.gz",
                ]

                # Run the command
                result = subprocess.run(command)

                # Print the output
                print("Docker Compose Output:")
                print(result.stdout)

        except subprocess.CalledProcessError as e:
            # Print the error if the command fails
            print("An error occurred while running docker compose up:")
            print(e.stderr)

    def _set_nginx(self, step=1):
        destination = "./nginx-conf/ngconfig.conf"
        source = "./webconfigs/step2.conf"
        if step == 1:
            source = "./webconfigs/step1.conf"
        with open(source, "rb") as src_file:
            with open(destination, "wb") as dest_file:
                # Copy the file content
                dest_file.write(src_file.read())
        print(f"File copied from {source} to {destination}.")

    def __set_ssl_email(self):
        while True:
            self.ssl_email = input("Enter email for SSl certificate: ")
            if self.__validate_email(self.ssl_email):
                break  # Valid SMTP host, break out of loop
            else:
                print("Invalid email format. Please try again.")

    def __rest_webserver(self):
        print("Restart webserver:")
        command = ["docker", "compose", "restart", "webserver", "--no-deps"]
        result = subprocess.run(command)

                # Print the output
        print("Docker restart Output:")
        print(result.stdout)

    def configure(self):
        # Set up nginx config
        self.__set_host_name()
        self._set_nginx(1)
        self.__update_server_name()
        # Config docker file
        self.__set_ssl_email()
        self.__config_step_one()

        # create step one docker file
        self.__save_step_one()
        self.run_docker_compose()

        self.REACT_APP_COLLABORA_HOST = self.get_first_urlsrc()
        self.__set_db_password()
        self.__set_jwt_secret()
        # create step one docker file
        self._set_nginx(2)
        self.__update_server_name()
        self.__add_volume_directory()
        self.__ask_db_cache_size()
        self.__set_smtp_config()
        # Generate config of step 2
        self.__config_step_two()
        self.__save_step_two()

        self.run_docker_compose()
        time.sleep(10)
        self.__db_restore()
        time.sleep(10)
        self.__rest_webserver()
