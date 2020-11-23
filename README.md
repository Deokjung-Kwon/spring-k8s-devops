# spring-k8s-devops
Pre-project for kakaopay
DevOps 포지션 사전과제로 진행합니다. 

## Project Info
웹 어플리케이션 [spring-petclinic-data-jdbc](https://github.com/spring-petclinic/spring-petclinic-data-jdbc)을 Kubernetes환경에서 실행하고자 합니다
* 다음의 요구사양에 부합하도록 빌드 스크립트, 어플리케이션 코드 등을 작성하십시오.
* K8S에 배포하기 위한 manifest 파일을 작성하십시오

## Test Environment
* OS: Windows 10
* K8S: Docker Desktop Community 2.3.0.3
 * Engine: 19.03.8
 * Kubernetes: v1.16.5
* JAVA: OpenJDK 1.8.0.275-1
* IDE: VisualStudio Code
* Builder: Gradle 6.7.1
* SCM: Git-2.29.164-bit
* Python 3.7.6

## 실행 방법
### Project Download
```
> git clone https://github.com/Deokjung-Kwon/spring-k8s-devops.git
```

### Build project
```
> cd spring-k8s-devops
> python ./manage.py build
```

### Deplay
모든 서비스 배포
```
> python ./manage.py deplay_all
```

app만 배포
```
> python ./manage.py deplay_app
```

App container 순차적 재실행
```
> python ./manage.py restart_app
```

### Scale In/Out
```
> python ./manage.py scale_in
> python ./manage.py scale_out
``` 

### Database Restart
```
> python ./manage.py db_restart
```
  
### Database Restore
```
> python ./manage.py db_restore
```
  
### 종료
```
> ./manage.py destroy
```  

***
## 요구사양별 구현 방법
### gradle을 사용하여 어플리케이션과 도커이미지를 빌드한다.
#### Maven 설정으로 Gradle project 생성
```
> gradle init --type pom 
```
#### build.gradle 수정
빌드를 위해 몇가지 수정해줍니다. 우선 plugin에 spring boot를 추가합니다. 
gradle로 docker build도 같이하기위해 [docker plugin](https://github.com/palantir/gradle-docker)을 추가합니다.
```
plugins {
    id 'java'
    id 'maven-publish'
    id 'org.springframework.boot' version '2.4.0.RELEASE'
    id 'com.palantir.docker' version '0.22.1'
}
```
그리고 먼저 project가 잘 실행되나 확인하기 위해 gradle run을 수행하고 싶었습니다.
그래서 mainClassName을 추가했습니다.
```
mainClassName = 'org.springframework.samples.petclinic.PetClinicApplication'
```
docker 빌드를 위한 task를 추가합니다.
```
docker {
    name "petclinic"
    files tasks.bootJar.outputs.files
    buildArgs(['JAR_FILE': tasks.bootJar.outputs.files.singleFile.name])
}
```
Continer를 생성하기 위해 Dockerfile를 작성합니다.
```
FROM openjdk:8-jdk-alpine

VOLUME /logs

EXPOSE 8080

ARG JAR_FILE
COPY ${JAR_FILE} app.jar
ENTRYPOINT ["java","-Djava.security.egd=file:/dev/./urandom","-jar","/app.jar"]
```


#### Gradle을 통한 build
```
> gradle docker
```
만약 빌드 에러가 난다면 java JDK가 설치되지 않았거나 환경변수에 없을 수도 있으니 확인하고 다시 빌드하면 됩니다.
docker plugin을 설치했기에 gradle build와 jar생성, docker image생성이 한번에 이루어 집니다.

#### 정상동작여부 test
우선 K8S환경으로 옮기기전에 제대로 도는지 test합니다.
docker-compose.yml로 같이 돌리기 위해 docker-compose.yml을 좀 수정합니다
```
version: "3"
services:
  mysql:
    image: mysql:5.7
    container_name: mysql
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=petclinic
      - MYSQL_DATABASE=petclinic
    volumes:
      - "./conf.d:/etc/mysql/conf.d:ro"
      - "./data:/var/lib/mysql"

  petclinic:
    image: petclinic
    ports:
      - 8080:8080
    user: "1000"
    links:
      - mysql
    depends_on:
      - mysql
```

이제 docker-compose로 contianer들을 실행해봅니다.
```
> docker-compose create 
```
web browser로 http://localhost:8080에 정상 접속됨을 확인했습니다.


### 어플리케이션의 log는 host의 /logs 디렉토리에 적재되도록 한다.
\src\main\resource\application.properties파일에서 log file path를 추가했습니다.
```
logging.file.path=/logs
```
그리고 volumn에 host_path를 추가해서 host_path = /c/logs에 저장되도록 하였습니다.
linux환경에서는 /logs로 deploy_app.yaml manifast를 수정하면 됩니다.

### 정상 동작 여부를 반환하는 api를 구현하며, 10초에 한번 체크하도록 한다. 3번 연속 체크에 실패하면 어플리케이션은 restart 된다.
Http probe방식으로 체크하기 위해서 Spring Boot에 Rest API를 추가했습니다.
.\src\java\org\springframework\samples\petclinic 경로에 api폴더를 추가하고 HealthCheck.java파일을 생성했습니다.
Spring boot에서 제공하는 RestController로 호출시 System online이라고 return하는 api를 하나 작성했습니다. 경로는 /healty로 지정했습니다.
```
package org.springframework.samples.petclinic.api;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;

@RestController
public class HealthCheck {
    @GetMapping(path="/healthy")
    public String HealthCheck()
    {
        return  "System Online";
    }
}
```
그리고 Deployment yaml에서 spec.template.spec.containers 아래에 livenessProbe 옵션을 추가했습니다.
```
        livenessProbe:
          httpGet: # check app health via rest api from app
            path: /healthy
            port: 8080
          initialDelaySeconds: 150 # wait for initialize app 
          periodSeconds: 10 # while 10 second
          failureThreshold: 3 # failure count is 3
```

### 종료 시 30초 이내에 프로세스가 종료되지 않으면 SIGKILL로 강제 종료 시킨다.
Deployment yaml에서 spec.template.spec아래에 terminationGracePeriodSeconds 옵션으로 설정했습니다.
```
terminationGracePeriodSeconds: 30
```

### 배포 시와 scale in/out 시 유실되는 트래픽이 없어야 한다.
Rolling Update 설정하여 순차적으로 실행하고 update하도록 설정하였습니다.
minReadySecond 옵션으로 Ready에서 바로 avaliable이 되어 순단현상을 발생하는걸 방지합니다.
```
minReadySeconds: 10
  strategy:
    rollingUpdate:
      maxSurge: 25% # ?
      maxUnavailable: 25% # ?
    type: RollingUpdate
```


### 어플리케이션 프로세스는 root 계정이 아닌 uid:1000으로 실행한다.
Deployment yaml에서 spec.template.spec.securityContext 아래에 runAsUser 설정했습니다.
```
securityContext:
  runAsUser: 1000
  runAsGroup: 1000
```
pod에 shell로 접근하여 top명령으로 확인하였습니다.
```
Mem: 5739732K used, 330164K free, 6196K shrd, 139868K buff, 2966504K cached
CPU:   4% usr   4% sys   0% nic  91% idle   0% io   0% irq   0% sirq
Load average: 0.19 0.24 0.33 2/1349 760
  PID  PPID USER     STAT   VSZ %VSZ CPU %CPU COMMAND
    1     0 1000     S    2987m  50%   2   0% java -Djava.security.egd=file:/dev/./urandom -jar app.jar
```

### DB도 kubernetes에서 실행하며 재 실행 시에도 변경된 데이터는 유실되지 않도록 설정한다.
StatefulSet control을 사용하여 DB를 올리고 volumeClaimTemplates를 사용해서 각 pod마다 고유의 Persistent Volumes를 생성합니다.
생성된 각 Persistent Volumes은 해당하는 pod에 mount하여 data가 유실되지 않도록 합니다..
```
volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
``` 

### 어플리케이션과 DB는 Cluster domain을 이용하여 통신한다.
mysql-service라는 이름으로 ClusterIP type Service를 생성합니다.
```
apiVersion: v1
kind: Service
metadata:
  name: mysql-service
  labels:
    app: mysql
spec:
  type: ClusterIP
  ports:
  - name: mysql
    port: 3306
    protocol: TCP
  selector:
    app: mysql
```

\src\main\resource\application.properties 파일에서 database url를 Cluster Domain으로 수정하고 다시 빌드합니다.
```
spring.datasource.url=jdbc:mysql://mysql-service.default.svc.cluster.local/petclinic
```

### nginx-ingress-controller를 통해 어플리케이션에 접속이 가능하다.
Ingress-nginx-controller를 설치 후 ingress 설정을 해줬습니다.
```
> kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/provider/baremetal/deploy.yaml
```

host설정을 의해서 hosts파일을 수정했습니다.
```
127.0.0.1 petclininic.com
```

접속은 Ingress NodePort Service의 port번호를 확인해서 web broser로 접속합니다.
```
>  kubectl -n ingress-nginx get svc ingress-nginx-controller
NAME                       TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx-controller   NodePort   10.111.62.240   <none>        80:31338/TCP,443:30498/TCP   129m
```

### namespace는 default를 사용한다.
yaml작성 시 namespace를 명기하지 않음으로 default로 사용하였습니다.

### README.md 파일에 실행 방법을 기술한다.
현재 Github 문서에 실행 방법을 기록합니다.
