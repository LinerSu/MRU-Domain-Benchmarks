#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
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

struct byte_buf {
  int length;
  int capacity;
  uint8_t *buffer;
};

void init_buf_ary(struct byte_buf **buf_ptr, int len, int cap) {
  struct byte_buf *buf = (*buf_ptr);
  buf->buffer = (uint8_t *)malloc(sizeof(uint8_t) * cap);
  buf->length = len;
  buf->capacity = cap;
  return;
}

struct byte_buf *_p1;
struct byte_buf *_p2;
struct byte_buf *_p3;
struct byte_buf **buf1 = &_p1;
struct byte_buf **buf2 = &_p2;
struct byte_buf **buf3 = &_p2;

void allocating() {
  struct byte_buf *p = malloc(sizeof(struct byte_buf));
  struct byte_buf *q = malloc(sizeof(struct byte_buf));
  struct byte_buf *r = malloc(sizeof(struct byte_buf));
  // NOTE: the follwing code pattern may occur in real C program:
  // Static pointer analysis may not resolve pointer aliasing precisely
  // E.g.
  // https://github.com/awslabs/aws-c-cal/blob/3d4c08b60ffa8698cda14bb8d56e5d6a27542f17/source/ecc.c#L245-L264
  if (nd_bool()) {
    *buf1 = p;
    *buf2 = q;
    *buf3 = r;
  } else if (nd_bool()) {
    *buf1 = r;
    *buf2 = p;
    *buf3 = q;
  } else {
    *buf1 = q;
    *buf2 = r;
    *buf3 = p;
  }
  // vstte and MOPSA can successfully update if just no confusion of aliasing
  // *buf1 = p;
  // *buf2 = q;
  // *buf3 = r;
}

int main() {
  // pattern 2: allocate bunch of objects at first
  // initializing each by a pointer of pointer
  allocating();
  init_buf_ary(buf1, 3, 7);
  init_buf_ary(buf2, 8, 10);
  init_buf_ary(buf3, 5, 6);
  ASSERT_IS_DEREF((*buf1)->buffer, (*buf1)->length * sizeof(uint8_t));
  ASSERT_IS_DEREF((*buf2)->buffer, (*buf2)->length * sizeof(uint8_t));
  ASSERT_IS_DEREF((*buf3)->buffer, (*buf3)->length * sizeof(uint8_t));

  return 0;
}
