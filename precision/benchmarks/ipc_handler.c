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

typedef struct handle {
  int id;
  void *cookie;
} handle_t;

void init_handle(handle_t *ptr) {
  ptr->id = nd_int();
  ptr->cookie = NULL; // strong update
}

int main() {
  handle_t *h1 = (handle_t *)malloc(sizeof(handle_t));
#ifdef __CRAB__
  memhavoc(h1, sizeof(handle_t));
#endif
  init_handle(h1);

  int *a = (int *)malloc(sizeof(int) * 10);
  h1->cookie = a; // strong update

  assert(h1->cookie != NULL);

  handle_t *h2 = (handle_t *)malloc(sizeof(handle_t));
#ifdef __CRAB__
  memhavoc(h2, sizeof(handle_t));
#endif
  init_handle(h2);
  assert(h2->cookie == NULL);

  handle_t *h;
  if (nd_bool()) {
    h = nd_bool() ? h1 : h2;
  } else {
    h = (handle_t *)malloc(sizeof(handle_t));
    init_handle(h);
    h->cookie = nd_bool() ? NULL : a; // strong update
  }

  h->cookie = a;    // strong update
  int idx = nd_int();
  assume(idx >= 0);
  assume(idx < 10);
  ASSERT_IS_DEREF(h->cookie, idx);

  return 0;
}