CD normal

REM Quick deleting old backup folder keep

CD keep

if errorlevel 1 (
	timeout 5
	exit
)

DEL /F/Q/S *.* > NUL

if errorlevel 1 (
	timeout 5
	exit
)

CD ..

if errorlevel 1 (
	timeout 5
	exit
)

RMDIR /Q/S keep

