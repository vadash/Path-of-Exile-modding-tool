# Features

* Disable post processing (bloom, blur, dof, vingette, chromatic abberation)

* Disable shadows (regular and screenplace), fog

* Uniform lighting for all locations (delve "hack")

* Remove laggy effects (all important stuff like cannot die aura, sirius meteor is untouched)

* Remove monster sounds (non boss)

* Remove dead bodies for performance

* Remove all MTX

# Guide for new users

https://imgur.com/a/lujEQq3

# Preview

Recommended preset posted below

[potato] - will remove something important but can provide big fps boost

OR - you can pick one. For example only 1 filter for .env files

![preview1](https://i.imgur.com/b77Ur76.jpg)

![preview1](https://i.imgur.com/LxqWWXE.png)

# Disclaimer

If you use GGPK to modify the game files, you are responsible for the consequences and risks. So far they didnt ban anyone for it in last 3 years

# How to use

[Гайд для 2HEAD на русском](https://youtu.be/JfGD9HfGwp4)

## Prepare phase (do it once)

* Backup clean Content.ggpk (skip with fast internet)

* [Download python](https://www.python.org/ftp/python/3.7.7/python-3.7.7-amd64.exe) -> **Check add to PATH**

![install](https://i.imgur.com/WGL3CSw.png)

* [Download script](https://github.com/vadash/Path-of-Exile-modding-tool/archive/master.zip) Unpack somewhere and open script folder (Path-of-Exile-modding-tool-master)

* Open optional folder and copy what u need to exctracted. Correct path is `Path-of-Exile-modding-tool\normal\extracted\Shaders\PostProcessing.hlsl`

* Run `Start.cmd` 

* Provide path to ggpk (example, C:\games\poe\Content.ggpk)

![install](https://i.imgur.com/QFt4iM1.png)

* Press Scan -> Wait for it to finish (Scan button is not red) -> Close tool

## After every patch

* Update Poe -> Close game

* Run `Start.cmd` 

* Automods -> PoeSmoother -> Tick everything you need

* Press modify (you dont need to wait, every action is added to queue. DONT click twice)

* Press insert button (you dont need to wait, every action is added to queue. DONT click twice)

* Now wait for ~10 minutes (SSD) / ~9000 minutes (HDD) until red background is gone

Skill and item MTX replacements: apply them 1 by 1 and test in multiple maps before applying another one! [Report crashes here](https://github.com/vadash/Path-of-Exile-modding-tool/issues) 

# Donate

[If you like what you see you can support me <3](https://www.paypal.me/vadash)

# Credits

* poemods (original repo) 95% work is his
https://github.com/poemods/Path-of-Exile-modding-tool

* avs for exception list and fog idea

* beta testers for bug testing <3

# Troubleshooting

* Close game and tool

* Delete old modding tool

* [Download script](https://github.com/vadash/Path-of-Exile-modding-tool/archive/master.zip) Unpack somewhere and open script folder (Path-of-Exile-modding-tool-master)

* Restore clean Content.ggpk from backup (or download it again)

* Delete folders CachedHLSLShaders, ShaderCacheD3D11, ShaderCacheVulkan from poe root folder

Now apply settings 1 by 1 and check where it crashed before

*Report* it here https://github.com/vadash/Path-of-Exile-modding-tool/issues or here https://www.ownedcore.com/forums/mmo/path-of-exile/poe-bots-programs/661920-path-of-exile-modding-tool-mods-1.html

## Permission denied

Right click poe folder -> Security -> Edit -> Add -> Advanced -> Find now -> Select "Everyone" -> Ok -> Click on "Everyone" -> Click allow full control -> Ok -> Ok

![access](https://i.imgur.com/nkdVySn.png)

## Failed to load ggpk invalid tag X

Close game -> Run included ggpk_defragment.exe -> Wait to finish

## File not found error

Example https://i.imgur.com/yuclr4X.jpg

Close game and tool -> Run `run_me_after_big_patch(reset keep folder).cmd`
