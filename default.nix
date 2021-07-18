with import <nixpkgs> {};

stdenv.mkDerivation rec {
    env = buildEnv {
        name = name;
        paths = buildInputs;
    };

    name = "braille-python-server";
    buildInputs = [
        brltty
        python38
        python38Packages.ipython
    ];

    shellHook = ''
        if [ ! -e brltty.conf ]; then
            touch brltty.conf
        fi
        if [ "x$VIRTUAL_ENV" == "x" ]; then
            if [ "x$USERCACHE" != "x" ]; then
                export VIRTUAL_ENV="$USERCACHE/.virtualenvs/${name}"
            fi
        fi
        if [ ! -e $VIRTUAL_ENV ]; then
            echo creating virtualenv at $VIRTUAL_ENV
            python -m venv $VIRTUAL_ENV
            source $VIRTUAL_ENV/bin/activate
            pip install -r requirements.txt
        else
            source $VIRTUAL_ENV/bin/activate
        fi
        
        alias start-brltty='sudo killall brltty; sudo $(which brltty) -f ./brltty.conf -n -p /var/run/brltty.pid'
        alias start-receiver="python receiver.py server"
        alias | grep start
    '';
}
