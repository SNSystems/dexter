setlocal EnableDelayedExpansion

for %%I in (%SOURCE_INDEXES%) do (
  clang++.exe -fuse-ld=lld -c !COMPILER_OPTIONS_%%I! !SOURCE_FILE_%%I! -o !OBJECT_FILE_%%I!
  if errorlevel 1 goto :FAIL
)

clang++.exe -fuse-ld=lld %OBJECT_FILES% -o %EXECUTABLE_FILE% -Wl,-subsystem:windows,-ENTRY:mainCRTStartup %LINKER_OPTIONS%
if errorlevel 1 goto :FAIL
goto :END

:FAIL
echo FAILED
exit /B 1

:END
exit /B 0
