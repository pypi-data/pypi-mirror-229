#include "exact_chord_matrix.h"

using namespace matrix;

float distance_to_boundary(float const &position,
                           float const *const &boundary_positions,
                           int const &n_boundary_pointsm, int const &index,
                           int const &max_index) {

  float min_distance_to_boundary = std::numeric_limits<float>::max();
  float boundary_position = 0.0f;

  int start_index = index - 20;
  int end_index = index + 20;

  if (start_index < 0)
    start_index = 0;

  if (end_index > max_index)
    end_index = max_index;

  for (int i = start_index; i < end_index + 1; i++) {
    float distance_to_boundary = std::abs(position - boundary_positions[i]);

    if (distance_to_boundary < min_distance_to_boundary) {
      min_distance_to_boundary = distance_to_boundary;
    }
  }
  return min_distance_to_boundary;
}

bool in_img_space(int const &i, int const &j, int const &k,
                  py::tuple const &img_shape) {
  bool is_inside_space_i = (0 <= i) && (i < py::cast<int>(img_shape[0]));
  bool is_inside_space_j = (0 <= j) && (j < py::cast<int>(img_shape[1]));
  bool is_inside_space_k = (0 <= k) && (k < py::cast<int>(img_shape[2]));

  return is_inside_space_i && is_inside_space_j && is_inside_space_k;
}

bool in_img_space(int const &i, int const &j, int const &k, int const &i_max,
                  int const &j_max, int const &k_max) {
  return 0 <= i && i < i_max && 0 <= j && j < j_max && 0 <= k && k < k_max;
}

long long flat_index(int const &i, int const &j, int const &k,
                     py::tuple const &img_shape) {
  int const i_max = py::cast<int>(img_shape[0]);
  int const j_max = py::cast<int>(img_shape[1]);
  int const k_max = py::cast<int>(img_shape[2]);
  return i * j_max * k_max + j * k_max + k;
}

long long flat_index(int const &i, int const &j, int const &k, int const &i_max,
                     int const &j_max, int const &k_max) {
  return i * j_max * k_max + j * k_max + k;
}

int sign(float const &x) { return std::copysign(1.0, x); }

