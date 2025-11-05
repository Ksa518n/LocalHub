#!/usr/bin/env sh

#
# Copyright 2017 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

##############################################################################
##
##  Gradle start up script for UN*X
##
##############################################################################

# Determine the Java command to use to start the JVM.
if [ -n "$JAVA_HOME" ] ; then
    if [ -x "$JAVA_HOME/jre/sh/java" ] ; then
        # IBM's JDK on AIX uses strange locations for the system java executable
        JAVACMD="$JAVA_HOME/jre/sh/java"
    else
        JAVACMD="$JAVA_HOME/bin/java"
    fi
    if [ ! -x "$JAVACMD" ] ; then
        die "ERROR: JAVA_HOME is set to an invalid directory: $JAVA_HOME

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
    fi
else
    JAVACMD="java"
    which java >/dev/null 2>&1 || die "ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.

Please set the JAVA_HOME variable in your environment to match the
location of your Java installation."
fi

# Determine the script directory (for the wrapper properties file)
# Use the shell script location to determine the wrapper location
# Backwards compatibility for scripts that have been moved to a different location
# than the wrapper jar.
APP_HOME=$(dirname "$0")

# Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
DEFAULT_JVM_OPTS=""

# Determine the wrapper jar location
WRAPPER_JAR="$APP_HOME/gradle/wrapper/gradle-wrapper.jar"

# Check if the wrapper jar exists
if [ ! -f "$WRAPPER_JAR" ]; then
    die "ERROR: Could not find the Gradle wrapper within your project.

Please ensure that the 'gradle/wrapper/gradle-wrapper.jar' file is present."
fi

# Determine the wrapper properties file location
WRAPPER_PROPERTIES="$APP_HOME/gradle/wrapper/gradle-wrapper.properties"

# Check if the wrapper properties file exists
if [ ! -f "$WRAPPER_PROPERTIES" ]; then
    die "ERROR: Could not find the Gradle wrapper properties file within your project.

Please ensure that the 'gradle/wrapper/gradle-wrapper.properties' file is present."
fi

# Execute the wrapper
exec "$JAVACMD" $DEFAULT_JVM_OPTS $JAVA_OPTS $GRADLE_OPTS -jar "$WRAPPER_JAR" "$@"
