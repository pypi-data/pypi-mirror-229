#include "io.h"
using namespace io;

void io::store_matrix(SparseMatrix &m, std::string const &filename) {
  m.makeCompressed();

  std::fstream os;
  os.open(filename, std::ios::binary | std::ios::out);

  if (!os.is_open()) {
    throw std::runtime_error("Could not open file " + filename);
  }

  StorageIndex rows, cols, nnzs, outS, innS;
  rows = m.rows();
  cols = m.cols();
  nnzs = m.nonZeros();
  outS = m.outerSize();
  innS = m.innerSize();

  os.write((const char *)&(rows), sizeof(StorageIndex));
  os.write((const char *)&(cols), sizeof(StorageIndex));
  os.write((const char *)&(nnzs), sizeof(StorageIndex));
  os.write((const char *)&(innS), sizeof(StorageIndex));
  os.write((const char *)&(outS), sizeof(StorageIndex));

  os.write((const char *)(m.valuePtr()), sizeof(float) * m.nonZeros());
  os.write((const char *)(m.outerIndexPtr()),
           sizeof(StorageIndex) * m.outerSize());
  os.write((const char *)(m.innerIndexPtr()),
           sizeof(StorageIndex) * m.nonZeros());
  os.close();
}

void io::store_vector(VectorXf const &vec, std::string const &filename) {
  std::fstream os;
  os.open(filename, std::ios::binary | std::ios::out);

  if (!os.is_open()) {
    throw std::runtime_error("Could not open file " + filename);
  }

  int rows = vec.size();
  os.write((const char *)&(rows), sizeof(int));
  os.write((const char *)vec.data(), sizeof(float) * rows);
  os.close();
}

void io::store_compressed_matrix(SparseMatrix &m, std::string const &filename,
                             int const &compression_level) {
  m.makeCompressed();

  std::fstream os;
  os.open(filename, std::ios::binary | std::ios::out);

  if (!os.is_open()) {
    throw std::runtime_error("Could not open file " + filename);
  }

  StorageIndex const rows = m.rows();
  StorageIndex const cols = m.cols();
  StorageIndex const nnz = m.nonZeros();
  StorageIndex const outS = m.outerSize();

  os.write((char const *const)&(rows), sizeof(StorageIndex));
  os.write((char const *const)&(cols), sizeof(StorageIndex));
  os.write((char const *const)&(nnz), sizeof(StorageIndex));
  os.write((char const *const)&(outS), sizeof(StorageIndex));

  size_t const vals_bytes_in = sizeof(float) * nnz;
  size_t const vals_bytes_out = sizeof(float) * nnz;
  char *const compressed_vals = new char[vals_bytes_out];
  int const compressed_vals_bytes = blosc1_compress(
      compression_level, BLOSC_BITSHUFFLE, sizeof(float), vals_bytes_in,
      m.valuePtr(), compressed_vals, vals_bytes_out);

  size_t const oindex_bytes_in = sizeof(StorageIndex) * outS;
  size_t const oindex_bytes_out = sizeof(StorageIndex) * outS;
  char *const compressed_oindex = new char[oindex_bytes_out];
  int const compressed_oindex_bytes = blosc1_compress(
      compression_level, BLOSC_BITSHUFFLE, sizeof(StorageIndex),
      oindex_bytes_in, m.outerIndexPtr(), compressed_oindex, oindex_bytes_out);

  size_t const iindex_bytes_in = sizeof(StorageIndex) * nnz;
  size_t const iindex_bytes_out = sizeof(StorageIndex) * nnz;
  char *const compressed_iindex = new char[iindex_bytes_out];
  int const compressed_iindex_bytes = blosc1_compress(
      compression_level, BLOSC_BITSHUFFLE, sizeof(StorageIndex),
      iindex_bytes_in, m.innerIndexPtr(), compressed_iindex, iindex_bytes_out);

  std::cout << "----------------------------------------------" << std::endl;
  std::cout << "COMPRESSION RESULTS" << '\n';
  std::cout << "values: " << (int64_t)vals_bytes_in << " bytes in, "
            << compressed_vals_bytes << " bytes out, ratio = "
            << (1. * (double)vals_bytes_in) / compressed_vals_bytes << '\n';

  std::cout << "oindex: " << (int64_t)oindex_bytes_in << " bytes in, "
            << compressed_oindex_bytes << " bytes out, ratio = "
            << (1. * (double)oindex_bytes_in) / compressed_oindex_bytes << '\n';

  std::cout << "iindex: " << (int64_t)iindex_bytes_in << " bytes in, "
            << compressed_iindex_bytes << " bytes out, ratio = "
            << (1. * (double)iindex_bytes_in) / compressed_iindex_bytes << '\n';

  os.write((char const *const)&(compressed_vals_bytes), sizeof(int));
  os.write((char const *const)&(compressed_oindex_bytes), sizeof(int));
  os.write((char const *const)&(compressed_iindex_bytes), sizeof(int));

  os.write(compressed_vals, compressed_vals_bytes);
  os.write(compressed_oindex, compressed_oindex_bytes);
  os.write(compressed_iindex, compressed_iindex_bytes);
  os.close();

  delete[] compressed_vals;
  delete[] compressed_oindex;
  delete[] compressed_iindex;
}

