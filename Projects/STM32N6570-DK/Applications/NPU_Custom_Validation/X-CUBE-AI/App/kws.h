/**
  ******************************************************************************
  * @file    kws.h
  * @author  STEdgeAI
  * @date    2026-02-02 09:49:26
  * @brief   Minimal description of the generated c-implemention of the network
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  ******************************************************************************
  */
#ifndef LL_ATON_KWS_H
#define LL_ATON_KWS_H

/******************************************************************************/
#define LL_ATON_KWS_C_MODEL_NAME        "kws"
#define LL_ATON_KWS_ORIGIN_MODEL_NAME   "kws_micronet_m"

/************************** USER ALLOCATED IOs ********************************/
// No user allocated inputs
// No user allocated outputs

/************************** INPUTS ********************************************/
#define LL_ATON_KWS_IN_NUM        (1)    // Total number of input buffers
// Input buffer 1 -- Input_0_out_0
#define LL_ATON_KWS_IN_1_ALIGNMENT   (32)
#define LL_ATON_KWS_IN_1_SIZE_BYTES  (490)

/************************** OUTPUTS *******************************************/
#define LL_ATON_KWS_OUT_NUM        (1)    // Total number of output buffers
// Output buffer 1 -- Quantize_57_out_0
#define LL_ATON_KWS_OUT_1_ALIGNMENT   (32)
#define LL_ATON_KWS_OUT_1_SIZE_BYTES  (12)

#endif /* LL_ATON_KWS_H */
