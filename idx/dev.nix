# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # nixpkgs channel
  channel = "stable-23.11";

  packages = [
    pkgs.python3
    pkgs.jdk20
    pkgs.cmake               # Required for Linux development
    pkgs.ninja               # Required for Linux development
    pkgs.pkg-config          # Required for Linux development
    pkgs.clang               # Required for Linux development
    pkgs.gtk3                # GTK 3 library
    pkgs.gtk3.dev            # GTK 3 development library for Linux toolchain
    pkgs.pango               # Pango library for text rendering
    pkgs.cairo               # Cairo library for graphics rendering
    pkgs.harfbuzz            # HarfBuzz library for text shaping
    pkgs.atk                 # ATK library for accessibility support
    pkgs.gdk-pixbuf          # GdkPixbuf library for image loading
    pkgs.glib                # GLib library for system-level utilities (includes GIO)
    pkgs.sudo                # Add sudo package
    pkgs.gst_all_1.gstreamer # Provides libgstapp-1.0.so.0
    pkgs.gcc                 # Add gcc for scikit-build
  ];

  idx = {
    extensions = [
      "ms-python.python",
      "ms-python.debugpy"
    ];

    workspace = {
      onCreate = {
        create-venv = ''
          export VENV_DIR=".venv"
          export MAIN_FILE="main.py"
          export LD_LIBRARY_PATH=/nix/store/b52h5nwsagbqnpfpv6aysr3b5ylgva7z-gst-plugins-base-1.22.8/lib:$LD_LIBRARY_PATH

          # Check if the virtual environment already exists
          if [ ! -d "$VENV_DIR" ]; then
            python -m venv $VENV_DIR
          fi

          if [ ! -f requirements.txt ]; then
            echo "requirements.txt not found. Creating one with flet..."
            echo "flet" > requirements.txt
          fi

          # Activate the virtual environment and update pip
          source $VENV_DIR/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
        '';

        default.openFiles = [ "README.md", "requirements.txt", "$MAIN_FILE" ];
      };
    };

    previews = {
      enable = true;
      previews = {
        web = {
          command = [
            "bash",
            "-c",
            ''
            export VENV_DIR=".venv"
            export MAIN_FILE="main.py"
            export LD_LIBRARY_PATH=/nix/store/b52h5nwsagbqnpfpv6aysr3b5ylgva7z-gst-plugins-base-1.22.8/lib:$LD_LIBRARY_PATH
            source $VENV_DIR/bin/activate
            flet run $MAIN_FILE --web --port $PORT
            ''
          ];
          env = { PORT = "$PORT"; };
          manager = "web";
        };
      };
    };
  };
}
