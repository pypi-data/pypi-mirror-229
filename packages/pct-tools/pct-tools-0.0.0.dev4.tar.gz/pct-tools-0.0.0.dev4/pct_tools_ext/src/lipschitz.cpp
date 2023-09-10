#include "lipschitz.h"

using namespace lipschitz;

VectorXf lipschitz::compute_ATAx(VectorXf const x,
                                 std::vector<std::string> const &filenames) {
  unsigned int const n_cols = x.size();
  int const n_loops = filenames.size();

  // initialise shared array
  // beware of hitting the max unsigned int limit 2**32 - 1
  float *shared_array = new float[n_cols * n_loops];
  for (unsigned int i = 0; i < n_cols * n_loops; i++)
    shared_array[i] = 0.0f;

    // std::cout << "compute lipschitz" << std::endl;
    // compute sub-multiplications
#pragma omp parallel for
  for (int i = 0; i < n_loops; i++) {
    SparseMatrix A = io::read_compressed_matrix(filenames[i]);

    // if (i == 0) {
    //   std::cout << "A.size(): " << A.size() << std::endl;
    //   std::cout << "A.rows(): " << A.rows() << std::endl;
    //   std::cout << "A.cols(): " << A.cols() << std::endl;
    // }
    VectorXf Ax = A * x;
    VectorXf ATAx_i = A.transpose() * Ax;

    for (unsigned int j = 0; j < n_cols; j++) {
      // #pragma omp critical
      shared_array[j + n_cols * i] = ATAx_i[j];
    }

    // clear the matrix and vectors
    A.resize(0, 0);
    Ax.resize(0);
    ATAx_i.resize(0);
  }

  // std::cout << "reduce" << std::endl;

  // reduce the shared array
  VectorXf ATAx = VectorXf::Zero(n_cols);
  for (unsigned int i = 0; i < n_loops; i++)
    for (unsigned int j = 0; j < n_cols; j++)
      ATAx[j] += shared_array[j + n_cols * i];

  delete[] shared_array;
  return ATAx;
}
