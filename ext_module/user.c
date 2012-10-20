#include <time.h>
#include <Python.h> 
#include <structmember.h>
#include <fcntl.h>
#include "libbbs.h"
#include "libsys.h"

typedef struct _UserRec{
    PyObject_HEAD

	char userid[IDLEN + 2];	/* PASSFILE */
	unsigned int firstlogin;
	char lasthost[16];	/* 上一次登录地址 */
	unsigned int numlogins;
	unsigned int numposts;
	char flags[2];			/* 用到了3位, consts.h userec->flag[0] */
	char passwd[MD5_PASSLEN];
	char username[NICKNAMELEN + 1]; /* nick */  /*!!!!!!!!!!!!!!!!!!!  username=>nickname */
	char ident[NAMELEN + 1];	/*帐号注册地址 */

	char termtype[16];	
	char reginfo[STRLEN - 16];	/* 也就是认证email */
	unsigned int userlevel;   	/* 用户权限 */
	unsigned char usertitle;  	/* 称号 */
	unsigned char reserved[7];
	unsigned int lastlogin;
	unsigned int lastlogout;	  	
	unsigned int stay;
	char realname[NAMELEN + 1];
	char address[STRLEN];
	char email[STRLEN - 12];
	unsigned int nummails;
	unsigned int lastjustify;
	char gender;
	unsigned char birthyear;
	unsigned char birthmonth;
	unsigned char birthday;
	int signature;
	unsigned int userdefine;	/* 个人设定参数 */
	int notedate;		/* no use currently */
	int noteline;			/* 进站时已阅读notepad noteline行了 */
}UserRec;

static PyMemberDef UserRecMember[] = {
    {"userid", T_STRING_INPLACE, offsetof(UserRec, userid), 0, "" },
    {"firstlogin", T_UINT, offsetof( UserRec, firstlogin ), 0, ""}, 
    {"lasthost",  T_STRING_INPLACE, offsetof( UserRec, lasthost ), 0, ""}, 
    {"numlogins", T_UINT, offsetof( UserRec, numlogins ), 0, ""}, 
    {"numposts", T_UINT , offsetof( UserRec,  numposts), 0, ""}, 
    {"flags", T_STRING_INPLACE, offsetof( UserRec, flags), 0, ""}, 
    {"passwd", T_STRING_INPLACE, offsetof( UserRec,  passwd), 0, ""}, 
    {"username", T_STRING_INPLACE, offsetof( UserRec, username ), 0, ""}, 
    {"ident", T_STRING_INPLACE, offsetof( UserRec, ident ), 0, ""}, 
//  {"termtype", T_STRING_INPLACE , offsetof( UserRec, termtype ), 0, ""}, 
    {"reginfo", T_STRING_INPLACE, offsetof( UserRec, reginfo ), 0, ""}, 
    {"userlevel", T_UINT, offsetof( UserRec, userlevel ), 0, ""}, 
    {"usertitle", T_UBYTE, offsetof( UserRec, usertitle ), 0, ""}, 
//  {"reserved", T_STRING_INPLACE, offsetof( UserRec, reserved ), 0, ""}, 
    {"lastlogin", T_UINT, offsetof( UserRec, lastlogin ), 0, ""}, 
    {"lastlogout", T_UINT, offsetof( UserRec, lastlogout ), 0, ""}, 
    {"stay", T_UINT, offsetof( UserRec, stay ), 0, ""}, 
    {"realname", T_STRING_INPLACE, offsetof( UserRec, realname ), 0, ""}, 
    {"address", T_STRING_INPLACE, offsetof( UserRec, address ), 0, ""}, 
    {"email", T_STRING_INPLACE, offsetof( UserRec, email ), 0, ""}, 
    {"nummails", T_UINT, offsetof( UserRec, nummails), 0, ""}, 
//  {"lastjustify", T_INT, offsetof( UserRec, lastjustify ), 0, ""}, 
    {"gender", T_CHAR, offsetof( UserRec, gender), 0, ""}, 
    {"birthyear", T_UBYTE, offsetof( UserRec, birthyear), 0, ""}, 
    {"birthmonth", T_UBYTE, offsetof( UserRec, birthmonth), 0, ""}, 
    {"birthday", T_UBYTE, offsetof( UserRec, birthday), 0, ""}, 
//  {"signature", T_, offsetof( UserRec, signature), 0, ""}, 
    {"userdefine", T_UINT, offsetof( UserRec, userdefine), 0, ""}, 
//  {"notedate", , offsetof( UserRec, ), 0, ""}, 
    {"noteline", T_UINT, offsetof( UserRec, noteline), 0, ""}, 
    {NULL}
};


