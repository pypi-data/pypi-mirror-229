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

#include <common.hpp>
#include <hps/embedding_cache.hpp>
#include <hps/hier_parameter_server.hpp>
#include <inference/inference_session.hpp>
#include <utils.hpp>

namespace HugeCTR {

class InferenceModel {
 public:
  virtual ~InferenceModel();
  InferenceModel(const std::string& model_config_path, const InferenceParams& inference_params);
  InferenceModel(const InferenceModel&) = delete;
  InferenceModel& operator=(const InferenceModel&) = delete;

  float evaluate(size_t num_batches, const std::string& source, DataReaderType_t data_reader_type,
                 Check_t check_type, const std::vector<long long>& slot_size_array,
                 const DataSourceParams& data_source_params, bool reading_file_seq = true);

  void predict(float* pred_output, size_t num_batches, const std::string& source,
               DataReaderType_t data_reader_type, Check_t check_type,
               const std::vector<long long>& slot_size_array,
               const DataSourceParams& data_source_params, bool reading_file_seq = true);

  std::tuple<size_t, size_t, std::vector<size_t>, int> get_tensor_info_by_name(
      const std::string& tensor_name);

  void check_out_tensor(int index, float* global_result);

  const InferenceParams& get_inference_params() const { return inference_params_; }

  const InferenceParser& get_inference_parser() const { return inference_parser_; }

 private:
  InferenceParams inference_params_;
  InferenceParser inference_parser_;
  std::shared_ptr<ResourceManager> resource_manager_;

  std::vector<std::shared_ptr<InferenceSession>> inference_sessions_;
  std::shared_ptr<HierParameterServerBase> parameter_server_;
  metrics::Metrics metrics_;

  std::shared_ptr<IDataReader> data_reader_;
  std::vector<core23::Tensor> pred_tensor_list_;       // the length equals local_gpu_count
  std::vector<core23::Tensor> key_tensor_list_;        // the length equals local_gpu_count
  std::vector<core23::Tensor> rowoffset_tensor_list_;  // the length equals local_gpu_count

  std::vector<std::shared_ptr<Tensor2<float>>>
      old_pred_tensor_list_;                              // the length equals local_gpu_count
  std::vector<core23::Tensor> reader_label_tensor_list_;  // the length equals local_gpu_count
  std::vector<core23::Tensor> reader_dense_tensor_list_;  // the length equals local_gpu_count
  std::map<std::string, core23_reader::SparseInput<long long>> sparse_input_map_64_;
  std::map<std::string, core23_reader::SparseInput<unsigned int>> sparse_input_map_32_;

  std::vector<std::vector<TensorEntry>> inference_tensor_entries_list_;

  std::vector<metrics::RawMetricMap> raw_metrics_map_list_;  // the length equals local_gpu_count
  std::shared_ptr<metrics::Metric> metric_;  // currently only support AUC during inference

  const long long global_max_batch_size_;
  long long current_batch_size_{0};

  Timer timer_infer;
  Timer timer_reader;
  Timer timer_forward;

  void reset_reader_tensor_list();

  template <typename TypeKey>
  void parse_input_from_data_reader(
      const std::map<std::string, core23_reader::SparseInput<TypeKey>>& sparse_input_map,
      std::vector<core23::Tensor>& key_tensor_list,
      std::vector<core23::Tensor>& rowoffset_tensor_list);
};

}  // namespace HugeCTR
