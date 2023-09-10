#include "mlp.h"

using namespace mlp;

std::vector<double> get_coefficients(std::string const &phantom_type) {
  std::vector<double> coefficients;

  if (phantom_type == "gammex") {
    coefficients = {4.996e-6, 1.571e-7,   -6.656e-9,
                    1.915e-9, -1.135e-10, 2.724e-12};

  } else {
    coefficients = {7.512e-6, 3.238e-7,   1.380e-8,
                    1.339e-9, -1.332e-10, 9.354e-12};
  }
  return coefficients;
}

double
compute_scattering_matrix_element_t(float const &a, float const &b,
                                    std::vector<double> const &coefficients) {
  double integral = 0.0;

  for (double n = 0; n < coefficients.size(); n++) {
    double element_1 =
        std::pow(b, 3 + n) * (1 / (3 + n) - 2 / (2 + n) + 1 / (1 + n));
    double element_2 = std::pow(a, n) * (std::pow(a, 3) / (3 + n) -
                                         2 * b * std::pow(a, 2) / (2 + n) +
                                         std::pow(b, 2) * a / (1 + n));
    integral += coefficients[n] / std::pow(10, n) * (element_1 - element_2);
  }
  double prefactor = 13.6 * (1 + 0.0038 * std::log((b - a) / 361.0));
  return prefactor * prefactor * integral / 361.0;
}

double compute_scattering_matrix_element_theta(
    float const &a, float const &b, std::vector<double> const &coefficients) {
  double integral = 0.f;

  for (double n = 0; n < coefficients.size(); n++) {
    double element_1 = std::pow(b, n + 1) / (n + 1);
    double element_2 = std::pow(a, n + 1) / (n + 1);
    integral += coefficients[n] / std::pow(10, n) * (element_1 - element_2);
  }

  double prefactor = 13.6 * (1 + 0.0038 * std::log((b - a) / 361.0));
  return prefactor * prefactor * integral / 361.0;
}

double compute_scattering_matrix_element_cross_term(
    float const &a, float const &b, std::vector<double> const &coefficients) {
  double integral = 0.f;

  for (double n = 0; n < coefficients.size(); n++) {
    double element_1 = std::pow(b, n + 2) * (1 / (n + 1) - 1 / (n + 2));
    double element_2 =
        b * std::pow(a, n + 1) / (n + 1) - std::pow(a, n + 2) / (n + 2);
    integral += coefficients[n] / std::pow(10, n) * (element_1 - element_2);
  }
  double prefactor = 13.6 * (1 + 0.0038 * std::log((b - a) / 361.0));
  return prefactor * prefactor * integral / 361.0;
}

Matrix2d
construct_inverse_sigma_matrix(float const &a, float const &b,
                               std::vector<double> const &coefficients) {
  double sigma_t = compute_scattering_matrix_element_t(a, b, coefficients);
  double sigma_t_theta =
      compute_scattering_matrix_element_cross_term(a, b, coefficients);
  double sigma_theta =
      compute_scattering_matrix_element_theta(a, b, coefficients);

  double determinant = sigma_t * sigma_theta - std::pow(sigma_t_theta, 2);

  if (determinant == 0) {
    determinant = 1e-30; // to avoid singular matrix
  }

  Matrix2d inverse_sigma_matrix{
      {sigma_theta / determinant, -sigma_t_theta / determinant},
      {-sigma_t_theta / determinant, sigma_t / determinant}};

  return inverse_sigma_matrix;
}

Matrix2d construct_rotation_matrix(float const &a, float const &b) {
  Matrix2d mat{{1, a - b}, {0, 1}};
  return mat;
}

VectorXf mlp::compute_mlp(std::string const &phantom_type,
                     py::array_t<float> const &z_array, float const &h_in,
                     float const &theta_in, float const &h_out,
                     float const &theta_out) {
  py::buffer_info z_buffer = z_array.request();
  int const n_z = z_buffer.shape[0];

  float const *const z = static_cast<float *>(z_buffer.ptr);

  std::vector<double> coefficients = get_coefficients(phantom_type);

  VectorXf y(n_z);
  y(0) = h_in;
  y(n_z - 1) = h_out;

  Vector2d y_in(h_in, theta_in);
  Vector2d y_out(h_out, theta_out);

  float z_in = z[0];
  float z_out = z[n_z - 1];

#pragma omp parallel for
  for (int i = 1; i < n_z - 1; i++) {
    Matrix2d inv_sigma_1 =
        construct_inverse_sigma_matrix(z_in, z[i], coefficients);

    Matrix2d inv_sigma_2 =
        construct_inverse_sigma_matrix(z[i], z_out, coefficients);

    Matrix2d r_0 = construct_rotation_matrix(z[i], z[0]);
    Matrix2d r_1 = construct_rotation_matrix(z[n_z - 1], z[i]);

    Matrix2d lhs =
        (inv_sigma_1 + r_1.transpose() * inv_sigma_2 * r_1).inverse();
    Vector2d rhs =
        (inv_sigma_1 * r_0 * y_in + r_1.transpose() * inv_sigma_2 * y_out);

    Vector2d y_i = lhs * rhs;
    y(i) = y_i(0);
  }

  return y;
}
