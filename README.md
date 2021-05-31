# arma_server_daemon
This is a wrapper script that creates and manages the mods for arma 3 server instances. You can create multiple installations or multiple instances (profiles) within one arma 3 installation. Linux only (maybe windows will come later). This app downloads the ArmA 3 dedicated server and any mods directly from steam and the steam workshop, that way you don't have to worry about uploading them. All you need to do to download is pass the workshop URL to the app.

### Why?
There are probably more complicated server managers for arma out there, but the use case for this is an easy set of commands to get you going to spin up an arma server with your friends. This is not intended to be a comprehensive server manager. As such, it is very light-weight, and doesn't run any daemons in the background.

### Usage
Not a ton of info here yet, but the application has a nice `--help` screen. You can pass `-h` or `--help` in the nested commands as well for different help pages.

### Requirements
* The command `steamcmd` needs to be available to the python application
* A steam username and password

### Future Work
* Ability to import existing servers
* TMUX / persistent session integration
* On-Boot service file generation
* Dependencies for workshop content
* Workshop collection integration
* Increased user friendliness
* Better workshop integration (search, etc.)
* Changing the port of an instance from the CLI
* Adding mods manually integration (outside of the workshop)
* workshop / manual mission integration

### Contributing
I would love your help! I probably won't develop this application very quickly (I just want to play arma), so any PRs are highly appreciated! See the future work section for what I was thinking about adding. All required python classes are built-in to a standard Python 3 installation.