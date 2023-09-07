File manager for the command line with understandable interface. The app has the necessary basic functionality. How it looks:
```
Files | disks: C
--------------------------------------------------------------------------
 C:\Users\alex-win\Documents
--------------------------------------------------------------------------
   1 ▓ Battle Brothers                                               dir
   2 ▓ FeedbackHub                                                   dir
   3 ▓ IISExpress                                                    dir
   4 ▓ Mount&Blade Warband                                           dir
   5 ▓ Mount&Blade Warband Savegames                                 dir
   6 ▓ Mount&Blade Warband WSE2                                      dir
   7 ▓ My Games                                                      dir
   8 ▓ My Web Sites                                                  dir
   9 ▓ Rockstar Games                                                dir
  10 ▓ Witcher 2                                                     dir
--------------------------------------------------------------------------
«help» for FAQ >
```


## Usage
To start app, enter the command at the command line:
```
filescli
```

Short commands to use the app with examples:
  - up: «..»
  - open: «12», «documents», «c:\users», «/home», «ftp://ftp.us.debian.org»
  - home path: «.»
  - copy,rename,delete: «copy 11», «delete 2,10»
  - ftp download: «download 11», «download 12,14»
  - show size: «size 9», «size» 
  - select page: «page 3»
  - disks: «disk», «disk C», «disk disk 2»
  - create: «dir Pictures», «file readme.txt»
  - sorting: «sort»(for ↑↓), «sort name», «sort size»
  - exercute CLI command: «code dir», «code ls»
  - «exit», «paste», «hidden»


## Features
- copy, paste, rename, delete
- sorts by name and size
- show/hide hidden files
- open files by default program
- catalog, files creation
- copy/paste to/from another file manager (only for windows)
- connect to ftp servers and download files from there
- exercute CLI (eg. "dir", "ls") commands (test functionality)
- navigation by typing short commands