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

#define N 100
#define BOUND 200

typedef struct range {
    int start;
    int end;
} range_t;

// Function to initialize a range ensuring the relational property is maintained
void init_bounded_range(range_t *r, int start, int end) {
    if (start <= end && end <= BOUND) {
        r->start = start;
        r->end = end;
    } else {
        // Handle the error case
        r->start = BOUND;
        r->end = BOUND;
    }
}

int main() {
    // allocate several objects based on branch conditions
    // initialize them right after
    // select one (randomly) and update
    range_t *a;
    if (nd_bool()) {
        range_t *tmp1 = malloc(sizeof(range_t));
        init_bounded_range(tmp1, 2, 10);
        a = tmp1;
    } else {
        range_t *tmp2 = malloc(sizeof(range_t));
        init_bounded_range(tmp2, 10, 2);
        a = tmp2;
    }

    int s = nd_int();
    s = a->start;
    int e = a->end;
    assert(s <= e);
    init_bounded_range(a, 4, 9);
    s = nd_int();
    s = a->start;
    e = a->end;
    assert(s <= e);

    return 0;
}