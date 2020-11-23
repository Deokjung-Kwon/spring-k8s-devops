FROM openjdk:8-jdk-alpine

EXPOSE 8080

VOLUME /logs

ARG JAR_FILE
COPY ${JAR_FILE} /app.jar

ENTRYPOINT ["java","-Djava.security.egd=file:/dev/./urandom","-jar","app.jar"]