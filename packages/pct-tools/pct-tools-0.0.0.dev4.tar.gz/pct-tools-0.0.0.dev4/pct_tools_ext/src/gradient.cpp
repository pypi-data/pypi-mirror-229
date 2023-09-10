#include "gradient.h"

using namespace recon;

std::tuple<VectorXf, float>
recon::gradient_descent(VectorXf x, float const &step_size,
                        std::vector<std::string> const &matrix_filenames,
                        std::vector<std::string> const &b_filenames) {

  if (matrix_filenames.size() != b_filenames.size()) {
    throw std::runtime_error("Number of matrices and b vectors must match!");
  }

  if (matrix_filenames[0] == b_filenames[0]) {
    throw std::runtime_error(
        "The matrix and b vector file names shouldn't match!");
  }

  unsigned int const n_cols = x.size();
  int const n_loops = matrix_filenames.size();

  // initialise shared arrays
  float *shared_grad = new float[n_cols * n_loops];
  float *shared_res_sq = new float[n_loops];

  for (unsigned int i = 0; i < n_cols * n_loops; i++)
    shared_grad[i] = 0.0f;

  for (unsigned int i = 0; i < n_loops; i++)
    shared_res_sq[i] = 0.0f;

    // compute sub-multiplications in parallel and store results in shared
    // vectors
#pragma omp parallel
  {
#pragma omp for
    for (int i = 0; i < n_loops; i++) {
      SparseMatrix const A = io::read_compressed_matrix(matrix_filenames[i]);
      VectorXf const b = io::read_vector(b_filenames[i]);

      VectorXf const Ax = A * x;
      VectorXf const grad_i = A.transpose() * (Ax - b);

      for (int j = 0; j < n_cols; j++) {
        // #pragma omp atomic
        shared_grad[j + n_cols * i] = grad_i[j];
      }
      shared_res_sq[i] = (b - Ax).transpose() * (b - Ax);
    }
  }
  // reduce shared arrays
  VectorXf grad = VectorXf::Zero(n_cols);
  for (int i = 0; i < n_loops; i++)
    for (int j = 0; j < n_cols; j++)
      grad[j] += shared_grad[j + n_cols * i];

  float res_sq = 0.0;
  for (int i = 0; i < n_loops; i++) {
    res_sq += shared_res_sq[i];
  }

  x -= step_size * grad; // make step in direction of steepest descent

  delete[] shared_grad;
  delete[] shared_res_sq;

  return std::make_tuple(x, res_sq);
}
