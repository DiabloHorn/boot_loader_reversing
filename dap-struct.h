struct dap{
    unsigned char size; // size of DAP 0x10
    unsigned char unused; // unused 0x0
    unsigned short numsectors; // number of sectors
    unsigned short buffer_offset; //buffer segment*16+offset
    unsigned short buffer_segment; //buffer segment*16+offset
    unsigned long startsectors; // absolute sector start
};
