{...}: {
  languages.python.enable = true;

  scripts.build.exec = "rm nupd && go build -o nupd .";

  enterTest = "go test ./...";
}
