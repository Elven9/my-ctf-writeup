# Setup Mysql Docker Image
docker run --name mysql-lab -e MYSQL_ROOT_PASSWORD=password -p 3306:3306 -d mysql