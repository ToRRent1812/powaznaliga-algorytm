let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    pkgs.gobject-introspection
    pkgs.gtk3
    (pkgs.python3.withPackages (python-pkgs: with python-pkgs; [
      pip
      pygobject3
    ]))
  ];
}
