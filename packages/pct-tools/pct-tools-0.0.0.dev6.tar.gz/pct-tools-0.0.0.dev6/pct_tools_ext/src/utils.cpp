#include "utils.h"

using namespace utils;

void utils::recompress_matrix(std::string const &filename,
                       int const &compression_level) {
  SparseMatrix mat = io::read_compressed_matrix(filename);
  io::store_compressed_matrix(
      mat, "recompressed_" + std::to_string(compression_level) + "_" + filename,
      compression_level);
}

void utils::subsample_matrix_vector_pair(std::string const &input_path,
                                  std::string const &projection_angle,
                                  std::string const &output_path,
                                  float const &ratio) {

  if (input_path == output_path) {
    throw std::runtime_error("Input and ouput path shouldn't match.");
  }

  std::string const matrix_filename =
      input_path + "/matrix/" + projection_angle + ".mat";
  SparseMatrix mat = io::read_compressed_matrix(matrix_filename);

  std::string const vector_filename =
      input_path + "/b/b_" + projection_angle + ".vec";
  VectorXf b = io::read_vector(vector_filename);

  std::cout << "reading " << matrix_filename << " and " << vector_filename
            << std::endl;

  // Sample row indices
  int n_indices = mat.rows();

  std::vector<int> indices(n_indices);
  std::iota(indices.begin(), indices.end(), 0);
  std::shuffle(indices.begin(), indices.end(),
               std::mt19937{std::random_device{}()});

  int n_samples = std::floor(ratio * mat.rows());
  std::vector<int> samples =
      std::vector<int>(indices.begin(), indices.begin() + n_samples);

  // Construct subsampled matrix
  SparseMatrix subsampled_mat(n_samples, mat.cols());
  for (int k = 0; k < n_samples; ++k)
    for (SparseMatrix::InnerIterator it(mat, samples[k]); it; ++it)
      subsampled_mat.insert(k, it.col()) = it.value();
  subsampled_mat.makeCompressed();

  // Construct subsampled vector
  VectorXf subsampled_vec(n_samples);
  for (int i = 0; i < n_samples; i++)
    subsampled_vec(i) = b(samples[i]);

  // Store matrix and b-vector
  io::store_compressed_matrix(
      subsampled_mat, output_path + "/matrix/" + projection_angle + ".mat", 1);

  io::store_vector(subsampled_vec,
               output_path + "/b/b_" + projection_angle + ".vec");
}