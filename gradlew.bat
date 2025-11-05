@rem
@rem Copyright 2017 the original author or authors.
@rem
@rem Licensed under the Apache License, Version 2.0 (the "License");
@rem you may not use this file except in compliance with the License.
@rem You may obtain a copy of the License at
@rem
@rem      http://www.apache.org/licenses/LICENSE-2.0
@rem
@rem Unless required by applicable law or agreed to in writing, software
@rem distributed under the License is distributed on an "AS IS" BASIS,
@rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@rem See the License for the specific language governing permissions and
@rem limitations under the License.
@rem

@rem
@rem Script to run the Gradle wrapper
@rem
@if "%DEBUG%" == "" @echo off
@rem ##########################################################################
@rem
@rem  Gradle startup script for Windows
@rem
@rem ##########################################################################

@rem Set local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" setlocal

@rem Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
set DEFAULT_JVM_OPTS=

@rem Find Java
if defined JAVA_HOME goto findJava1
set JAVA_HOME=
:findJava1
if exist "%JAVA_HOME%\bin\java.exe" goto findJava2
set JAVA_HOME=
:findJava2
if defined JAVA_HOME goto findJava3
for %%i in (java.exe) do if defined PATHEXT (set JAVA_HOME=%%~dpi) else (set JAVA_HOME=%%~dpi)
:findJava3
if defined JAVA_HOME goto findJava4
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
echo.
echo Please set the JAVA_HOME variable in your environment to match the
echo location of your Java installation.
goto end
:findJava4
set JAVA_HOME=%JAVA_HOME:~0,-1%

@rem Determine the script directory (for the wrapper properties file)
set APP_HOME=%~dp0

@rem Determine the wrapper jar location
set WRAPPER_JAR=%APP_HOME%gradle\wrapper\gradle-wrapper.jar

@rem Check if the wrapper jar exists
if exist "%WRAPPER_JAR%" goto checkProperties
echo ERROR: Could not find the Gradle wrapper within your project.
echo.
echo Please ensure that the 'gradle\wrapper\gradle-wrapper.jar' file is present.
goto end

:checkProperties
@rem Determine the wrapper properties file location
set WRAPPER_PROPERTIES=%APP_HOME%gradle\wrapper\gradle-wrapper.properties

@rem Check if the wrapper properties file exists
if exist "%WRAPPER_PROPERTIES%" goto executeWrapper
echo ERROR: Could not find the Gradle wrapper properties file within your project.
echo.
echo Please ensure that the 'gradle\wrapper\gradle-wrapper.properties' file is present.
goto end

:executeWrapper
@rem Execute the wrapper
"%JAVA_HOME%\bin\java" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %GRADLE_OPTS% -jar "%WRAPPER_JAR%" %*

:end
if "%OS%"=="Windows_NT" endlocal
