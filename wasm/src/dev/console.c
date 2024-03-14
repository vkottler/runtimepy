#include <emscripten/emscripten.h>
#include <stdio.h>

int main() {

  emscripten_log(EM_LOG_INFO, "Hello, world! (info) %d.", 345);
  emscripten_log(EM_LOG_DEBUG, "Hello, world! (debug) %d.", 456);

  printf("(printf) Console test.\n");

  return 0;
}
