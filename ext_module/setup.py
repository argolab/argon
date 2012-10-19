from distutils.core import setup, Extension
setup(name = "ext_argo",
        version = "1.0",
        maintainer = "",
        maintainer_email = "",
        description = "Argo ext_user module",
        ext_modules = [
            Extension('ext_user',
            sources=['crypt.c', 'user.c', 'pass.c']
            #extra_compile_args=['-m32'],
            #extra_link_args=['-m32']
            ),

            Extension('ext_board',
            sources=['board.c']
            ),
            Extension('ext_post',
            sources=['post.c']
            )


            ]
        )

