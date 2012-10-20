/* most copy from libSystem */

#ifndef LIBSYS_H
#define LIBSYS_H

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <dirent.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <setjmp.h>
#include <errno.h>
#include <ctype.h>
#include <time.h>		/* for time_t prototype */
//#include "sysdep.h"



/* crypt.c */
typedef struct {
	unsigned long A, B, C, D;
	unsigned long Nl, Nh;
	unsigned long data[16];
	int num;
} MD5_CTX;
void MD5Init(MD5_CTX *);
void MD5Update(MD5_CTX *, const unsigned char *, unsigned int);
void MD5Final(MD5_CTX *, unsigned char[16]);
char *crypt_des(char *buf, char *salt);

#endif // LIBSYS_H


/*
 * Local variables:
 * tab-width: 4
 * c-basic-offset: 4
 * End:
 * vim600: noet sw=4 ts=4 fdm=marker
 * vim<600: noet sw=4 ts=4
 */

