# GCC_PATH ?= "/c/Users/foobar/TOOLS/gcc-arm-none-eabi/12.2 rel1/bin"
######################################
# helpers
######################################
# Recursive wildcard: returns all files matching a given pattern
# $(call rwildcard,$(BUILD_DIR),*.d) -> returns a list of files in $(BUILD_DIR) matching the pattern *.d
rwildcard=$(foreach d,$(wildcard $(1:=/*)),$(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))
 
######################################
# target
######################################
TARGET = Project
# Build configs are either N6-DK (default) or N6-DK-legacy, N6-Nucleo
BUILD_CONF ?= N6-DK
# Generate lst files with gcc (set it to a value to generate listings)
GENERATE_LISTINGS=

######################################
# building variables
######################################
OPT = -Os -g3

#######################################
# paths
#######################################
BASE_PATH = ../../..
PROJECT_PATH = $(BASE_PATH)/Applications/NPU_Validation
CORE_PATH = $(PROJECT_PATH)/Core
VALIDATION_PATH = $(PROJECT_PATH)/X-CUBE-AI/App
MIDDLEWARES_PATH = $(PROJECT_PATH)/../../../../Middlewares/ST
# --- Atonn specific
ATONN_PATH = $(PROJECT_PATH)/X-CUBE-AI/atonn
ATONN_RT_PATH = $(PROJECT_PATH)/../../../../Middlewares/ST/AI/Npu/ll_aton
# --- Drivers specific
BSP_PATH = $(PROJECT_PATH)/Drivers/BSP
CMSIS_PATH = $(PROJECT_PATH)/Drivers/CMSIS
N6_DRIVER_PATH = $(PROJECT_PATH)/Drivers/STM32N6xx_HAL_Driver
DK_DRIVER_PATH = $(BSP_PATH)/STM32N6570-DK
NUCLEO_DRIVER_PATH = $(BSP_PATH)/STM32N6xx_Nucleo

######################################
# source
######################################
# C sources
VALIDATION_SOURCES += $(VALIDATION_PATH)/aiPbIO.c
VALIDATION_SOURCES += $(VALIDATION_PATH)/aiPbMemRWServices.c
VALIDATION_SOURCES += $(VALIDATION_PATH)/aiPbMgr.c
VALIDATION_SOURCES += $(VALIDATION_PATH)/aiTestHelper.c
VALIDATION_SOURCES += $(VALIDATION_PATH)/aiTestUtility.c
#VALIDATION_SOURCES += $(VALIDATION_PATH)/aiValidation.c
VALIDATION_SOURCES += $(VALIDATION_PATH)/ai_device_adaptor.c
VALIDATION_SOURCES += $(VALIDATION_PATH)/lc_print.c
VALIDATION_SOURCES += $(VALIDATION_PATH)/pb_common.c
VALIDATION_SOURCES += $(VALIDATION_PATH)/pb_decode.c
VALIDATION_SOURCES += $(VALIDATION_PATH)/pb_encode.c
VALIDATION_SOURCES += $(VALIDATION_PATH)/stm32msg.pb.c
# VALIDATION_SOURCES += $(VALIDATION_PATH)/network.c
VALIDATION_SOURCES += $(VALIDATION_PATH)/kws.c
VALIDATION_SOURCES += $(VALIDATION_PATH)/img.c

ATONN_SOURCES += $(ATONN_RT_PATH)/ll_aton.c
ATONN_SOURCES += $(ATONN_RT_PATH)/ll_aton_cipher.c
ATONN_SOURCES += $(ATONN_RT_PATH)/ll_aton_dbgtrc.c
ATONN_SOURCES += $(ATONN_RT_PATH)/ll_aton_debug.c
ATONN_SOURCES += $(ATONN_RT_PATH)/ll_aton_lib.c
ATONN_SOURCES += $(ATONN_RT_PATH)/ll_aton_lib_sw_operators.c
ATONN_SOURCES += $(ATONN_RT_PATH)/ll_aton_rt_main.c
ATONN_SOURCES += $(ATONN_RT_PATH)/ll_aton_runtime.c
ATONN_SOURCES += $(ATONN_RT_PATH)/ll_aton_util.c
ATONN_SOURCES += $(ATONN_RT_PATH)/ll_sw_float.c
ATONN_SOURCES += $(ATONN_RT_PATH)/ll_sw_integer.c
ATONN_SOURCES += $(ATONN_RT_PATH)/ecloader.c
ATONN_SOURCES += $(ATONN_PATH)/ai_wrapper_ATON.c
ATONN_SOURCES += $(ATONN_PATH)/aiValidation_ATON.c
ATONN_SOURCES += $(ATONN_PATH)/ai_io_buffers_ATON.c

DRIVER_SOURCES += $(CMSIS_PATH)/Device/ST/STM32N6xx/Source/Templates/system_stm32n6xx_fsbl.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal_bsec.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal_cacheaxi.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal_cortex.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal_gpio.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal_i2c.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal_i2c_ex.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal_pwr.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal_pwr_ex.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal_rcc.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal_rcc_ex.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal_rif.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal_uart.c
DRIVER_SOURCES += $(N6_DRIVER_PATH)/Src/stm32n6xx_hal_xspi.c
# CMSIS STUFF #
#DRIVER_SOURCES += $(wildcard $(CMSIS_PATH)/DSP/Source/SupportFunctions/*.c)

# EndOfCMSIS #
C_SOURCES += $(CORE_PATH)/Src/main.c
C_SOURCES += $(CORE_PATH)/Src/stm32n6xx_it.c
C_SOURCES += $(CORE_PATH)/Src/md5.c
C_SOURCES += $(CORE_PATH)/Src/system_clock_config.c
C_SOURCES += $(CORE_PATH)/Src/misc_toolbox.c
C_SOURCES += $(CORE_PATH)/Src/npu_cache.c
C_SOURCES += $(CORE_PATH)/Src/mcu_cache.c
C_SOURCES += $(CORE_PATH)/Src/sysmem.c
C_SOURCES += $(CORE_PATH)/Src/syscalls.c
C_SOURCES += $(VALIDATION_SOURCES)
C_SOURCES += $(ATONN_SOURCES)
C_SOURCES += $(DRIVER_SOURCES)


#C_SOURCES += Src/check_malloc.c
#C_SOURCES += Src/stm32n6xx_hal_msp.c
#C_SOURCES += Src/system_stm32n6xx_s.c
#C_SOURCES += Drivers/STM32N6xx_HAL_Driver/Src/stm32n6xx_hal_cortex.c
#C_SOURCES += Drivers/STM32N6xx_HAL_Driver/Src/stm32n6xx_hal_pwr.c
#C_SOURCES += Drivers/STM32N6xx_HAL_Driver/Src/stm32n6xx_hal_pwr_ex.c
#C_SOURCES += Drivers/STM32N6xx_HAL_Driver/Src/stm32n6xx_hal_rcc.c
#C_SOURCES += Drivers/STM32N6xx_HAL_Driver/Src/stm32n6xx_hal_rcc_ex.c
#C_SOURCES += Drivers/STM32N6xx_HAL_Driver/Src/stm32n6xx_hal.c
#C_SOURCES += Drivers/STM32N6xx_HAL_Driver/Src/stm32n6xx_hal_uart.c
#C_SOURCES += Drivers/STM32N6xx_HAL_Driver/Src/stm32n6xx_hal_gpio.c

# ASM sources
ASM_SOURCES += ./startup_stm32n657xx.s

#######################################
# binaries
#######################################
PREFIX = arm-none-eabi-
# The gcc compiler bin path can be either defined in make command via GCC_PATH variable (> make GCC_PATH=xxx)
# either it can be added to the PATH environment variable.
ifdef GCC_PATH
CC = $(GCC_PATH)/$(PREFIX)gcc
AS = $(GCC_PATH)/$(PREFIX)gcc -x assembler-with-cpp
CP = $(GCC_PATH)/$(PREFIX)objcopy
SZ = $(GCC_PATH)/$(PREFIX)size
else
CC = $(PREFIX)gcc
AS = $(PREFIX)gcc -x assembler-with-cpp
CP = $(PREFIX)objcopy
SZ = $(PREFIX)size
endif
HEX = $(CP) -O ihex
BIN = $(CP) -O binary -S

#######################################
# CFLAGS
#######################################
CPU = -mcpu=cortex-m55 -mcmse -mthumb
FPU = -mfpu=auto -mfloat-abi=hard


# mcu
MCU = $(CPU) $(FPU)

# others c flags
CFLAGS_OTHERS = -std=c11

# C defines
C_DEFS += -DSTM32N657xx
C_DEFS += -DUSE_FULL_ASSERT
C_DEFS += -DUSE_FULL_LL_DRIVER
C_DEFS += -DUSER_VECT_TAB_ADDRESS
C_DEFS += -DVECT_TAB_SRAM
C_DEFS += -DLL_ATON_DUMP_DEBUG_API
C_DEFS += -DLL_ATON_PLATFORM=LL_ATON_PLAT_STM32N6
C_DEFS += -DLL_ATON_OSAL=LL_ATON_OSAL_BARE_METAL
C_DEFS += -DLL_ATON_RT_MODE=LL_ATON_RT_ASYNC
C_DEFS += -DLL_ATON_SW_FALLBACK
C_DEFS += -DLL_ATON_EB_DBG_INFO
C_DEFS += -DLL_ATON_DBG_BUFFER_INFO_EXCLUDED=1

# C includes
C_INCLUDES += -I$(CMSIS_PATH)/Core/Include
C_INCLUDES += -I$(CMSIS_PATH)/Device/ST/STM32N6xx/Include
C_INCLUDES += -I$(CMSIS_PATH)/Device/ST/STM32N6xx/Include/Templates
C_INCLUDES += -I$(CMSIS_PATH)/DSP/Include
C_INCLUDES += -I$(N6_DRIVER_PATH)/Inc
C_INCLUDES += -I$(CORE_PATH)/Inc
C_INCLUDES += -I$(ATONN_PATH)
C_INCLUDES += -I$(ATONN_RT_PATH)
C_INCLUDES += -I$(PROJECT_PATH)/../../../../Middlewares/ST/AI/Inc
C_INCLUDES += -I$(VALIDATION_PATH)

# DEPENDING ON THE TARGET BUILD, add extra files/defines:
ifeq ($(BUILD_CONF),N6-DK-legacy)
-include mk/N6-DK-legacy.mk
else ifeq ($(BUILD_CONF),N6-Nucleo)
-include mk/N6-Nucleo.mk
else ifeq ($(BUILD_CONF),N6-DK)
-include mk/N6-DK.mk
else ifeq ($(BUILD_CONF),N6-DK-USB)
-include mk/N6-DK-USB.mk
else ifeq ($(BUILD_CONF),N6-Nucleo-USB)
-include mk/N6-Nucleo-USB.mk
else
$(error Please use a known build configuration (N6-DK, N6-Nucleo, ...))
endif

# Build path
BUILD_DIR = build/$(BUILD_CONF)

ASFLAGS = $(MCU) $(AS_DEFS) $(AS_INCLUDES) $(OPT) -Wall -fdata-sections -ffunction-sections
CFLAGS = $(CFLAGS_OTHERS) $(MCU) $(C_DEFS) $(C_INCLUDES) $(OPT) -Wall -fdata-sections -ffunction-sections
# Generate dependency information
CFLAGS += -MMD -MP -MF"$(@:%.o=%.d)"

#######################################
# LDFLAGS		c:/users/foobar/tools/gcc-arm-none-eabi/12.2 rel1/bin/../lib/gcc/arm-none-eabi/12.2.1/../../../../arm-none-eabi/bin/ld.exe: warning: cannot find entry symbol Reset_Handler; defaulting to 34000000

#######################################
# link script
LDSCRIPT = ./STM32N657xx.ld

LDFLAGS_OTHERS = -Wl,--wrap=malloc --verbose


# libraries
LIBS = -lc -lm -lnosys -l:NetworkRuntime1020_CM55_GCC.a
LIBDIR = $(PROJECT_PATH)/../../../../Middlewares/ST/AI/Lib/GCC/ARMCortexM55
LDFLAGS = $(MCU) -specs=nano.specs -T$(LDSCRIPT) -L$(LIBDIR) $(LIBS) $(LDFLAGS_OTHERS) -Wl,-Map=$(BUILD_DIR)/$(TARGET).map,--cref -Wl,--gc-sections
# Uncomment to enable %f formatted output
# LDFLAGS += -u _printf_float
LDFLAGS += -Wl,--print-memory-usage

#######################################
# build the application into BUILD_DIR (all .o in build dir with same structure as in original tree)
#######################################

#OBJECTS = $(addprefix $(BUILD_DIR)/, $(notdir $(C_SOURCES:.c=.o)))
OBJECTS = $(C_SOURCES:$(BASE_PATH)/%.c=$(BUILD_DIR)/%.o)
OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(ASM_SOURCES:.s=.o)))
OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(ASM_SOURCES_S:.S=.o)))

## Use those lines if asm files are stored somewhere relative to base path
#OBJECTS = $(C_SOURCES:$(BASE_PATH)/%.c=$(BUILD_DIR)/%.o)
#OBJECTS += $(ASM_SOURCES:$(BASE_PATH)/%.s=$(BUILD_DIR)/%.o)
#OBJECTS += $(ASM_SOURCES_S:$(BASE_PATH)/%.S=$(BUILD_DIR)/%.o)

#OBJECTS = $(addprefix $(BUILD_DIR)/, $(notdir $(C_SOURCES:.c=.o)))
#OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(ASM_SOURCES:.s=.o)))
#OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(ASM_SOURCES_S:.S=.o)))

## Function to "pretty"-print steps in the logfile - 1 argument=string to print
define PRINT_STEP
$(info )
$(info )
$(info --- $(1))
endef

############################ Targets ##########################
# default action: build all
all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).hex $(BUILD_DIR)/$(TARGET).bin

$(BUILD_DIR)/%.o: $(BASE_PATH)/%.c Makefile | $(BUILD_DIR)
	@mkdir -p $(dir $@)
#	$(info -)
#	$(info -)
#	$(info Building $@ with $< --prereqs = $^)
	$(call PRINT_STEP,Compiling $@)
ifdef GENERATE_LISTINGS
# Generate info from the assembler 
# The -a option tells the assembler to generate a listing file, and the -ad option tells the assembler to include debugging information in the listing file.
# he -alms option is a specific option for the GNU assembler (as) that tells it to generate a listing file
	$(CC) -c $(CFLAGS) -Wa,-a,-ad,-alms=$(BUILD_DIR)/$(notdir $(<:.c=.lst)) $< -o $@
else
	$(CC) -c $(CFLAGS) $< -o $@
endif
	

$(BUILD_DIR)/%.o: %.S Makefile | $(BUILD_DIR)
	@mkdir -p $(dir $@)
	$(call PRINT_STEP,Compiling $@)
ifdef GENERATE_LISTINGS
	$(CC) -c $(CFLAGS) -Wa,-a,-ad,-alms=$(BUILD_DIR)/$(notdir $(<:.c=.lst)) $< -o $@
else
	$(CC) -c $(CFLAGS) $< -o $@
endif

$(BUILD_DIR)/%.o: %.s Makefile | $(BUILD_DIR)
	@mkdir -p $(dir $@)
	$(call PRINT_STEP,Compiling $@)
	$(AS) -c $(CFLAGS) $< -o $@

$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS) Makefile
	$(call PRINT_STEP,Linking $@)
	$(CC) $(OBJECTS) $(LDFLAGS) -o $@
	$(SZ) $@

$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.elf | $(BUILD_DIR)
	$(HEX) $< $@

$(BUILD_DIR)/%.bin: $(BUILD_DIR)/%.elf | $(BUILD_DIR)
	$(BIN) $< $@

$(BUILD_DIR):
	mkdir -p $@

#######################################
# clean up
#######################################
clean:
	-rm -fR $(BUILD_DIR)

test: 
#$(foreach var,$(.VARIABLES),$(info $(var) = $($(var))))
	$(info OBJECTS = $(OBJECTS))
	$(info ASM_SOURCES = $(ASM_SOURCES))
	$(info C_SOIURCE = $(C_SOURCES))
#######################################
# dependencies
#######################################
-include $(call rwildcard,$(BUILD_DIR),*.d)