void io::store_compressed_vector(VectorXf const &vec, std::string const &filename,
                             int const &compression_level) {
  std::fstream os;
  os.open(filename, std::ios::binary | std::ios::out);

  if (!os.is_open()) {
    throw std::runtime_error("Could not open file " + filename);
  }

  int const rows = vec.size();
  os.write((char const *const)&(rows), sizeof(int));

  size_t const vals_bytes_in = sizeof(float) * rows;
  size_t const vals_bytes_out = 2 * sizeof(float) * rows;
  char *const compressed_vals = new char[vals_bytes_out];
  int const compressed_vals_bytes = blosc1_compress(
      compression_level, BLOSC_BITSHUFFLE, sizeof(float), vals_bytes_in,
      vec.data(), compressed_vals, vals_bytes_out);

  std::cout << "-------------------------" << '\n';
  std::cout << "size of vals " << sizeof(float) << '\n';
  std::cout << "rows " << vec.size() << '\n';
  std::cout << "data " << vec.data() << '\n';
  std::cout << "vals_bytes_in " << (int64_t)vals_bytes_in << '\n';
  std::cout << "compressed_vals_bytes " << compressed_vals_bytes << '\n';
  std::cout << "ratio " << (1. * (double)vals_bytes_in) / compressed_vals_bytes
            << '\n';

  os.write((char const *const)&(compressed_vals_bytes), sizeof(int));
  os.write(compressed_vals, compressed_vals_bytes);
  os.close();

  delete[] compressed_vals;
}

SparseMatrix io::read_matrix(std::string const &filename) {
  SparseMatrix mat;
  std::ifstream is(filename, std::ios::binary | std::ios::in);

  if (!is.is_open()) {
    throw std::runtime_error("Could not open file " + filename);
  }

  StorageIndex rows, cols, nnz, inSz, outSz;
  is.read((char *)&rows, sizeof(StorageIndex));
  is.read((char *)&cols, sizeof(StorageIndex));
  is.read((char *)&nnz, sizeof(StorageIndex));
  is.read((char *)&inSz, sizeof(StorageIndex));
  is.read((char *)&outSz, sizeof(StorageIndex));

  mat.resize(rows, cols);
  mat.makeCompressed();
  mat.resizeNonZeros(nnz);

  is.read((char *)mat.valuePtr(), sizeof(float) * nnz);
  is.read((char *)mat.outerIndexPtr(), sizeof(StorageIndex) * outSz);
  is.read((char *)mat.innerIndexPtr(), sizeof(StorageIndex) * nnz);

  mat.finalize();
  is.close();
  return mat;
}

VectorXf io::read_vector(std::string const &filename) {
  VectorXf vec;
  std::ifstream is(filename, std::ios::binary | std::ios::in);

  if (!is.is_open()) {
    throw std::runtime_error("Could not open file " + filename);
  }

  int rows;
  is.read((char *)&rows, sizeof(int));

  vec.resize(rows);
  is.read((char *)vec.data(), sizeof(float) * rows);
  is.close();

  return vec;
}

