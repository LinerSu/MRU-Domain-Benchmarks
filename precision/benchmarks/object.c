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

struct object {
  int x;
  int y;
};

int main() {
  // pattern 3: allocate and init two seperate allocated object, random pick one
  // and update
  struct object *obj = (struct object *)malloc(sizeof(struct object));
  obj->x = 3;
  obj->y = 4;
  struct object *ret = (struct object *)malloc(sizeof(struct object));
  ret->x = 5;
  ret->y = 6;
  struct object *a;
  if (nd_bool()) {
    a = obj;
  } else if (nd_bool()) {
    a = ret;
  } else {
    a = (struct object *)malloc(sizeof(struct object));
#ifdef __CRAB__
    memhavoc(a, sizeof(struct object));
#endif
  }
  int x = nd_int();
  int y = nd_int();
  assume(x == 10);
  assume(y == 4);
  a->x = x;
  a->y = y;
  int ret_x = nd_int();
  ret_x = a->x;
  int ret_y = a->y;
  assert(ret_x > ret_y);

#ifdef __CRAB__
  memhavoc(a, sizeof(struct object));
#endif

  return 0;
}