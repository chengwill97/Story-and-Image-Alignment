# Installation Instructions for Servlet App

### 1. Setup Servlet Environment

1. Install Java 8 (1.8.0)

[Java Download Listin](https://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html)

[Java Installation Guide](https://askubuntu.com/questions/56104/how-can-i-install-sun-oracles-proprietary-java-jdk-6-7-8-or-jre)

2. Install Maven 3.6.0

[Maven Installation Guide](https://maven.apache.org/install.html)

[Optional: Proxy Setup](https://maven.apache.org/settings.html#Proxies)

3. Install Gurobi 7.02

[Gurobi Installation Guide](http://www.gurobi.com/academia/for-universities)

[Gurobi Set Environment Variables](http://abelsiqueira.github.io/blog/installing-gurobi-7-on-linux/)

4. Install and Setup Tomcat 9

(Tomcat Download Listing)[http://tomcat.apache.org/]

(Tomcat Installation Guide)[http://www.ntu.edu.sg/home/ehchua/programming/howto/tomcat_howto.html]

5. Build and setup war

Install gurobi.jar and utils.jar

- Go to main directory of SandiOptimizer servlet

```cd ${STORY_ALIGNMENT_ROOT}/servlet/SandiOptimizer```

- Change path of option "-Dfile" that points to gurobi.jar

- Path of gurobi.jar should be in ${gurobi_path}/linux64/lib/gurobi.jar

```bash init_jars.sh```

- Build application

```mvn clean install```

- copy war to tomcat webapps folder

```cp  ${STORY_ALIGNMENT_ROOT}/servlet/SandiOptimizer/target/SandiOptimizer.war ${TOMCAT_HOME}/webapps```

4. Download Stanford Post Tagger

[Stanford POS Download Listing](https://nlp.stanford.edu/software/tagger.shtml#Download)

5. Download Google Word2Vec

[Google Word2Vec Download](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit)

6. Set up SandiOptimizer.xml

```cd ${STORY_ALIGNMENT_ROOT}/servlet/SandiOptimizer/src/main/resources```

- Change the model_path's Environment "value"/path
to point to the Google word2vec model

- Change the postagger_path's Environment "value"/path to point to ```${stanford-postagger}/models/english-bidirectional-distsim.tagger```

- Copy SandiOptimizer.xml to tomcat

```cp SandiOptimizer.xml ${TOMCAT_HOME}/conf/Catalina/localhost```

7. Start tomcat server

```cd ${TOMCAT_HOME}/bin```
```sh startup.sh```

8. Stop tomcat server

```cd ${TOMCAT_HOME}/bin```
```sh shutdown.sh```