static PyObject * UserRec_GetAddress(UserRec *self) 
{
    return PyString_FromStringAndSize(self->address, strlen(self->address));
}

static void _HexDigest(const char *passwd, int passwdlen, char *digest)
{
    static const char ttb[] = "0123456789abcdef";

    int i;
    for ( i = 0; i < passwdlen; i++ )
    {
        digest[i*2] = ttb[(passwd[i] >> 4) & 15];
        digest[i*2+1] = ttb[passwd[i] & 15];
    }
    digest[ passwdlen * 2] = '\0';

}
static PyObject * UserRec_GetPasswd( UserRec *self )
{
    // Need to transfer binary stream to hex representation
    if (self->passwd[0]) {
        // For old encryption crypt_des
        return PyString_FromString( self->passwd);
    }
    // For md5
    char buf[64];
    memset(buf, 0, sizeof(buf));
    _HexDigest(self->passwd, sizeof(self->passwd), buf);
    return PyString_FromStringAndSize( buf, 2 * sizeof(self->passwd));
}

static PyObject * UserRec_GetUsername( UserRec *self )
{
    return PyString_FromStringAndSize(self->username, strlen(self->username));
}

static PyObject * UserRec_GetRealname( UserRec *self )
{
    return PyString_FromStringAndSize(self->realname, strlen(self->realname));
}

static PyMethodDef UserRecMethods[] = {
    { "GetPasswd", (PyCFunction)UserRec_GetPasswd, METH_NOARGS },
    { "GetAddress", (PyCFunction)UserRec_GetAddress, METH_NOARGS },
    { "GetUsername", (PyCFunction)UserRec_GetUsername, METH_NOARGS },
    { "GetRealname", (PyCFunction)UserRec_GetRealname, METH_NOARGS },
    {NULL }
};


static PyTypeObject UserRecType= {
    PyObject_HEAD_INIT(NULL)
    0,
    "user.UserRec", /* tp_name */ 
    sizeof(UserRec), /* tp_basicsize */ 
    0, /* tp_itemsize */ 
    0, /* tp_dealloc */
    0, /* tp_print */
    0, /* tp_getattr */
    0, /* tp_setattr */
    0, /* tp_compare */
    0, /* tp_repr */
    0, /* tp_as_number */ 
    0, /* tp_as_sequence */ 
    0, /* tp_as_mapping */ 
    0, /* tp_hash */
    0, /* tp_call */
    0, /* tp_str */
    0, /* tp_getattro */ 
    0, /* tp_setattro */ 
    0, /* tp_as_buffer */ 
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    0, /* tp_doc */
    0, /* tp_traverse */
    0, /* tp_clear */
    0, /* tp_richcompare */ 
    0, /* tp_weaklistoffset */ 
    0, /* tp_iter */
    0, /* tp_iternext */ 
    UserRecMethods, /* tp_methods */
    UserRecMember, /* tp_members */
    0, /* tp_getset */
    0, /* tp_base */
    0, /* tp_dict */
    0, /* tp_descr_get */
    0, /* tp_descr_set */
    0, /* tp_dictoffset */ 
    0, /* tp_init */
    0, /* tp_alloc */
    0, /* tp_new */
};

