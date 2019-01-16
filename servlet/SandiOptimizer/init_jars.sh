mvn install:install-file \
   -Dfile=./src/main/resources/utils.jar \
   -DgroupId=com.github.SandiOptimizer \
   -DartifactId=util \
   -Dversion=1.0 \
   -Dpackaging=jar \
   -DgeneratePom=true

# Where each refers to:

# < path-to-file >: the path to the file to load e.g -> c:\kaptcha-2.3.jar

# < group-id >: the group that the file should be registered under e.g -> com.google.code

# < artifact-id >: the artifact name for the file e.g -> kaptcha

# < version >: the version of the file e.g -> 2.3

# < packaging >: the packaging of the file e.g. -> jar