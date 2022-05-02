with import <nixpkgs> {};

let 
  nixShortcutsPath = ~/setup/bash/nix_shortcuts.sh;
  nixShortcuts = (import nixShortcutsPath);
in stdenv.mkDerivation rec {
    env = buildEnv {
        name = name;
        paths = buildInputs;
    };

    name = "braille-python-server";
    buildInputs = [
        brltty
        python39
        python39Packages.ipython
        glibcLocales
    ] ++ nixShortcuts.buildInputs;

    nativeBuildInputs = [
      nixShortcutsPath
    ];

    shellHook = ''
        if [ ! -e brltty.conf ]; then
            touch brltty.conf
        fi

        _setup-venv() {
            pip install -r requirements.txt
        }
        ensure-venv _setup-venv
        
        alias start-brltty='sudo killall brltty; sudo $(which brltty) -f ./brltty.conf -n -p /var/run/brltty.pid'
        alias start-receiver="python receiver.py server"

        echo-shortcuts ${__curPos.file}
    '';
}
