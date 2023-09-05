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
#pragma once

#include <cuda_runtime.h>

#include <cassert>
#include <core/macro.hpp>

namespace embedding {

template <typename T>
HOST_DEVICE_INLINE int64_t bs_upper_bound_sub_one(const T *const arr, int64_t num, T target) {
  int64_t start = 0;
  int64_t end = num;
  while (start < end) {
    int64_t middle = start + (end - start) / 2;
    T value = arr[middle];
    if (value <= target) {
      start = middle + 1;
    } else {
      end = middle;
    }
  }
  return (start == num && arr[start - 1] != target) ? num : start - 1;
}

template <typename T>
class ArrayView {
 public:
  using value_type = T;
  using size_type = int64_t;
  // using difference_type = ptrdiff_t;
  using reference = value_type &;
  using const_reference = value_type const &;

 private:
  using pointer = T *;
  pointer data_;
  size_type len_;

 public:
  HOST_DEVICE_INLINE ArrayView(void *data, size_type len)
      : data_(static_cast<pointer>(data)), len_(len) {}

  HOST_DEVICE_INLINE const_reference operator[](size_type index) const { return data_[index]; }

  HOST_DEVICE_INLINE reference operator[](size_type index) { return data_[index]; }

  HOST_DEVICE_INLINE size_type &size() { return len_; }
};

}  // namespace embedding
