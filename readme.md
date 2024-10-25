docker exec -it mongodb mongorestore -u root -p `<mongodb-password> `--authenticationDatabase=admin --gzip --archive=./backups/initdata.gz

/c/codes/Antecedent/apps/dockerConfig
