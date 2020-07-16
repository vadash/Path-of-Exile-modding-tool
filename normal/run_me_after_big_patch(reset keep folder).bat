REM Quick deleting old backup folder keep

REN keep keep2

if errorlevel 1 (
	exit
)

CD keep2

if errorlevel 1 (
	exit
)

DEL /F/Q/S *.* > NUL

if errorlevel 1 (
	exit
)

CD ..

if errorlevel 1 (
	exit
)

RMDIR /Q/S keep2

