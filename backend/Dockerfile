FROM eclipse-temurin:23-jdk AS builder
RUN apt-get update && \
    apt-get install -y curl unzip && \
    curl -fsSL https://downloads.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.zip -o maven.zip && \
    unzip maven.zip -d /opt && \
    ln -s /opt/apache-maven-3.9.6 /opt/maven && \
    ln -s /opt/maven/bin/mvn /usr/bin/mvn

ENV MAVEN_HOME=/opt/maven
ENV PATH=$MAVEN_HOME/bin:$PATH

WORKDIR /app
COPY mvnw pom.xml ./
RUN chmod +x mvnw
COPY .mvn .mvn
RUN mvn dependency:go-offline -B
COPY src src
RUN mvn package -DskipTests -B

FROM eclipse-temurin:23-jdk
WORKDIR /app
RUN mkdir -p /logs
VOLUME /logs
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENV LOG_PATH=/logs/backend.log
ENTRYPOINT ["sh", "-c", "java -Dlogging.file.name=${LOG_PATH} -jar /app/app.jar"]
