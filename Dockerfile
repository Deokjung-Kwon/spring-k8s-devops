FROM openjdk:8-jdk-alpine

EXPOSE 8080

VOLUME /logs

#ARG name=webapp
ARG JAR_FILE
#ARG path=/apps

#RUN mkdir ${path}
#WORKDIR ${path}

#COPY ${JAR_FILE} ${path}/app.jar
COPY ${JAR_FILE} /app.jar

# add group and user
#RUN addgroup -g 1000 -S ${name} 
#RUN adduser -D -h "/home/${name}" -u 1000 -G ${name} -s /bin/bash ${name}

# add permission
#RUN chown -R 1000:1000 /logs
#RUN chown -R 1000:1000 ${path}

#ENTRYPOINT ["java","-Djava.security.egd=file:/dev/./urandom","-jar","${path}/app.jar"]
ENTRYPOINT ["java","-Djava.security.egd=file:/dev/./urandom","-jar","app.jar"]