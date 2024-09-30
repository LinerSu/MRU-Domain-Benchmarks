#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdbool.h>
/************************/
/* AbsInt APIs settings */
/************************/
#ifdef __CRAB__
extern uint8_t uint8_t_nd(void);
extern bool bool_nd(void);
extern int int_nd(void);
extern void *void_nd(void);
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
#define nd_voidp() void_nd()
#define MEMCPY(DST, SRC, N) memcpy(DST, SRC, N)
#define MEMSET(PTR, VAL, NUM) memset(PTR, VAL, NUM)
#else
#include "mopsa.h"
#define assume(X) _mopsa_assume(X)
#define assert(X) _mopsa_assert(X)
#define ASSERT_IS_DEREF(PTR, N) _mopsa_assert_valid_bytes(PTR, N)
#define nd_int() _mopsa_rand_s32()
#define nd_bool() _mopsa_rand_u8() == 0
#define nd_voidp() _mopsa_rand_void_pointer()
#define MEMCPY(DST, SRC, N) _mopsa_memcpy(DST, SRC, 0, N)
#define MEMSET(PTR, VAL, NUM) _mopsa_memset(PTR, VAL, 0, NUM)
#endif

struct byte_buf {
    int length;
    int capacity;
    uint8_t *buffer;
};

int main(void) {
  struct byte_buf *b1 = malloc(sizeof(struct byte_buf));
  #ifdef __CRAB__
  memhavoc(b1, sizeof(struct byte_buf));
  #endif
  int len = nd_int();
  int cap = nd_int();
  assume(0 <= len);
  assume(len < cap);
  assume(cap <= 10);
  b1->length = len;
  b1->capacity = cap;
  b1->buffer = malloc(cap * sizeof(int));
  
  struct byte_buf *b2 = malloc(sizeof(struct byte_buf));
  #ifdef __CRAB__
  memhavoc(b2, sizeof(struct byte_buf));
  #endif
  len = nd_int();
  cap = nd_int();
  assume(0 <= len);
  assume(len < cap);
  assume(cap <= 20);
  b2->length = len;
  b2->capacity = cap;
  b2->buffer = malloc(cap * sizeof(int));

  #ifdef __CRAB__
  sea_dsa_alias(b1, b2);
  struct byte_buf *b = b2;
  #else
  struct byte_buf *b = nd_bool() ? b1 : b2;
  #endif

  len = b->length;
  cap = b->capacity;
  uint8_t *buf = b->buffer;

  assert(cap > 0);
  assert(len < cap);
  ASSERT_IS_DEREF(buf, cap);

  return 0;
}
