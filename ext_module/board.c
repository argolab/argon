#include <time.h>
#include <Python.h> 
#include <structmember.h>
#include <fcntl.h>
#include "libbbs.h"
#include "libsys.h"

typedef struct _BoardHeader{
    PyObject_HEAD
  
	char boardname[BFNAMELEN];
	char title[BTITLELEN];
	char BM[BMLEN];
	unsigned int flag;		/* 版面属性 */
	unsigned int level;		/* read/post权限 */
	unsigned int lastpost;	/* lastpost time */
	unsigned int total; 	/* 文章数 */
	unsigned int parent;	/* parent board ID */
	unsigned int total_today;
	unsigned char reserved[4];

}BoardHeader;


static PyMemberDef BoardHeaderMembers[] = {
    {"boardname", T_STRING_INPLACE, offsetof(BoardHeader, boardname), 0, "" },
    {"title", T_STRING_INPLACE, offsetof(BoardHeader, title), 0, "" },
    {"BM", T_STRING_INPLACE, offsetof(BoardHeader, BM), 0, "" },
    {"flag", T_UINT, offsetof(BoardHeader, flag), 0, "" },
    {"level", T_UINT, offsetof(BoardHeader, level), 0, "" },
    {"lastpost", T_UINT, offsetof(BoardHeader, lastpost), 0, "" },
    {"parent", T_UINT, offsetof(BoardHeader, parent), 0, "" },
    {NULL}
};

static PyMethodDef BoardHeaderMethods[] = {
    {NULL }
};


static PyTypeObject BoardHeaderType= {
    PyObject_HEAD_INIT(NULL)
    0,
    "BoardHeader.BoardHeaderType", /* tp_name */ 
    sizeof(BoardHeader), /* tp_basicsize */ 
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
    BoardHeaderMethods, /* tp_methods */
    BoardHeaderMembers, /* tp_members */
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

static PyObject * Convert2Object( struct boardheader *bh )
{
    BoardHeader *ptObj;
    ptObj = (BoardHeader *)PyObject_New(BoardHeader, &BoardHeaderType);

    memcpy(ptObj->boardname, bh->filename, sizeof( bh->filename ));
    memcpy(ptObj->title, bh->title, sizeof( bh->title));
    memcpy(ptObj->BM, bh->BM, sizeof( bh->BM));
    ptObj->flag = bh->flag;
    ptObj->level= bh->level;
    ptObj->lastpost= bh->lastpost;
    ptObj->total = bh->total;
    ptObj->parent = bh->parent;
    ptObj->total_today = bh->total_today;
    return (PyObject *)ptObj;
}

static PyObject * BoardHeader_GetBoardHeader(PyObject *self, PyObject *args) 
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
    
    if ( num * sizeof( struct boardheader ) >= st.st_size ) {
        PyErr_SetString( PyExc_AttributeError, "Get overflow." );
        return 0;
    }

    lseek( fd, num * sizeof( struct boardheader ), SEEK_SET);
    
    struct boardheader bh;
    if ( read(fd, &bh, sizeof(bh)) != sizeof( bh ) )  {
        PyErr_SetString( PyExc_IOError, "Read boardheader error." );
        return 0;
    }
    PyObject *retObj = Convert2Object(&bh); 

    close(fd);
    return retObj;
}


static PyMethodDef module_methods[] = {
    {"GetBoardHeader", (PyCFunction)BoardHeader_GetBoardHeader, METH_VARARGS, ""},
    {NULL}
};

void initext_board(  )
{
    PyObject *m;
    if ( PyType_Ready( &BoardHeaderType)  < 0)
    {
        return ;
    }
    m = Py_InitModule3("ext_board", module_methods, "argo ext_modules");

    if ( !m )
    {
        return ;
    }

    Py_INCREF( &BoardHeaderType );

    PyModule_AddObject( m, "BoardHeaderType", (PyObject *)&BoardHeaderType);

}