SparseMatrix io::read_compressed_matrix(std::string const &filename) {
  SparseMatrix mat;
  std::ifstream is(filename, std::ios::binary | std::ios::in);

  if (!is.is_open()) {
    throw std::runtime_error("Could not open file " + filename);
  }

  StorageIndex rows, cols, nnz, outS;
  int comp_vals_size, comp_oindex_size, comp_iindex_size;

  is.read((char *)&rows, sizeof(StorageIndex));
  is.read((char *)&cols, sizeof(StorageIndex));
  is.read((char *)&nnz, sizeof(StorageIndex));
  is.read((char *)&outS, sizeof(StorageIndex));
  is.read((char *)&comp_vals_size, sizeof(int));
  is.read((char *)&comp_oindex_size, sizeof(int));
  is.read((char *)&comp_iindex_size, sizeof(int));

  mat.resize(rows, cols);
  mat.makeCompressed();
  mat.resizeNonZeros(nnz);

  char *comp_vals = new char[comp_vals_size];
  char *comp_oindex = new char[comp_oindex_size];
  char *comp_iindex = new char[comp_iindex_size];

  is.read(comp_vals, comp_vals_size);
  is.read(comp_oindex, comp_oindex_size);
  is.read(comp_iindex, comp_iindex_size);

  blosc1_decompress(comp_vals, mat.valuePtr(), sizeof(float) * nnz);
  blosc1_decompress(comp_oindex, mat.outerIndexPtr(),
                    sizeof(StorageIndex) * outS);
  blosc1_decompress(comp_iindex, mat.innerIndexPtr(),
                    sizeof(StorageIndex) * nnz);

  mat.finalize();
  is.close();

  delete[] comp_vals;
  delete[] comp_oindex;
  delete[] comp_iindex;

  return mat;
}

VectorXf io::read_compressed_vector(std::string const &filename) {
  VectorXf vec;
  std::ifstream is(filename, std::ios::binary | std::ios::in);

  if (!is.is_open()) {
    throw std::runtime_error("Could not open file " + filename);
  }

  int rows, comp_vals_size;

  is.read((char *)&rows, sizeof(int));
  is.read((char *)&comp_vals_size, sizeof(int));

  vec.resize(rows);
  char *comp_vals = new char[comp_vals_size];

  is.read(comp_vals, comp_vals_size);
  blosc1_decompress(comp_vals, vec.data(), sizeof(float) * rows);
  is.close();

  delete[] comp_vals;
  return vec;
}

void io::construct_matrix(std::string const filename, py::array_t<int> const rows,
                      py::array_t<int> const cols,
                      py::array_t<float> const values,
                      py::tuple const img_shape, int const &verbose) {
  py::buffer_info rows_buffer = rows.request();
  py::buffer_info cols_buffer = cols.request();
  py::buffer_info values_buffer = values.request();

  int *row_index = static_cast<int *>(rows_buffer.ptr);
  int *col_index = static_cast<int *>(cols_buffer.ptr);
  float *vals = static_cast<float *>(values_buffer.ptr);

  int const n_rows = row_index[rows_buffer.shape[0] - 1] + 1;
  int const n_cols = py::cast<int>(img_shape[0]) * py::cast<int>(img_shape[1]) *
                     py::cast<int>(img_shape[2]);
  int const n_nonzero = values_buffer.shape[0];

  SparseMatrix mat(n_rows, n_cols);
  std::vector<Triplet> tripletList;
  tripletList.reserve(n_nonzero);

  for (int i = 0; i < rows_buffer.shape[0]; i++)
    tripletList.push_back(Triplet(row_index[i], col_index[i], vals[i]));

  if (verbose > 0) {
    std::cout << "----------------------------------------------" << std::endl;
    std::cout << "MATRIX PARAMETERS" << std::endl;
    std::cout << "image shape: (" << py::cast<int>(img_shape[0]) << ", "
              << py::cast<int>(img_shape[1]) << ", "
              << py::cast<int>(img_shape[2]) << ")" << std::endl;
    std::cout << "slices: " << py::cast<int>(img_shape[0]) << std::endl;
    std::cout << "n_rows: " << n_rows << std::endl;
    std::cout << "n_cols: " << n_cols << std::endl;
    std::cout << "n_nonzero: " << n_nonzero << std::endl;
    std::cout << "n_triplets: " << tripletList.size() << std::endl;
  }

  mat.setFromTriplets(tripletList.begin(), tripletList.end());
  mat.makeCompressed();
  store_compressed_matrix(mat, filename, 1);
}