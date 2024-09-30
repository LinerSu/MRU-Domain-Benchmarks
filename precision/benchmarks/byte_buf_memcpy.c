#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
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

extern FILE *file;

void foo(struct byte_buf *buf) {
    if (buf->capacity < 20) {
        uint8_t *new_buf = malloc(sizeof(uint8_t) * 20);
        buf->buffer[buf->length] = 1;
        ASSERT_IS_DEREF(buf->buffer, buf->length * sizeof(uint8_t));
        MEMCPY(new_buf, buf->buffer, sizeof(uint8_t) * buf->length);
        buf->capacity = 20;
        buf->buffer = new_buf;
    }
    uint8_t *tmp = nd_voidp();
    tmp = buf->buffer;
    ASSERT_IS_DEREF(buf->buffer, 20 * sizeof(uint8_t));
    // NOTE: Most AbsInt cannot interact with file sysytem, we just check buffer is 
    // accessible or not
    // size_t read_bytes = fread(buf->buffer, 1, 20, file);
    // if (read_bytes == 20) {
    //     buf->length = 20;
    // }
}

int main() {
    struct byte_buf *buf_ary[2];
    for (unsigned i = 0; i < 2; ++i) {
        buf_ary[i] = malloc(sizeof(struct byte_buf));
        if (!buf_ary[i]) {
            return -1;
        }
        int capacity = nd_int();
        int length = nd_int();
        assume(0 <= capacity);
        assume(capacity <= 10);
        assume(0 <= length);
        assume(length < capacity);
        buf_ary[i]->length = length;
        buf_ary[i]->capacity = capacity;
        buf_ary[i]->buffer = malloc(sizeof(uint8_t) * capacity);
        if (!buf_ary[i]->buffer) {
            return -1;
        }
    }
    // model pointer may alias
    struct byte_buf *buf_to_use;
    buf_to_use = nd_bool() ? buf_ary[0] : buf_ary[1];
    foo(buf_to_use);
    ASSERT_IS_DEREF(buf_ary[0]->buffer, buf_ary[0]->length * sizeof(uint8_t));

    return 0;
}