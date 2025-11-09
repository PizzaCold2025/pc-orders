{
  pkgs ? import <nixpkgs> { },
}:
pkgs.mkShell {
  packages = with pkgs; [
    awscli2
    jq
    zip
    (python311.withPackages (ps: with ps; [ pip ]))
    serverless
  ];
}
