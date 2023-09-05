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

#include <core23_helper.hpp>
#include <data_readers/async_reader/async_reader_adapter.hpp>
#include <data_readers/data_reader.hpp>
#include <loss.hpp>
#include <metrics.hpp>
#include <optimizer.hpp>
#include <parser.hpp>

#ifdef ENABLE_MPI
#include <mpi.h>
#endif

namespace HugeCTR {
// Create data reader for InferenceSession (internal use)
template <typename TypeKey>
void create_datareader<TypeKey>::operator()(
    const InferenceParams& inference_params, const InferenceParser& inference_parser,
    std::shared_ptr<IDataReader>& data_reader,
    const std::shared_ptr<ResourceManager> resource_manager,
    std::map<std::string, core23_reader::SparseInput<TypeKey>>& sparse_input_map,
    std::map<std::string, core23::Tensor>& label_dense_map, const std::string& source,
    const DataReaderType_t data_reader_type, const Check_t check_type,
    const std::vector<long long>& slot_size_array, const bool repeat_dataset,
    const long long num_samples, const DataSourceParams& data_source_params) {
  // TO DO：support multi-hot
  long long slot_sum = 0;
  std::vector<long long> slot_offset;
  for (auto slot_size : slot_size_array) {
    slot_offset.push_back(slot_sum);
    slot_sum += slot_size;
  }

  std::vector<DataReaderSparseParam> data_reader_sparse_param_array;
  for (size_t i = 0; i < inference_parser.slot_num_for_tables.size(); i++) {
    data_reader_sparse_param_array.emplace_back(inference_parser.sparse_names[i],
                                                inference_parser.max_nnz_for_tables[i], false,
                                                inference_parser.slot_num_for_tables[i]);
  }

  for (unsigned int i = 0; i < inference_parser.sparse_names.size(); i++) {
    DataReaderSparseParam param = data_reader_sparse_param_array[i];
    std::string sparse_name = inference_parser.sparse_names[i];
    core23_reader::SparseInput<TypeKey> sparse_input(param.slot_num, param.max_feature_num);
    sparse_input_map.emplace(sparse_name, sparse_input);
  }

  core23_reader::DataReader<TypeKey>* data_reader_tk = new core23_reader::DataReader<TypeKey>(
      inference_params.max_batchsize, inference_parser.label_dim, inference_parser.dense_dim,
      data_reader_sparse_param_array, resource_manager, true, 1, false, data_source_params);
  data_reader.reset(data_reader_tk);

  switch (data_reader_type) {
    case DataReaderType_t::Norm: {
      bool start_right_now = repeat_dataset;
      data_reader->create_drwg_norm(source, check_type, start_right_now);
      break;
    }
    case DataReaderType_t::Raw: {
      data_reader->create_drwg_raw(source, num_samples, false, false, true);
      break;
    }
    case DataReaderType_t::Parquet: {
#ifdef DISABLE_CUDF
      HCTR_OWN_THROW(Error_t::WrongInput, "Parquet is not supported under DISABLE_CUDF");
#else
      std::shared_ptr<Metadata> parquet_meta = std::make_shared<Metadata>();
      auto get_meta_path = [&](std::string one_parquet_file_path) -> std::string {
        std::size_t found = one_parquet_file_path.find_last_of("/\\");
        std::string metadata_path = one_parquet_file_path.substr(0, found);
        metadata_path.append("/_metadata.json");
        return metadata_path;
      };
      std::string first_file_name, buff;
      std::string metadata_path;
      std::ifstream read_stream(source, std::ifstream::in);
      if (!read_stream.is_open()) {
        HCTR_OWN_THROW(Error_t::FileCannotOpen, "file list open failed: " + source);
      }
      std::getline(read_stream, buff);
      int num_of_files = std::stoi(buff);
      if (num_of_files) {
        std::getline(read_stream, first_file_name);
        metadata_path = get_meta_path(first_file_name);
      }
      parquet_meta->reset_metadata(metadata_path);
      auto parquet_eval_max_row_group_size = parquet_meta->get_max_row_group();
      auto parquet_label_cols = parquet_meta->get_label_names().size();
      auto parquet_dense_cols = parquet_meta->get_cont_names().size();
      read_stream.close();
      HCTR_LOG(INFO, WORLD, "parquet_eval_max_row_group_size %lld\n",
               parquet_eval_max_row_group_size);
      data_reader->create_drwg_parquet(source, false, slot_offset, true,
                                       parquet_eval_max_row_group_size,
                                       parquet_dense_cols + parquet_label_cols,
                                       inference_parser.dense_dim + inference_parser.label_dim);
#endif
      break;
    }
    default: {
      assert(!"Error: no such option && should never get here!");
    }
  }

  label_dense_map.emplace(inference_parser.label_name, data_reader_tk->get_label_tensor23s()[0]);
  label_dense_map.emplace(inference_parser.dense_name, data_reader_tk->get_dense_tensor23s()[0]);

  for (unsigned int i = 0; i < inference_parser.sparse_names.size(); i++) {
    const std::string& sparse_name = inference_parser.sparse_names[i];
    const auto& sparse_input = sparse_input_map.find(sparse_name);

    sparse_input->second.evaluate_sparse_tensors =
        data_reader_tk->get_sparse_tensor23s(sparse_name);
  }
}

// Create data reader for InferenceModel (multi-GPU offline inference use)
template <typename TypeKey>
void create_datareader<TypeKey>::operator()(
    const InferenceParams& inference_params, const InferenceParser& inference_parser,
    std::shared_ptr<IDataReader>& data_reader,
    const std::shared_ptr<ResourceManager> resource_manager,
    std::map<std::string, core23_reader::SparseInput<TypeKey>>& sparse_input_map,
    std::vector<core23::Tensor>& label_tensor_list, std::vector<core23::Tensor>& dense_tensor_list,
    const std::string& source, const DataReaderType_t data_reader_type, const Check_t check_type,
    const std::vector<long long>& slot_size_array, const bool repeat_dataset,
    const DataSourceParams& data_source_params, bool read_file_seq) {
  HCTR_CHECK_HINT(label_tensor_list.size() == 0,
                  "label tensor list should be empty before creating data reader");
  HCTR_CHECK_HINT(dense_tensor_list.size() == 0,
                  "dense tensor list should be empty before creating data reader");
  HCTR_CHECK_HINT(repeat_dataset, "repeat dataset should be true for inference");
  HCTR_LOG_S(INFO, ROOT) << "Create inference data reader on "
                         << resource_manager->get_local_gpu_count() << " GPU(s)" << std::endl;
  long long slot_sum = 0;
  std::vector<long long> slot_offset;
  for (auto slot_size : slot_size_array) {
    slot_offset.push_back(slot_sum);
    slot_sum += slot_size;
  }

  std::vector<DataReaderSparseParam> data_reader_sparse_param_array;
  for (size_t i = 0; i < inference_parser.slot_num_for_tables.size(); i++) {
    data_reader_sparse_param_array.emplace_back(inference_parser.sparse_names[i],
                                                inference_parser.max_nnz_for_tables[i], false,
                                                inference_parser.slot_num_for_tables[i]);
  }

  for (unsigned int i = 0; i < inference_parser.sparse_names.size(); i++) {
    DataReaderSparseParam param = data_reader_sparse_param_array[i];
    std::string sparse_name = inference_parser.sparse_names[i];
    core23_reader::SparseInput<TypeKey> sparse_input(param.slot_num, param.max_feature_num);
    sparse_input_map.emplace(sparse_name, sparse_input);
  }

  // For Norm, there should be only one worker to ensure the correct prediction order
  const int num_workers =
      data_reader_type == DataReaderType_t::Parquet ? resource_manager->get_local_gpu_count() : 1;
  HCTR_LOG_S(INFO, ROOT) << "num of DataReader workers: " << num_workers << std::endl;

  core23_reader::DataReader<TypeKey>* data_reader_tk = new core23_reader::DataReader<TypeKey>(
      inference_params.max_batchsize, inference_parser.label_dim, inference_parser.dense_dim,
      data_reader_sparse_param_array, resource_manager, repeat_dataset, num_workers, false,
      data_source_params);  // use_mixed_precision = false
  data_reader.reset(data_reader_tk);

  switch (data_reader_type) {
    case DataReaderType_t::Norm: {
      bool start_right_now = repeat_dataset;
      data_reader->create_drwg_norm(source, check_type, start_right_now);
      break;
    }
    case DataReaderType_t::Parquet: {
#ifdef DISABLE_CUDF
      HCTR_OWN_THROW(Error_t::WrongInput, "Parquet is not supported under DISABLE_CUDF");
#else
      std::shared_ptr<Metadata> parquet_meta = std::make_shared<Metadata>();
      auto get_meta_path = [&](std::string one_parquet_file_path) -> std::string {
        std::size_t found = one_parquet_file_path.find_last_of("/\\");
        std::string metadata_path = one_parquet_file_path.substr(0, found);
        metadata_path.append("/_metadata.json");
        return metadata_path;
      };
      std::string first_file_name, buff;
      std::string metadata_path;
      std::ifstream read_stream(source, std::ifstream::in);
      if (!read_stream.is_open()) {
        HCTR_OWN_THROW(Error_t::FileCannotOpen, "file list open failed: " + source);
      }
      std::getline(read_stream, buff);
      int num_of_files = std::stoi(buff);
      if (num_of_files) {
        std::getline(read_stream, first_file_name);
        metadata_path = get_meta_path(first_file_name);
      }
      parquet_meta->reset_metadata(metadata_path);
      auto parquet_eval_max_row_group_size = parquet_meta->get_max_row_group();
      auto parquet_label_cols = parquet_meta->get_label_names().size();
      auto parquet_dense_cols = parquet_meta->get_cont_names().size();
      read_stream.close();
      HCTR_LOG(INFO, WORLD, "parquet_eval_max_row_group_size %lld\n",
               parquet_eval_max_row_group_size);
      data_reader->create_drwg_parquet(source, read_file_seq, slot_offset, true,
                                       parquet_eval_max_row_group_size,
                                       parquet_dense_cols + parquet_label_cols,
                                       inference_parser.dense_dim + inference_parser.label_dim);
#endif
      break;
    }
    default: {
      assert(!"Error: no such option && should never get here!");
    }
  }

  for (size_t i = 0; i < resource_manager->get_local_gpu_count(); i++) {
    label_tensor_list.push_back(data_reader_tk->get_label_tensor23s()[i]);
    dense_tensor_list.push_back(data_reader_tk->get_dense_tensor23s()[i]);
  }

  for (unsigned int i = 0; i < inference_parser.sparse_names.size(); i++) {
    const std::string& sparse_name = inference_parser.sparse_names[i];
    const auto& sparse_input = sparse_input_map.find(sparse_name);
    sparse_input->second.evaluate_sparse_tensors =
        data_reader_tk->get_sparse_tensor23s(sparse_name);
  }
}

template struct create_datareader<long long>;
template struct create_datareader<unsigned int>;

}  // namespace HugeCTR
