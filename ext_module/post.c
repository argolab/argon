#include <time.h>
#include <Python.h> 
#include <structmember.h>
#include <fcntl.h>
#include "libbbs.h"
#include "libsys.h"

typedef struct _FileHeader{
    PyObject_HEAD
    
    char boardname[BFNAMELEN];
    char prefix[FNAMELEN];
    unsigned int bid;

    char filename[FNAMELEN];		// filename format: {M|G}.time.{Alphabet}
	char owner[IDLEN + 2];
	char realowner[IDLEN + 2];		// to perserve real owner id even in anonymous board
	char title[TITLELEN];
	unsigned int flag;
	unsigned int size;
	unsigned int id;  			// identity of article (per thread)
	unsigned int filetime;
	char reserved[12];

}FileHeader;


static PyMemberDef FileHeaderMembers[] = {
    {"bid", T_UINT, offsetof(FileHeader, bid), 0, "" },
    {"boardname", T_STRING_INPLACE, offsetof(FileHeader, boardname), 0, "" },
    {"prefix", T_STRING_INPLACE, offsetof(FileHeader, prefix), 0, "" },

    {"filename", T_STRING_INPLACE, offsetof(FileHeader, filename), 0, "" },
    {"owner", T_STRING_INPLACE, offsetof(FileHeader, owner), 0, "" },
    {"realowner", T_STRING_INPLACE, offsetof(FileHeader, realowner), 0, "" },
    {"title", T_STRING_INPLACE, offsetof(FileHeader, title), 0, "" },

    {"flag", T_UINT, offsetof(FileHeader, flag), 0, "" },
    {"size", T_UINT, offsetof(FileHeader, size), 0, "" },
    {"id", T_UINT, offsetof(FileHeader, id), 0, "" },
    {"filetime", T_UINT, offsetof(FileHeader, filetime), 0, "" },
    {NULL}
};

static PyObject * FileHeader_GetFileStream( FileHeader *self )
{
    char filepath[128];
    snprintf( filepath, sizeof( filepath ), "%s/boards/%s/%s", self->prefix, self->boardname, self->filename );
    char *buf;
    struct stat st;
    if ( stat(filepath, &st) < 0 ) {
        PyErr_SetString( PyExc_IOError, "Stat file error" );
        return NULL;
    }
    int fd = open(filepath, O_RDONLY, 0600); 
    if ( fd < 0 ) {
        PyErr_SetString( PyExc_IOError, "Open file error" );
        return NULL;
    }

    buf = malloc(st.st_size+1);
    int n = read(fd, buf, st.st_size);
    
    PyObject *retObj = PyString_FromStringAndSize( buf, n );
    free(buf);
    close(fd);

    return retObj;
}


static PyMethodDef FileHeaderMethods[] = {
    { "GetFileStream", (PyCFunction)FileHeader_GetFileStream, METH_NOARGS },
    {NULL}
};


static PyTypeObject FileHeaderType= {
    PyObject_HEAD_INIT(NULL)
    0,
    "FileHeader.FileHeaderType", /* tp_name */ 
    sizeof(FileHeader), /* tp_basicsize */ 
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
    FileHeaderMethods, /* tp_methods */
    FileHeaderMembers, /* tp_members */
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

static FileHeader *Convert2Object( struct fileheader *fh )
{
    FileHeader *ptObj;
    ptObj = (FileHeader *)PyObject_New(FileHeader, &FileHeaderType);

    memcpy(ptObj->filename, fh->filename, sizeof( fh->filename ));
    memcpy(ptObj->owner, fh->owner, sizeof( fh->owner ));
    memcpy(ptObj->realowner, fh->realowner, sizeof( fh->realowner ));
    memcpy(ptObj->title, fh->title, sizeof( fh->title ));
    
    ptObj->flag = fh->flag;
    ptObj->size = fh->size;
    ptObj->id = fh->id;
    ptObj->filetime = fh->filetime;

    return ptObj;
}

static PyObject * FileHeader_GetFileHeader(PyObject *self, PyObject *args) 
{
    const char *boardname, *prefix;
    char recfile[256];
    int num, bid;
    if ( !PyArg_ParseTuple(args, "ssii", &prefix, &boardname, &bid, &num) )
        return 0;
    
    sprintf( recfile, "%s/boards/%s/.DIR", prefix, boardname );

    int fd = open(recfile, O_RDONLY, 0600);

    if ( fd < 0 )  {
        char msg[128];
        sprintf( msg, "Can not open file %s", recfile );
        PyErr_SetString( PyExc_IOError, msg );
        return 0;
    }

    struct stat st; 
    if (stat(recfile, &st) < 0) {
        PyErr_SetString( PyExc_IOError, "Get stat error." );
        return 0;
    }
    
    struct fileheader fh;

    if ( num * sizeof( fh ) >= st.st_size ) {
        PyErr_SetString( PyExc_AttributeError, "Get overflow." );
        return 0;
    }

    lseek( fd, num * sizeof( fh ), SEEK_SET);
    
    if ( read(fd, &fh, sizeof(fh)) != sizeof( fh ) )  {
        PyErr_SetString( PyExc_IOError, "Read FileHeader error." );
        return 0;
    }

    FileHeader *retObj = Convert2Object(&fh); 
    strcpy(retObj->boardname, boardname);
    strcpy(retObj->prefix, prefix);

    retObj->bid = bid;

    close(fd);
    return (PyObject *)retObj;
}


static PyMethodDef module_methods[] = {
    {"GetFileHeader", (PyCFunction)FileHeader_GetFileHeader, METH_VARARGS, ""},
    {NULL}
};

void initext_post(  )
{
    PyObject *m;
    if ( PyType_Ready( &FileHeaderType)  < 0)
    {
        return ;
    }
    m = Py_InitModule3("ext_post", module_methods, "argo ext_modules");

    if ( !m )
    {
        return ;
    }

    Py_INCREF( &FileHeaderType );

    PyModule_AddObject( m, "FileHeaderType", (PyObject *)&FileHeaderType);

}


