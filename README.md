# boot_loader_reversing
Collection of files to aid with boot loader reversing  
Files will be added as needed, feel free to contribute  
The reference section contains multiple useful references

## overview files
* dap-main.c
* dap-struct.h
* debug_cmds.py
* dot_gdbinit
* wrap_directory.py

## using the files

**dot_gdbinit**  
The _dot_gdbinit_ file should be used as your _.~/gdbinit_ file and it contains some commands to set the a hardware breakpoint, the architecture and load the DAP structure definition. It is assumed that when you start _gdb_ this will be the working directory.

**dap-\***  
The header and C file are used as a trick to load the definition of the DAP structure into GDB. Used by _dot_gdbinit_. They can be compiled with:  

`gcc -g -c dap-main.c dap-struct.h`

**debug_cmds.py**  
Helper functions for gdb written in python with some useful commands, must be sourced from within gdb with:  

`source debug_cmds.py`

* ci \<mnemonic\>
  * run application until it encounters the specified mnemonic `ci int`
* pex_interrupt
  * parses, executes and displays interrupt calls

**wrap_directory.py**  
Wraps calls to a target directory and the files within with fuse. Can be used to print read and write calls.  

`python wrap_directory.py target mountpoint`

## References

* https://github.com/skorokithakis/python-fuse-sample
  * Example on wrapping file system read/write calls with fuse
* https://gist.github.com/Manouchehri/2b1b523eed834f295915
  * Running Windows 10 with QEMU
* https://serverfault.com/a/683272
  * Allow root/other users on fuse
* https://stackoverflow.com/a/39031709
  * Allow root/other users on fuse programmatically
* https://stackoverflow.com/a/31249378
  * Python GDB command to break on mnemonic
* https://fy.blackhats.net.au/blog/html/2017/08/04/so_you_want_to_script_gdb_with_python.html
  * Tutorial on howto extend GDB with Python
* https://sourceware.org/gdb/onlinedocs/gdb/Python-API.html
  * GDB Python API documentation
* https://en.wikipedia.org/wiki/INT_13H
  * Interrupt 0x13 documentation
* https://gist.github.com/logc/c37ef4f5604430bfbf5625bf7546d4cd
  * Nifty trick on adding unknown structs to GDB while running
* http://ternet.fr/gdb_real_mode.html
  * Tutorial on remote debugging of real mode code with gdb and an example _.gdbinit_ file