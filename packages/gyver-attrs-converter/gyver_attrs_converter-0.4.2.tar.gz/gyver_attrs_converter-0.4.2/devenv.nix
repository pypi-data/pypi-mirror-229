{ pkgs, ... }:

{
  # https://devenv.sh/basics/
  env.GREET = "devenv";
  env.LD_LIBRARY_PATH = with pkgs; "${stdenv.cc.cc.lib}/lib";


  # https://devenv.sh/packages/
  packages = with pkgs; [ glib glibc gcc git python39 maturin patchelf commitizen python310 python311 ];

  languages.python = {
    enable = true;
    package = pkgs.python39;
  };
  # https://devenv.sh/scripts/

  # https://devenv.sh/languages/
  # languages.nix.enable = true;

  # https://devenv.sh/pre-commit-hooks/
  # pre-commit.hooks.shellcheck.enable = true;

  # https://devenv.sh/processes/
  # processes.ping.exec = "ping example.com";

  # See full reference at https://devenv.sh/reference/options/
}
