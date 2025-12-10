; TimeTracker installer - production ready

[Setup]
AppName=Time Tracker
AppVersion=1.0.0
AppPublisher=Your Company
AppPublisherURL=https://yourcompany.example
DefaultDirName={pf}\Time Tracker
DefaultGroupName=Time Tracker
DisableProgramGroupPage=no
OutputDir=.
OutputBaseFilename=TimeTrackerInstaller_v1_0_0
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile=resources\icon.ico
AllowNoIcons=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "resources\*"; DestDir: "{app}\resources"; Flags: recursesubdirs createallsubdirs
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Time Tracker"; Filename: "{app}\main.exe"
Name: "{autodesktop}\Time Tracker"; Filename: "{app}\main.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\main.exe"; Description: "{cm:LaunchProgram,Time Tracker}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
