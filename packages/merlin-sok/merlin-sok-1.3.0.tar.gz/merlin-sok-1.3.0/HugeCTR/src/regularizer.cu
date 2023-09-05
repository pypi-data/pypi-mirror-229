/*
 * Copyright (c) 2023, NVIDIA CORPORATION.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <core23/tensor.hpp>
#include <regularizer.hpp>
#include <utility>

namespace HugeCTR {

template <typename T>
Regularizer<T>::Regularizer(const Tensor2<float>& weight_buff, const Tensor2<T>& wgrad_buff,
                            const int batch_size, const std::shared_ptr<GPUResource>& gpu_resource)
    : weight_buff_(weight_buff),
      wgrad_buff_(wgrad_buff),
      weight_tensors_(std::nullopt),
      wgrad_tensors_(std::nullopt),
      batch_size_(batch_size),
      gpu_resource_(gpu_resource) {}

template <typename T>
Regularizer<T>::Regularizer(std::optional<WeightTensors> weight_tensors,
                            std::optional<WgradTensors<T>> wgrad_tensors, const int batch_size,
                            const std::shared_ptr<GPUResource>& gpu_resource)
    : weight_tensors_(weight_tensors),
      wgrad_tensors_(wgrad_tensors),
      batch_size_(batch_size),
      gpu_resource_(gpu_resource) {}

template <typename T>
void Regularizer<T>::compute_rterm() {
  CudaDeviceContext context(get_device_id());
  if (weight_tensors_) {
    // core23 branch
    auto flat_weight_tensor = weight_tensors_->flatten();
    const float* weight = flat_weight_tensor.data();
    auto num_elements = flat_weight_tensor.size(0);
    do_compute_rterm(weight, &h_rterm_, num_elements);
    return;
  } else if (weight_buff_.allocated()) {
    // legacy branch
    const float* weight = weight_buff_.get_ptr();
    auto num_elements = weight_buff_.get_num_elements();
    do_compute_rterm(weight, &h_rterm_, num_elements);
    return;
  } else {
    do_compute_rterm(nullptr, &h_rterm_, 0);
  }
}

template <typename T>
void Regularizer<T>::initialize_wgrad() {
  CudaDeviceContext context(get_device_id());
  // no regularizer
  if (!weight_tensors_ && !weight_buff_.allocated()) {
    return;
  }
  if (!wgrad_tensors_) {
    const float* weight = weight_buff_.get_ptr();
    T* wgrad = wgrad_buff_.get_ptr();
    auto num_elements = weight_buff_.get_num_elements();
    do_initialize_wgrad(weight, wgrad, num_elements, get_gpu().get_stream());
  } else {
    auto flat_weight_tensor = weight_tensors_->flatten();
    auto flat_wgrad_tensor = wgrad_tensors_->flatten();
    const float* weight = flat_weight_tensor.data();
    T* wgrad = flat_wgrad_tensor.data();
    auto num_elements = flat_weight_tensor.size(0);
    do_initialize_wgrad(weight, wgrad, num_elements, get_gpu().get_stream());
  }
}

template class Regularizer<float>;
template class Regularizer<__half>;
}  // namespace HugeCTR
