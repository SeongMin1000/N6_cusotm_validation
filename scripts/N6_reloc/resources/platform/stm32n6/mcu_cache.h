#ifndef __MCU_CACHE_H__
#define __MCU_CACHE_H__

#if (LL_ATON_PLATFORM != LL_ATON_PLAT_STM32N6)
#error "LL_ATON_PLATFORM should be equal to LL_ATON_PLAT_STM32N6"
#endif

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

int mcu_cache_invalidate(void);
int mcu_cache_clean(void);
int mcu_cache_clean_invalidate(void);
int mcu_cache_invalidate_range(uint32_t start_addr, uint32_t end_addr);
int mcu_cache_clean_range(uint32_t start_addr, uint32_t end_addr);
int mcu_cache_clean_invalidate_range(uint32_t start_addr, uint32_t end_addr);

#ifdef __cplusplus
}
#endif

#endif // __MCU_CACHE_H__
