/*
    Pirate Bulletin Board System
    Copyright (C) 1990, Edward Luke, lush@Athena.EE.MsState.EDU

    Eagles Bulletin Board System
    Copyright (C) 1992, Raymond Rocker, rocker@rock.b11.ingr.com
			Guy Vega, gtvega@seabass.st.usm.edu
			Dominic Tynes, dbtynes@seabass.st.usm.edu

    Firebird Bulletin Board System
    Copyright (C) 1996, Hsien-Tsung Chang, Smallpig.bbs@bbs.cs.ccu.edu.tw
			Peng Piaw Foong, ppfoong@csie.ncu.edu.tw

    Firebird2000 Bulletin Board System
    Copyright (C) 1999-2001, deardragon, dragon@fb2000.dhs.org

    Puke Bulletin Board System
    Copyright (C) 2001-2002, Yu Chen, monster@marco.zsu.edu.cn
			     Bin Jie Lee, is99lbj@student.zsu.edu.cn

    Contains codes from YTHT & SMTH distributions of Firebird Bulletin
    Board System.

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 1, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
*/

#include "libbbs.h"

void
igenpass(const char *passwd, const char *userid, unsigned char md5passwd[])
{
	static const char passmagic[] =
	    " #r3:`>/CH'M&p%<xCj?bqd=/?L7o:N.s;j}Ouo!--PhX j^icU3aX{]?7`<(jOt";

	MD5_CTX md5;

	MD5Init(&md5);

	/* update size > 128 */
	MD5Update(&md5, (unsigned char *) passmagic, 64);
	MD5Update(&md5, (unsigned char *) passwd, strlen(passwd));
	MD5Update(&md5, (unsigned char *) passmagic, 64);
	MD5Update(&md5, (unsigned char *) userid, strlen(userid));

	MD5Final(&md5, md5passwd);
	md5passwd[0] = 0;
}

int
setpasswd(const char *passwd, struct userec *user)
{
	igenpass(passwd, user->userid, (unsigned char*)user->passwd);
	return 1;
}

void
genpasswd(const char *passwd, unsigned char md5passwd[])
{
	igenpass(passwd, "BBS System", md5passwd);
}

int
checkpasswd(const char *passwd, const char *test)
{
	static char pwbuf[DES_PASSLEN];
	char *pw;

	strlcpy(pwbuf, test, DES_PASSLEN);
	pw = crypt_des(pwbuf, (char *) passwd);
	return (!strcmp(pw, passwd));
}

int
checkpasswd2(const char *passwd, struct userec *user)
{
	unsigned char md5passwd[MD5_PASSLEN];

	if (user->passwd[0]) {
		if (checkpasswd(user->passwd, passwd)) {
			setpasswd(passwd, user);
			return YEA;
		}
		return NA;
	} else {
		igenpass(passwd, user->userid, md5passwd);
		return !memcmp(md5passwd, user->passwd, MD5_PASSLEN);
	}
}

int
checkpasswd3(const char *passwd, const char *test)
{
	unsigned char md5passwd[MD5_PASSLEN];

	igenpass(test, "BBS System", md5passwd);
	return !memcmp(md5passwd, passwd, MD5_PASSLEN);
}