py::array_t<float> matrix::compute_matrix_elements(
    py::array_t<float> const &x_array, py::array_t<float> const &y_array,
    py::array_t<float> const &z_array, py::array_t<float> const &x_boundaries,
    py::array_t<float> const &y_boundaries,
    py::array_t<float> const &z_boundaries, py::tuple const &img_shape,
    py::tuple const &coord_origin, float const &pixel_width,
    float const &slice_thickness) {
  py::buffer_info x_buf = x_array.request();
  py::buffer_info y_buf = y_array.request();
  py::buffer_info z_buf = z_array.request();

  int const n_x = x_buf.shape[0];
  int const n_y = y_buf.shape[0];
  int const n_z = z_buf.shape[0];

  float const *const x = static_cast<float *>(x_buf.ptr);
  float const *const y = static_cast<float *>(y_buf.ptr);
  float const *const z = static_cast<float *>(z_buf.ptr);

  py::buffer_info xb_buf = x_boundaries.request();
  py::buffer_info yb_buf = y_boundaries.request();
  py::buffer_info zb_buf = z_boundaries.request();

  float const *const xb = static_cast<float *>(xb_buf.ptr);
  float const *const yb = static_cast<float *>(yb_buf.ptr);
  float const *const zb = static_cast<float *>(zb_buf.ptr);

  const float origin_x = py::cast<float>(coord_origin[0]);
  const float origin_y = py::cast<float>(coord_origin[1]);
  const float origin_z = py::cast<float>(coord_origin[2]);

  const int i_max = py::cast<int>(img_shape[0]);
  const int j_max = py::cast<int>(img_shape[1]);
  const int k_max = py::cast<int>(img_shape[2]);

  if (i_max < j_max || i_max < k_max) {
    throw std::runtime_error(
        "The given image shape seems to be incorrect as dimension 1 should not "
        "be larger than dimensions 2 or 3.");
  }

  size_t const size = i_max * j_max * k_max;
  float *mat = new float[size];
  for (size_t i = 0; i < size; i++)
    mat[i] = 0.0f;

  for (int i = 0; i < n_z - 1; i++) {

    float const dx = x[i + 1] - x[i];
    float const dy = y[i + 1] - y[i];
    float const dz = z[i + 1] - z[i];

    int const i_1 = std::floor((y[i] - origin_y) / slice_thickness);
    int const j_1 = std::floor((x[i] - origin_x) / pixel_width);
    int const k_1 = std::floor((z[i] - origin_z) / pixel_width);

    int const i_2 = std::floor((y[i + 1] - origin_y) / slice_thickness);
    int const j_2 = std::floor((x[i + 1] - origin_x) / pixel_width);
    int const k_2 = std::floor((z[i + 1] - origin_z) / pixel_width);

    int i_inter = i_1;
    int j_inter = j_1;
    int k_inter = k_1;

    int const di = i_2 - i_1;
    int const dj = j_2 - j_1;
    int const dk = k_2 - k_1;

    float const dyb_1 = distance_to_boundary(y[i], yb, n_y, i_1, i_max);
    float const dxb_1 = distance_to_boundary(x[i], xb, n_x, j_1, j_max);
    float const dzb_1 = distance_to_boundary(z[i], zb, n_z, k_1, k_max);

    float const dyb_2 = distance_to_boundary(y[i + 1], yb, n_y, i_2, i_max);
    float const dxb_2 = distance_to_boundary(x[i + 1], xb, n_x, j_2, j_max);
    float const dzb_2 = distance_to_boundary(z[i + 1], zb, n_z, k_2, k_max);

    bool debug_condition = (i_1 == 1 || i_2 == 1) &&
                           (j_1 == 317 || j_2 == 317) &&
                           (k_1 == 475 || k_2 == 475);

    debug_condition = false;

    if (debug_condition) {
      std::cout << "--------------" << std::endl;
      std::cout << "i: " << i << std::endl;
      std::cout << "p1: (" << i_1 << ", " << j_1 << ", " << k_1 << ")"
                << std::endl;
      std::cout << "p2: (" << i_2 << ", " << j_2 << ", " << k_2 << ")"
                << std::endl;
      std::cout << "delta: (" << di << ", " << dj << ", " << dk << ")"
                << std::endl;
    }

    if (!in_img_space(i_1, j_1, k_1, i_max, j_max, k_max) &&
        !in_img_space(i_2, j_2, k_2, i_max, j_max, k_max)) {
      continue;
    }

    // crossing no boundaries
    if (di == 0 && dj == 0 && dk == 0 &&
        in_img_space(i_1, j_1, k_1, i_max, j_max, k_max)) {
      mat[flat_index(i_1, j_1, k_1, i_max, j_max, k_max)] +=
          std::sqrt(std::pow(dx, 2) + std::pow(dy, 2) + std::pow(dz, 2));

      if (debug_condition) {
        std::cout << "chord: "
                  << std::sqrt(std::pow(dx, 2) + std::pow(dy, 2) +
                               std::pow(dz, 2))
                  << std::endl;
      }
      continue;
    }

    float chord_in_pixel1;
    float chord_in_pixel2;

    float xb_to_p1;
    float yb_to_p1;
    float zb_to_p1;

    float xb_to_p2;
    float yb_to_p2;
    float zb_to_p2;

    float const chord_x =
        std::sqrt(1 + std::pow(dy / dx, 2) + std::pow(dz / dx, 2));
    float const chord_y =
        std::sqrt(1 + std::pow(dx / dy, 2) + std::pow(dz / dy, 2));
    float const chord_z =
        std::sqrt(1 + std::pow(dx / dz, 2) + std::pow(dy / dz, 2));

    // crossing 1 boundary
    if (di != 0 && dj == 0 && dk == 0) {
      chord_in_pixel1 = std::abs(dyb_1) * chord_y;
      chord_in_pixel2 = std::abs(dyb_2) * chord_y;

      if (debug_condition) {
        std::cout << "crossed y boundary" << std::endl;
        std::cout << "chord_in_pixel1: " << chord_in_pixel1 << std::endl;
        std::cout << "chord_in_pixel2: " << chord_in_pixel2 << std::endl;
      }
    } else if (di == 0 && dj == 0 && dk != 0) {
      chord_in_pixel1 = std::abs(dzb_1) * chord_z;
      chord_in_pixel2 = std::abs(dzb_2) * chord_z;

      if (debug_condition) {
        std::cout << "crossed z boundary" << std::endl;
        std::cout << "chord_in_pixel1: " << chord_in_pixel1 << std::endl;
        std::cout << "chord_in_pixel2: " << chord_in_pixel2 << std::endl;
      }
    } else if (di == 0 && dj != 0 && dk == 0) {
      chord_in_pixel1 = std::abs(dxb_1) * chord_x;
      chord_in_pixel2 = std::abs(dxb_2) * chord_x;

      if (debug_condition) {
        std::cout << "crossed x boundary" << std::endl;
        std::cout << "chord_in_pixel1: " << chord_in_pixel1 << std::endl;
        std::cout << "chord_in_pixel2: " << chord_in_pixel2 << std::endl;
      }
    }

    // crossing 2 boundaries
    else if (di != 0 && dj == 0 && dk != 0) {
      yb_to_p1 = dyb_1 * chord_y;
      zb_to_p1 = dzb_1 * chord_z;

      yb_to_p2 = dyb_2 * chord_y;
      zb_to_p2 = dzb_2 * chord_z;

      float yb_to_zb = std::sqrt(
          std::pow(sign(dy) * dyb_1 - dy / std::abs(dz) * dzb_1, 2) +
          std::pow(sign(dz) * dzb_1 - dx / std::abs(dy) * dyb_1, 2) +
          std::pow(dx / std::abs(dz) * dzb_1 - dx / std::abs(dy) * dyb_1, 2));

      if (yb_to_p1 < zb_to_p1) {
        chord_in_pixel1 = yb_to_p1;
        chord_in_pixel2 = zb_to_p2;
        i_inter += sign(dy);
      } else if (zb_to_p1 < yb_to_p1) {
        chord_in_pixel1 = zb_to_p1;
        chord_in_pixel2 = yb_to_p2;
        k_inter += sign(dz);
      } else {
        chord_in_pixel1 = zb_to_p1;
        chord_in_pixel2 = 0.0;
        yb_to_zb = 0.0;
      }

      if (debug_condition) {
        std::cout << "yb_to_p1: " << yb_to_p1 << std::endl;
        std::cout << "zb_to_p1: " << zb_to_p1 << std::endl;
        std::cout << "yb_to_p2: " << yb_to_p2 << std::endl;
        std::cout << "zb_to_p2: " << zb_to_p2 << std::endl;
        std::cout << "yb_to_zb: " << yb_to_zb << std::endl;
        std::cout << "chord_in_pixel1: " << chord_in_pixel1 << std::endl;
        std::cout << "chord_in_pixel2: " << chord_in_pixel2 << std::endl;
      }

      if (in_img_space(i_inter, j_inter, k_inter, i_max, j_max, k_max)) {
        mat[flat_index(i_inter, j_inter, k_inter, i_max, j_max, k_max)] +=
            yb_to_zb;
      }
    }

    else if (di == 0 && dj != 0 && dk != 0) {
      xb_to_p1 = dxb_1 * chord_x;
      zb_to_p1 = dzb_1 * chord_z;

      xb_to_p2 = dxb_2 * chord_x;
      zb_to_p2 = dzb_2 * chord_z;

      float xb_to_zb = std::sqrt(
          std::pow(sign(dx) * dxb_1 - dx / std::abs(dz) * dzb_1, 2) +
          std::pow(sign(dz) * dzb_1 - dy / std::abs(dx) * dxb_1, 2) +
          std::pow(dy / std::abs(dz) * dzb_1 - dy / std::abs(dx) * dxb_1, 2));

      if (xb_to_p1 < zb_to_p1) {
        chord_in_pixel1 = xb_to_p1;
        chord_in_pixel2 = zb_to_p2;
        j_inter += sign(dx);
      } else if (zb_to_p1 < xb_to_p1) {
        chord_in_pixel1 = zb_to_p1;
        chord_in_pixel2 = xb_to_p2;
        k_inter += sign(dz);
      } else {
        chord_in_pixel1 = xb_to_p1;
        chord_in_pixel2 = 0.0;
        xb_to_zb = 0.0;
      }

      if (debug_condition) {
        std::cout << "xb_to_p1: " << xb_to_p1 << std::endl;
        std::cout << "zb_to_p1: " << zb_to_p1 << std::endl;
        std::cout << "xb_to_p2: " << xb_to_p2 << std::endl;
        std::cout << "zb_to_p2: " << zb_to_p2 << std::endl;
        std::cout << "xb_to_zb: " << xb_to_zb << std::endl;
        std::cout << "chord_in_pixel1: " << chord_in_pixel1 << std::endl;
        std::cout << "chord_in_pixel2: " << chord_in_pixel2 << std::endl;
        std::cout << "i_inter: " << i_inter << std::endl;
        std::cout << "j_inter: " << j_inter << std::endl;
        std::cout << "k_inter: " << k_inter << std::endl;
      }

      if (in_img_space(i_inter, j_inter, k_inter, i_max, j_max, k_max)) {
        mat[flat_index(i_inter, j_inter, k_inter, i_max, j_max, k_max)] +=
            xb_to_zb;
      }
    }

    else if (di != 0 && dj != 0 && dk == 0) {
      yb_to_p1 = dyb_1 * chord_y;
      xb_to_p1 = dxb_1 * chord_x;

      yb_to_p2 = dyb_2 * chord_y;
      xb_to_p2 = dxb_2 * chord_x;

      float yb_to_xb = std::sqrt(
          std::pow(sign(dy) * dyb_1 - dy / std::abs(dx) * dxb_1, 2) +
          std::pow(sign(dx) * dxb_1 - dz / std::abs(dy) * dyb_1, 2) +
          std::pow(dz / std::abs(dx) * dxb_1 - dz / std::abs(dy) * dyb_1, 2));

      if (yb_to_p1 < xb_to_p1) {
        chord_in_pixel1 = yb_to_p1;
        chord_in_pixel2 = xb_to_p2;
        i_inter += sign(dy);
      } else if (xb_to_p1 < yb_to_p1) {
        chord_in_pixel1 = xb_to_p1;
        chord_in_pixel2 = yb_to_p2;
        j_inter += sign(dx);
      } else {
        chord_in_pixel1 = yb_to_p1;
        chord_in_pixel2 = 0.0;
        yb_to_xb = 0.0;
      }

      if (in_img_space(i_inter, j_inter, k_inter, i_max, j_max, k_max)) {
        mat[flat_index(i_inter, j_inter, k_inter, i_max, j_max, k_max)] +=
            yb_to_xb;
      }
    }

    // crossing 3 boundaries
    else if (di != 0 && dj != 0 && dz != 0) {
      yb_to_p1 = dyb_1 * chord_y;
      zb_to_p1 = dzb_1 * chord_z;

      yb_to_p2 = dyb_2 * chord_y;
      zb_to_p2 = dzb_2 * chord_z;

      float yb_to_zb = std::sqrt(
          std::pow(sign(dy) * dyb_1 - dy / std::abs(dz) * dzb_1, 2) +
          std::pow(sign(dz) * dzb_1 - dz / std::abs(dy) * dyb_1, 2) +
          std::pow(dx / std::abs(dz) * dzb_1 - dx / std::abs(dy) * dyb_1, 2));

      if (yb_to_p1 < zb_to_p1) {
        chord_in_pixel1 = yb_to_p1;
        chord_in_pixel2 = zb_to_p2;
        i_inter += sign(dy);
      } else if (zb_to_p1 < yb_to_p1) {
        chord_in_pixel1 = zb_to_p1;
        chord_in_pixel2 = yb_to_p2;
        k_inter += sign(dz);
      } else {
        chord_in_pixel1 = yb_to_p1;
        chord_in_pixel2 = 0.0;
        yb_to_zb = 0.0;
      }

      if (in_img_space(i_inter, j_inter, k_inter, i_max, j_max, k_max)) {
        mat[flat_index(i_inter, j_inter, k_inter, i_max, j_max, k_max)] +=
            yb_to_zb;
      }
    }

    if (in_img_space(i_1, j_1, k_1, i_max, j_max, k_max)) {
      mat[flat_index(i_1, j_1, k_1, i_max, j_max, k_max)] += chord_in_pixel1;
    }

    if (in_img_space(i_2, j_2, k_2, i_max, j_max, k_max)) {
      mat[flat_index(i_2, j_2, k_2, i_max, j_max, k_max)] += chord_in_pixel2;
    }
  }

  return py::array_t<float>({i_max, j_max, k_max}, mat);
}

