#!/usr/bin/env python

from distutils.core import setup, Extension

setup(name             = "coincidence",
      version          = "0.0.1",
      description      = "Counts coincidences in B&H DPC230 timetag files",
      author           = "Pete Shadbolt",
      author_email     = "pete.shadbolt@gmail.com",
      maintainer       = "pete.shadbolt@gmail.com",
      url              = "",
      packages         = ["coincidence"],
      ext_modules      = [
          Extension(
              'coincidence', ['./src/coincidence.c'],
              extra_compile_args=["-Ofast", "-march=native"])
        ]
      )
