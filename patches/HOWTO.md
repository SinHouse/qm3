## Basic instructions for patch management  

Make patch:
`diff -Naur original_file new_file_version`

Apply a patch:
`patch -b -p0 < patch_file.patch`

See [more examples here](https://www.thegeekstuff.com/2014/12/patch-command-examples/).
