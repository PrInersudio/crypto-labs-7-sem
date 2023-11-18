#include "find_set_bits.h"

// вычисляет позизию старшего установленного бита
unsigned last_set_bit(long unsigned n) {
    unsigned pos;
    asm volatile("bsr %0, %1": "=r"(pos) : "r"(n));
    return pos;
}

// вычисляет позизию младшего установленного бита
unsigned first_set_bit(long unsigned n) {
    unsigned pos;
    asm volatile("bsf %0, %1": "=r"(pos) : "r"(n));
    return pos;
}