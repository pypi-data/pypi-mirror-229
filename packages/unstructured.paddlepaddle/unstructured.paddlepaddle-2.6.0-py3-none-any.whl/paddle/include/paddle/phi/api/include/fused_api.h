#pragma once

#include <tuple>

#include "paddle/phi/api/include/tensor.h"
#include "paddle/phi/common/scalar.h"
#include "paddle/phi/common/int_array.h"
#include "paddle/utils/optional.h"

namespace paddle {
namespace experimental {


PADDLE_API Tensor fused_bias_act(const Tensor& x, const paddle::optional<Tensor>& bias, const paddle::optional<Tensor>& dequant_scales, const paddle::optional<Tensor>& shift, const paddle::optional<Tensor>& smooth, const std::string& act_method = "gelu", const std::string& compute_dtype = "default", float quant_scale = -1, int quant_round_type = 1, float quant_max_bound = 127.0, float quant_min_bound = -127.0);

PADDLE_API std::tuple<Tensor, Tensor, Tensor, Tensor> fused_bias_residual_layernorm(const Tensor& x, const paddle::optional<Tensor>& bias, const paddle::optional<Tensor>& residual, const paddle::optional<Tensor>& norm_weight, const paddle::optional<Tensor>& norm_bias, float epsilon, float residual_alpha, int begin_norm_axis, float quant_scale, int quant_round_type, float quant_max_bound, float quant_min_bound);

PADDLE_API std::tuple<Tensor, Tensor> fused_dropout_add(const Tensor& x, const Tensor& y, const paddle::optional<Tensor>& seed_tensor, const Scalar& p, bool is_test, const std::string& mode, int seed = 0, bool fix_seed = false);

PADDLE_API std::tuple<Tensor, Tensor> fused_linear_param_grad_add(const Tensor& x, const Tensor& dout, const paddle::optional<Tensor>& dweight, const paddle::optional<Tensor>& dbias, bool multi_precision = true, bool has_bias = true);

PADDLE_API std::tuple<Tensor, Tensor, Tensor> fused_rotary_position_embedding(const Tensor& q, const paddle::optional<Tensor>& k, const paddle::optional<Tensor>& v, const paddle::optional<Tensor>& sin, const paddle::optional<Tensor>& cos, const paddle::optional<Tensor>& position_ids, bool use_neox_rotary_style = true);


}  // namespace experimental
}  // namespace paddle