static PyObject* Convert2Object(struct userec *ptUrec)
{
    UserRec * ptObj;
    ptObj = (UserRec *)PyObject_New(UserRec, &UserRecType);
    
    memcpy(ptObj->userid, ptUrec->userid, sizeof( ptUrec->userid )); 
    ptObj->firstlogin = ptUrec->firstlogin;
    memcpy(ptObj->lasthost, ptUrec->lasthost, sizeof( ptUrec->lasthost )); 
    ptObj->numlogins = ptUrec->numlogins;
    ptObj->numposts= ptUrec->numposts;
    memcpy(ptObj->flags, ptUrec->flags, sizeof( ptUrec->flags )); 
    memcpy(ptObj->passwd, ptUrec->passwd, sizeof( ptUrec->passwd )); 
    memcpy(ptObj->username, ptUrec->username, sizeof( ptUrec->username )); 
    memcpy(ptObj->ident, ptUrec->ident, sizeof( ptUrec->ident )); 
    memcpy(ptObj->reginfo, ptUrec->reginfo, sizeof( ptUrec->reginfo )); 
    ptObj->userlevel= ptUrec->userlevel;
    ptObj->usertitle= ptUrec->usertitle;
    ptObj->lastlogin= ptUrec->lastlogin;
    ptObj->lastlogout= ptUrec->lastlogout;
    ptObj->stay= ptUrec->stay;
    memcpy(ptObj->realname, ptUrec->realname, sizeof( ptUrec->realname )); 
    memcpy(ptObj->address, ptUrec->address, sizeof( ptUrec->address )); 

    memcpy(ptObj->email, ptUrec->email, sizeof( ptUrec->email )); 
    ptObj->nummails= ptUrec->nummails;
    ptObj->gender= ptUrec->gender;
    ptObj->birthyear= ptUrec->birthyear;
    ptObj->birthmonth= ptUrec->birthmonth;
    ptObj->birthday= ptUrec->birthday;
    ptObj->userdefine= ptUrec->userdefine;
    ptObj->noteline= ptUrec->noteline;

    return (PyObject *)ptObj;
}
static PyObject * user_GetUserRec(PyObject *self, PyObject *args) 
{
    const char *recfile;
    int num;
    if ( !PyArg_ParseTuple(args, "si", &recfile, &num) )
        return 0;

    int fd = open(recfile, O_RDONLY, 0644);
    if ( fd < 0 )  {
        PyErr_SetString( PyExc_IOError, "Can not open file." );
        return 0;
    }
    struct stat st; 
    if (stat(recfile, &st) < 0) {
        PyErr_SetString( PyExc_IOError, "Get stat error." );
        return 0;
    }
    
    if ( num * sizeof( struct userec ) >= st.st_size ) {
        PyErr_SetString( PyExc_AttributeError, "Get overflow." );
        return 0;
    }

    lseek( fd, num * sizeof( struct userec ), SEEK_SET);

    struct userec urec;
    if ( read(fd, &urec, sizeof(urec)) != sizeof( urec) )  {
        PyErr_SetString( PyExc_IOError, "Read userec error." );
        return 0;
    }
    
    PyObject * retObj = Convert2Object(&urec);
    
    close(fd);
    return retObj;
}

static PyObject * user_GenPasswdMd5(PyObject *self, PyObject *args)
{
    const char *userid, *passwd;
    if ( !PyArg_ParseTuple(args, "ss", &userid, &passwd) ) {
        return  0; 
    }
    
    char md5passwd[32], digestpasswd[64];
    igenpass(passwd, userid, md5passwd);
    _HexDigest(md5passwd, 16, digestpasswd);
    return PyString_FromString(digestpasswd);
}

static PyObject * user_GenPasswdDes(PyObject *self, PyObject *args)
{
    const char *passwd, *trypasswd;
    static char pwbuf[DES_PASSLEN]; 
    char *pw;
    if ( !PyArg_ParseTuple( args, "ss", &passwd, &trypasswd ) )
    strlcpy(pwbuf, trypasswd, DES_PASSLEN);
    pw = crypt_des(pwbuf, (char*) passwd);
    return PyString_FromString( pw );
}

static PyMethodDef module_methods[] = {
    { "GetUserRec", (PyCFunction)user_GetUserRec, METH_VARARGS, 
        "GetUserRec(recfile, num) \n The first argument is the .PASSWDS file. Second argument represent the num(order) of the record to get." },
    {"GenPasswdMd5", (PyCFunction)user_GenPasswdMd5, METH_VARARGS, "GenPasswdMd5(userid, passwd) \nGenerate md5 passwds using argo's algorithm."},
    {"GenPasswdDes", (PyCFunction)user_GenPasswdDes, METH_VARARGS, "GenPasswdDes(passwd, trypasswd) \nGenerate Des encryption."},
    {NULL}
};


void initext_user(  )
{
    PyObject *m;
    if ( PyType_Ready( &UserRecType)  < 0)
    {
        return ;
    }
    m = Py_InitModule3("ext_user", module_methods, "argo ext_modules");

    if ( !m )
    {
        return ;
    }

    Py_INCREF( &UserRecType);

    PyModule_AddObject( m, "UserRecType", (PyObject *)&UserRecType);

}

