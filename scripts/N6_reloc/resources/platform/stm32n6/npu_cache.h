#ifndef __NPU_CACHE_H__
#define __NPU_CACHE_H__

#if (LL_ATON_PLATFORM != LL_ATON_PLAT_STM32N6)
#error "LL_ATON_PLATFORM should be equal to LL_ATON_PLAT_STM32N6"
#endif

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

void npu_cache_clean_invalidate_range(uint32_t start_addr, uint32_t end_addr);
void npu_cache_clean_range(uint32_t start_addr, uint32_t end_addr);
void npu_cache_invalidate(void);

#ifdef __cplusplus
}
#endif

#endif /* __NPU_CACHE_H__ */