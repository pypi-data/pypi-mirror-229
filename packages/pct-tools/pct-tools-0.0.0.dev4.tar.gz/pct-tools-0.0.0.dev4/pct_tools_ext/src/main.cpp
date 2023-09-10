#include "main.h"

PYBIND11_MODULE(pct_tools_ext, m) {
  //   m.doc() = "Compute projections used in power method.";

  //   auto m_io = m.def_submodule("io", "I/O for matrices and vectors.");

  m.def("store_vector", &io::store_vector, "Store a vector.");

  m.def("store_compressed_vector", &io::store_compressed_vector,
        "Compress and store a vector.");

  m.def("read_vector", &io::read_vector, "Read a vector.");

  m.def("read_compressed_vector", &io::read_compressed_vector,
        "Read a compressed vector.");

  m.def("read_compressed_matrix", &io::read_compressed_matrix,
        "Read a compressed vector.");

  m.def("construct_matrix", &io::construct_matrix,
        "Construct and store a matrix from a list of indices and values.");

  //   auto m_lip = m.def_submodule("lipschitz", "Compute Lipschitz constant.");

  m.def("compute_ATAx", &lipschitz::compute_ATAx,
        "Compute the multiplication A.T * A * x");

  //   auto m_matrix = m.def_submodule("matrix", "Compute matrix elements.");

  m.def("compute_matrix_elements", &matrix::compute_matrix_elements,
        "Compute the matrix elements for a given proton trajectory.");

  m.def("compute_matrix_elements_block", &matrix::compute_matrix_elements_block,
        "Compute the matrix elements for a given block of proton trajectories.",
        py::return_value_policy::copy);

  //   auto m_mlp = m.def_submodule("mlp", "Compute MLP.");
  m.def("compute_mlp", &mlp::compute_mlp,
        "Compute the MLP for a set of parameters.");

  //   auto m_rec = m.def_submodule("recon", "Functions for reconstruction.");
  m.def("gradient_descent", &recon::gradient_descent,
        "Compute gradient descent step.");

  //   auto m_utils = m.def_submodule("utils", "Utility functions.");
  m.def("recompress_matrix", &utils::recompress_matrix,
        "Load a matrix and store it with a given compression level.");

  m.def("subsample_matrix_vector_pair", &utils::subsample_matrix_vector_pair,
        "Subsample corresponding matrix and b-vector for a given projection "
        "angle.");
}