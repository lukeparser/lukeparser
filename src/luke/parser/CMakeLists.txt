# minimum required CMAKE version
CMAKE_MINIMUM_REQUIRED(VERSION 3.7 FATAL_ERROR)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

# compiler must be 11 or 14
set(CMAKE_CXX_STANDARD 17)

# required if linking to static library
add_definitions(-DANTLR4CPP_STATIC)

# using /MD flag for antlr4_runtime (for Visual C++ compilers only)
set(ANTLR4_WITH_STATIC_CRT OFF)
# add external build for antlrcpp
include(ExternalAntlr4Cpp)
# add antrl4cpp artifacts to project environment
include_directories(${ANTLR4_INCLUDE_DIRS})

# set variable pointing to the antlr tool that supports C++
# this is not required if the jar file can be found under PATH environment
set(ANTLR_EXECUTABLE /usr/share/java/antlr-complete.jar)
# add macros to generate ANTLR Cpp code from grammar
find_package(ANTLR REQUIRED)

# Call macro to add lexer and grammar to your build dependencies.
antlr_target(MarkdownLexer MarkdownLexer.g4 LEXER)
antlr_target(MarkdownParser MarkdownParser.g4 PARSER
             DEPENDS_ANTLR MarkdownLexer
             COMPILE_FLAGS -lib ${ANTLR_MarkdownLexer_OUTPUT_DIR}
             LISTENER
             )

# include generated files in project environment
include_directories(${ANTLR_MarkdownLexer_OUTPUT_DIR})
include_directories(${ANTLR_MarkdownParser_OUTPUT_DIR})

# python.h
FIND_PACKAGE(PythonLibs 3)
FIND_PATH(PYTHON_INCLUDE_PATH Python.h
  /usr/include
  /usr/local/include)
INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_DIRS})


# add generated grammar to markdown binary target
add_executable(markdown glue.cpp
               ${ANTLR_MarkdownLexer_CXX_OUTPUTS}
               ${ANTLR_MarkdownParser_CXX_OUTPUTS})
target_link_libraries(markdown antlr4_static)
