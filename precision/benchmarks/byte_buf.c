#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
/************************/
/* AbsInt APIs settings */
/************************/
#ifdef __CRAB__
extern uint8_t uint8_t_nd(void);
extern bool bool_nd(void);
extern int int_nd(void);
extern void __CRAB_assert(int);
extern void __CRAB_assume(int);
extern bool sea_is_dereferenceable(const void *ptr, intptr_t offset);
extern void memhavoc(void *, size_t);
extern void sea_dsa_alias(const void *p, ...);
extern void __CRAB_intrinsic_do_reduction(void *, bool);

#define assume(X) __CRAB_assume(X)
#define assert(X) __CRAB_assert(X)
#define ASSERT_IS_DEREF(PTR, N) __CRAB_assert(sea_is_dereferenceable(PTR, N))
#define nd_int() int_nd()
#define nd_bool() bool_nd()
#define MEMCPY(DST, SRC, N) memcpy(DST, SRC, N)
#define MEMSET(PTR, VAL, NUM) memset(PTR, VAL, NUM)
#else
#include "mopsa.h"
#define assume(X) _mopsa_assume(X)
#define assert(X) _mopsa_assert(X)
#define ASSERT_IS_DEREF(PTR, N) _mopsa_assert_valid_bytes(PTR, N)
#define nd_int() _mopsa_rand_s32()
#define nd_bool() _mopsa_rand_u8() == 0
#define MEMCPY(DST, SRC, N) _mopsa_memcpy(DST, SRC, 0, N)
#define MEMSET(PTR, VAL, NUM) _mopsa_memset(PTR, VAL, 0, NUM)
#endif

#define N 100

struct byte_buf {
  int length;
  int capacity;
  char *buffer;
};

int main() {
  // pattern 1: allocate and init a batch of buffer in a for loop
  struct byte_buf *ary[N];
  for (int i = 0; i < N; ++i) { // no loop unrolling
    struct byte_buf *p = malloc(sizeof(struct byte_buf));
    p->buffer = malloc(sizeof(char) * (i + 1));
    p->length = i;
    p->capacity = i + 1;
    ary[i] = p;
  }
  struct byte_buf *buf1 = ary[0];
  char *new_buf = malloc(sizeof(char) * 20);
  ary[0]->buffer = new_buf;
  ary[0]->length = 15;
  ary[0]->capacity = 20;
  assert(ary[0]->length <= ary[0]->capacity); // mopsa and VSTTE cannot prove due to weak updates
  ASSERT_IS_DEREF(
      ary[0]->buffer,
      ary[0]->length * sizeof(char)); // mopsa claims this is out-of-bounds access
  ASSERT_IS_DEREF(
      ary[0]->buffer,
      ary[0]->capacity * sizeof(char)); // mopsa claims this is out-of-bounds access
  return 0;
}

/*
Obj:
Reported 2 safe checks

Rgn:
Reported 2 warning checks

==> Q: why one less assertion?
The assertion on 62 can be optimize as assert(true) through constant
propagation. Crab uses LLVM pass to simplify code.

Mopsa:
Commands:
mopsa-c -config mopsa_rel.json -numeric octagon -widening-delay=2 -loop-decr-it -stub-ignore-case malloc.failure -debug print byte_buf.c


3 warning checks on Line 69, Line 70 and Line 73 reported.
*/