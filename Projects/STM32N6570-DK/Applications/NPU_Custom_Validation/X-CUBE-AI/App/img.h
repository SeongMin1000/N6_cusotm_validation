/**
  ******************************************************************************
  * @file    img.h
  * @author  STEdgeAI
  * @date    2026-02-02 09:29:14
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
#ifndef LL_ATON_IMG_H
#define LL_ATON_IMG_H

/******************************************************************************/
#define LL_ATON_IMG_C_MODEL_NAME        "img"
#define LL_ATON_IMG_ORIGIN_MODEL_NAME   "mobilenet_v2_1_0_224_INT8"

/************************** USER ALLOCATED IOs ********************************/
// No user allocated inputs
// No user allocated outputs

/************************** INPUTS ********************************************/
#define LL_ATON_IMG_IN_NUM        (1)    // Total number of input buffers
// Input buffer 1 -- Input_0_out_0
#define LL_ATON_IMG_IN_1_ALIGNMENT   (32)
#define LL_ATON_IMG_IN_1_SIZE_BYTES  (150528)

/************************** OUTPUTS *******************************************/
#define LL_ATON_IMG_OUT_NUM        (1)    // Total number of output buffers
// Output buffer 1 -- Quantize_247_out_0
#define LL_ATON_IMG_OUT_1_ALIGNMENT   (32)
#define LL_ATON_IMG_OUT_1_SIZE_BYTES  (1001)

#endif /* LL_ATON_IMG_H */
