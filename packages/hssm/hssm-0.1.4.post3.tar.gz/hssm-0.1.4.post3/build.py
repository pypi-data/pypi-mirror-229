# noqa: D100
import os
import platform
import shutil
from distutils.core import Distribution, Extension

import numpy as np  # noqa
from Cython.Build import build_ext, cythonize

cython_dir = "src/hssm/likelihoods/hddm_wfpt"


if platform.system() == "Darwin":
    ext1 = Extension(
        "wfpt",
        ["src/hssm/likelihoods/hddm_wfpt/wfpt.pyx"],
        language="c++",
        extra_compile_args=["-stdlib=libc++"],
        include_dirs=[np.get_include()],
        extra_link_args=["-stdlib=libc++", "-mmacosx-version-min=10.9"],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    )
else:
    ext1 = Extension(
        "wfpt",
        ["src/hssm/likelihoods/hddm_wfpt/wfpt.pyx"],
        language="c++",
        include_dirs=[np.get_include()],
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    )

ext_modules = cythonize(
    [
        ext1,
        Extension(
            "cdfdif_wrapper",
            [
                "src/hssm/likelihoods/hddm_wfpt/cdfdif_wrapper.pyx",
                "src/hssm/likelihoods/hddm_wfpt/cdfdif.c",
            ],
            include_dirs=[np.get_include()],
        ),
    ],
    build_dir="./cython_build",
    compiler_directives={"language_level": "3", "linetrace": True},
)

dist = Distribution({"ext_modules": ext_modules})
cmd = build_ext(dist)
cmd.ensure_finalized()
cmd.run()

for output in cmd.get_outputs():
    relative_extension = os.path.relpath(output, cmd.build_lib)
    shutil.copyfile(output, "./src/hssm/likelihoods/hddm_wfpt/" + relative_extension)
