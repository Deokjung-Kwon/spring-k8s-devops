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
```
plugins {
    id 'java'
    id 'maven-publish'
    id 'org.springframework.boot' version '2.4.0.RELEASE'
}
```
그리고 먼저 project가 잘 실행되나 확인하기 위해 gradle run을 수행하고 싶었습니다.
그래서 mainClassName을 추가했습니다.
```
mainClassName = 'org.springframework.samples.petclinic.PetClinicApplication'
```

#### Gradle을 통한 build
```
> gradle compileJava
```
만약 빌드 에러가 난다면 java JDK가 설치되지 않았거나 환경변수에 없을 수도 있으니 확인하고 다시 빌드하면 됩니다.

#### 정상동작여부 test
우선 K8S환경으로 옮기기전에 제대로 도는지 test합니다.
docker-compose.yml에 mssql이 있으니 일단 올리고 확인합니다.
```
> docker-compose create 
> docker ps
```

### 어플리케이션의 log는 host의 /logs 디렉토리에 적재되도록 한다.

### 정상 동작 여부를 반환하는 api를 구현하며, 10초에 한번 체크하도록 한다. 3번 연속 체크에 실패하면 어플리케이션은 restart 된다.

### 종료 시 30초 이내에 프로세스가 종료되지 않으면 SIGKILL로 강제 종료 시킨다.

### 배포 시와 scale in/out 시 유실되는 트래픽이 없어야 한다.

### 어플리케이션 프로세스는 root 계정이 아닌 uid:1000으로 실행한다.

### DB도 kubernetes에서 실행하며 재 실행 시에도 변경된 데이터는 유실되지 않도록 설정한다.

### nginx-ingress-controller를 통해 어플리케이션에 접속이 가능하다.

### namespace는 default를 사용한다.

### README.md 파일에 실행 방법을 기술한다.
현재 Github 문서에 기록합니다.