// std::tuple<std::vector<int>, std::vector<int>, std::vector<float>>
void matrix::compute_matrix_elements_block(
    std::string const &filename, py::array_t<float> const &x_array,
    py::array_t<float> const &y_array, py::array_t<float> const &z_array,
    py::array_t<float> const &x_boundaries,
    py::array_t<float> const &y_boundaries,
    py::array_t<float> const &z_boundaries, py::tuple const &img_shape,
    py::tuple const &coord_origin, float const &pixel_width,
    float const &slice_thickness) {

  py::buffer_info x_buf = x_array.request();
  py::buffer_info y_buf = y_array.request();
  py::buffer_info z_buf = z_array.request();

  int const n_x = x_buf.shape[1];
  int const n_y = y_buf.shape[1];
  int const n_z = z_buf.shape[1];

  int const block_size = x_buf.shape[0];
  int const sub_array_size = n_x;

  float const *const x_block = static_cast<float *>(x_buf.ptr);
  float const *const y_block = static_cast<float *>(y_buf.ptr);
  float const *const z_block = static_cast<float *>(z_buf.ptr);

  py::buffer_info xb_buf = x_boundaries.request();
  py::buffer_info yb_buf = y_boundaries.request();
  py::buffer_info zb_buf = z_boundaries.request();

  float const *const xb = static_cast<float *>(xb_buf.ptr);
  float const *const yb = static_cast<float *>(yb_buf.ptr);
  float const *const zb = static_cast<float *>(zb_buf.ptr);

  float const origin_x = py::cast<float>(coord_origin[0]);
  float const origin_y = py::cast<float>(coord_origin[1]);
  float const origin_z = py::cast<float>(coord_origin[2]);

  int const i_max = py::cast<int>(img_shape[0]);
  int const j_max = py::cast<int>(img_shape[1]);
  int const k_max = py::cast<int>(img_shape[2]);

  // estimate n of non-zeros as image width times number of blocks and add 25%
  int const n_nonzero_approx = i_max * block_size * 3;

  std::vector<Triplet> triplets_master;
  triplets_master.reserve(n_nonzero_approx);

#pragma omp parallel
  {
#pragma omp for
    for (unsigned int b = 0; b < block_size; b++) {
      int i_sparse = b;

      float *x = new float[sub_array_size];
      float *y = new float[sub_array_size];
      float *z = new float[sub_array_size];

      for (unsigned int i = 0; i < sub_array_size; i++) {
        x[i] = x_block[i + b * sub_array_size];
        y[i] = y_block[i + b * sub_array_size];
        z[i] = z_block[i + b * sub_array_size];
      }
      std::vector<Triplet> triplets;
      for (unsigned int i = 0; i < sub_array_size - 1; i++) {

        float const dx = x[i + 1] - x[i];
        float const dz = z[i + 1] - z[i];
        float const dy = y[i + 1] - y[i];

        int const i_1 = std::floor((y[i] - origin_y) / slice_thickness);
        int const j_1 = std::floor((x[i] - origin_x) / pixel_width);
        int const k_1 = std::floor((z[i] - origin_z) / pixel_width);

        int const i_2 = std::floor((y[i + 1] - origin_y) / slice_thickness);
        int const j_2 = std::floor((x[i + 1] - origin_x) / pixel_width);
        int const k_2 = std::floor((z[i + 1] - origin_z) / pixel_width);

        int i_inter = i_1;
        int j_inter = j_1;
        int k_inter = k_1;

        int const di = i_2 - i_1;
        int const dj = j_2 - j_1;
        int const dk = k_2 - k_1;

        float const dyb_1 = distance_to_boundary(y[i], yb, n_y, i_1, i_max);
        float const dxb_1 = distance_to_boundary(x[i], xb, n_x, j_1, j_max);
        float const dzb_1 = distance_to_boundary(z[i], zb, n_z, k_1, k_max);

        float const dyb_2 = distance_to_boundary(y[i + 1], yb, n_y, i_2, i_max);
        float const dxb_2 = distance_to_boundary(x[i + 1], xb, n_x, j_2, j_max);
        float const dzb_2 = distance_to_boundary(z[i + 1], zb, n_z, k_2, k_max);

        if (!in_img_space(i_1, j_1, k_1, i_max, j_max, k_max) &&
            !in_img_space(i_2, j_2, k_2, i_max, j_max, k_max)) {
          continue;
        }

        // crossing no boundaries
        if (di == 0 && dj == 0 && dk == 0 &&
            in_img_space(i_1, j_1, k_1, i_max, j_max, k_max)) {
          int j_sparse = flat_index(i_1, j_1, k_1, i_max, j_max, k_max);
          float val =
              std::sqrt(std::pow(dx, 2) + std::pow(dy, 2) + std::pow(dz, 2));
          triplets.push_back(Triplet(i_sparse, j_sparse, val));
          continue;
        }

        float chord_in_pixel1;
        float chord_in_pixel2;

        float xb_to_p1;
        float yb_to_p1;
        float zb_to_p1;

        float xb_to_p2;
        float yb_to_p2;
        float zb_to_p2;

        float const chord_x =
            std::sqrt(1 + std::pow(dy / dx, 2) + std::pow(dz / dx, 2));
        float const chord_y =
            std::sqrt(1 + std::pow(dx / dy, 2) + std::pow(dz / dy, 2));
        float const chord_z =
            std::sqrt(1 + std::pow(dx / dz, 2) + std::pow(dy / dz, 2));

        // crossing 1 boundary
        if (di != 0 && dj == 0 && dk == 0) {
          chord_in_pixel1 = std::abs(dyb_1) * chord_y;
          chord_in_pixel2 = std::abs(dyb_2) * chord_y;
        } else if (di == 0 && dj == 0 && dk != 0) {
          chord_in_pixel1 = std::abs(dzb_1) * chord_z;
          chord_in_pixel2 = std::abs(dzb_2) * chord_z;
        } else if (di == 0 && dj != 0 && dk == 0) {
          chord_in_pixel1 = std::abs(dxb_1) * chord_x;
          chord_in_pixel2 = std::abs(dxb_2) * chord_x;
        }

        // crossing 2 boundaries
        else if (di != 0 && dj == 0 && dk != 0) {
          yb_to_p1 = dyb_1 * chord_y;
          zb_to_p1 = dzb_1 * chord_z;

          yb_to_p2 = dyb_2 * chord_y;
          zb_to_p2 = dzb_2 * chord_z;

          float yb_to_zb = std::sqrt(
              std::pow(sign(dy) * dyb_1 - dy / std::abs(dz) * dzb_1, 2) +
              std::pow(sign(dz) * dzb_1 - dx / std::abs(dy) * dyb_1, 2) +
              std::pow(dx / std::abs(dz) * dzb_1 - dx / std::abs(dy) * dyb_1,
                       2));

          if (yb_to_p1 < zb_to_p1) {
            chord_in_pixel1 = yb_to_p1;
            chord_in_pixel2 = zb_to_p2;
            i_inter += sign(dy);
          } else if (zb_to_p1 < yb_to_p1) {
            chord_in_pixel1 = zb_to_p1;
            chord_in_pixel2 = yb_to_p2;
            k_inter += sign(dz);
          } else {
            chord_in_pixel1 = zb_to_p1;
            chord_in_pixel2 = 0.0;
            yb_to_zb = 0.0;
          }

          if (in_img_space(i_inter, j_inter, k_inter, i_max, j_max, k_max)) {
            int j_sparse =
                flat_index(i_inter, j_inter, k_inter, i_max, j_max, k_max);
            triplets.push_back(Triplet(i_sparse, j_sparse, yb_to_zb));
          }
        }

        else if (di == 0 && dj != 0 && dk != 0) {
          xb_to_p1 = dxb_1 * chord_x;
          zb_to_p1 = dzb_1 * chord_z;

          xb_to_p2 = dxb_2 * chord_x;
          zb_to_p2 = dzb_2 * chord_z;

          float xb_to_zb = std::sqrt(
              std::pow(sign(dx) * dxb_1 - dx / std::abs(dz) * dzb_1, 2) +
              std::pow(sign(dz) * dzb_1 - dy / std::abs(dx) * dxb_1, 2) +
              std::pow(dy / std::abs(dz) * dzb_1 - dy / std::abs(dx) * dxb_1,
                       2));

          if (xb_to_p1 < zb_to_p1) {
            chord_in_pixel1 = xb_to_p1;
            chord_in_pixel2 = zb_to_p2;
            j_inter += sign(dx);
          } else if (zb_to_p1 < xb_to_p1) {
            chord_in_pixel1 = zb_to_p1;
            chord_in_pixel2 = xb_to_p2;
            k_inter += sign(dz);
          } else {
            chord_in_pixel1 = xb_to_p1;
            chord_in_pixel2 = 0.0;
            xb_to_zb = 0.0;
          }

          if (in_img_space(i_inter, j_inter, k_inter, i_max, j_max, k_max)) {
            int j_sparse =
                flat_index(i_inter, j_inter, k_inter, i_max, j_max, k_max);
            triplets.push_back(Triplet(i_sparse, j_sparse, xb_to_zb));
          }
        }

        else if (di != 0 && dj != 0 && dk == 0) {
          yb_to_p1 = dyb_1 * chord_y;
          xb_to_p1 = dxb_1 * chord_x;

          yb_to_p2 = dyb_2 * chord_y;
          xb_to_p2 = dxb_2 * chord_x;

          float yb_to_xb = std::sqrt(
              std::pow(sign(dy) * dyb_1 - dy / std::abs(dx) * dxb_1, 2) +
              std::pow(sign(dx) * dxb_1 - dz / std::abs(dy) * dyb_1, 2) +
              std::pow(dz / std::abs(dx) * dxb_1 - dz / std::abs(dy) * dyb_1,
                       2));

          if (yb_to_p1 < xb_to_p1) {
            chord_in_pixel1 = yb_to_p1;
            chord_in_pixel2 = xb_to_p2;
            i_inter += sign(dy);
          } else if (xb_to_p1 < yb_to_p1) {
            chord_in_pixel1 = xb_to_p1;
            chord_in_pixel2 = yb_to_p2;
            j_inter += sign(dx);
          } else {
            chord_in_pixel1 = yb_to_p1;
            chord_in_pixel2 = 0.0;
            yb_to_xb = 0.0;
          }

          if (in_img_space(i_inter, j_inter, k_inter, i_max, j_max, k_max)) {
            int j_sparse =
                flat_index(i_inter, j_inter, k_inter, i_max, j_max, k_max);
            triplets.push_back(Triplet(i_sparse, j_sparse, yb_to_xb));
          }
        }

        // crossing 3 boundaries
        else if (di != 0 && dj != 0 && dz != 0) {
          yb_to_p1 = dyb_1 * chord_y;
          zb_to_p1 = dzb_1 * chord_z;

          yb_to_p2 = dyb_2 * chord_y;
          zb_to_p2 = dzb_2 * chord_z;

          float yb_to_zb = std::sqrt(
              std::pow(sign(dy) * dyb_1 - dy / std::abs(dz) * dzb_1, 2) +
              std::pow(sign(dz) * dzb_1 - dz / std::abs(dy) * dyb_1, 2) +
              std::pow(dx / std::abs(dz) * dzb_1 - dx / std::abs(dy) * dyb_1,
                       2));

          if (yb_to_p1 < zb_to_p1) {
            chord_in_pixel1 = yb_to_p1;
            chord_in_pixel2 = zb_to_p2;
            i_inter += sign(dy);
          } else if (zb_to_p1 < yb_to_p1) {
            chord_in_pixel1 = zb_to_p1;
            chord_in_pixel2 = yb_to_p2;
            k_inter += sign(dz);
          } else {
            chord_in_pixel1 = yb_to_p1;
            chord_in_pixel2 = 0.0;
            yb_to_zb = 0.0;
          }

          if (in_img_space(i_inter, j_inter, k_inter, i_max, j_max, k_max)) {
            int j_sparse =
                flat_index(i_inter, j_inter, k_inter, i_max, j_max, k_max);
            triplets.push_back(Triplet(i_sparse, j_sparse, yb_to_zb));
          }
        }

        if (in_img_space(i_1, j_1, k_1, i_max, j_max, k_max)) {
          int j_sparse = flat_index(i_1, j_1, k_1, i_max, j_max, k_max);
          triplets.push_back(Triplet(i_sparse, j_sparse, chord_in_pixel1));
        }

        if (in_img_space(i_2, j_2, k_2, i_max, j_max, k_max)) {
          int j_sparse = flat_index(i_2, j_2, k_2, i_max, j_max, k_max);
          triplets.push_back(Triplet(i_sparse, j_sparse, chord_in_pixel2));
        }
      }

#pragma omp critical
      triplets_master.insert(triplets_master.end(), triplets.begin(),
                             triplets.end());
    }
  }

  size_t const size = triplets_master.size();
  std::vector<int> row_indices;
  std::vector<int> col_indices;
  std::vector<float> values;

  for (size_t i = 0; i < size; i++) {

    if (triplets_master[i].value() > 0) {
      row_indices.push_back(triplets_master[i].row());
      col_indices.push_back(triplets_master[i].col());
      values.push_back(triplets_master[i].value());
    }
  }

  int n_cols = i_max * j_max * k_max;

  std::cout << "create mat of size " << block_size << ", " << n_cols << '\n';
  SparseMatrix mat(block_size, n_cols);

  std::cout << "set from triplets of size " << triplets_master.size() << '\n';
  mat.setFromTriplets(triplets_master.begin(), triplets_master.end());

  std::cout << "make compressed" << std::endl;
  mat.makeCompressed();
  io::store_compressed_matrix(mat, filename, 1);
  // return std::make_tuple(row_indices, col_indices, values);

  std::cout << "nonzero matrix: " << mat.nonZeros() << std::endl;
  std::cout << "matrix sum: " << mat.sum() << std::endl;
}