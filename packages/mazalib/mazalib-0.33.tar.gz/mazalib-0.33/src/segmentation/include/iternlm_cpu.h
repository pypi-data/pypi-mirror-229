#ifndef ITERNLM_CPU_H
#define ITERNLM_CPU_H

#include <iostream>
#include <math.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif
#include <algorithm>
#include <chrono>
#include <cstdint>

#include "denoise_parameters.h"

/*********************************************************************************************************************************************************
 *
 * Location: Helmholtz-Zentrum fuer Material und Kuestenforschung,
 *Max-Planck-Strasse 1, 21502 Geesthacht Author: Stefan Bruns Contact:
 *bruns@nano.ku.dk
 *
 * License: TBA
 *
 *********************************************************************************************************************************************************/

// THIS IS A CPU VERSION

namespace denoise {
class IterativeNLM_CPU {
  typedef long long int idx_type;

public:
  static float *pad_reflective(float *imagestack, int padding[6],
                               const int inshape[3], int outshape[3]);
  static float *pad_reflective_unrollpatchspace(
      float *imagestack, int padding[6], const int inshape[3], int outshape[3],
      long long int *patchpositions, int nsize_patch);

  static long long int *setup_searchspace(int shape[3],
                                          protocol::DenoiseParameters *params,
                                          int &nsize_search);
  static long long int *setup_patchspace(int shape[3],
                                         protocol::DenoiseParameters *params,
                                         int &nsize_patch);
  static float *setup_distweight(int shape[3],
                                 protocol::DenoiseParameters *params);

  // experimental stuff:
  static float *
  setup_gaussian_searchweight(float sigma, int shape[3],
                              protocol::DenoiseParameters *params);

  // keeping the whole stack in RAM
  float *Run_GaussianNoise(int iter, float *&image_raw, float *&previous_result,
                           float *sigmalist, int shape[3],
                           protocol::DenoiseParameters *params, bool verbose);

  void print_estimatedmemory(int shape[3],
                             protocol::DenoiseParameters *params) {
    int searchspace[3];
    searchspace[0] = params->radius_searchspace[0];
    searchspace[1] = params->radius_searchspace[1];
    searchspace[2] = params->radius_searchspace[2];

    int patchspace[3];
    patchspace[0] = params->radius_patchspace[0];
    patchspace[1] = params->radius_patchspace[1];
    patchspace[2] = params->radius_patchspace[2];

    int nslices3Dinfo = params->nslices;
    int n_threads = params->cpu.max_threads;

    setup_patchspace(shape, params, nsize_patch);

    int dim2padding = std::min(nslices3Dinfo / 2, searchspace[2]);

    long long int nslice = shape[0] * shape[1];
    long long int nstack = shape[2] * nslice;
    long long int nstack_blocks = n_threads * nslice;

    long long int nslice_unroll =
        (shape[0] + 2 * searchspace[0]) * (shape[1] + 2 * searchspace[1]);
    long long int nstack_unroll = (shape[2] + 2 * dim2padding) * nslice_unroll;

    long long int nslice_nounroll =
        (shape[0] + 2 * (searchspace[0] + patchspace[0])) *
        (shape[1] + 2 * (searchspace[1] + patchspace[1]));
    long long int nstack_nounroll =
        (shape[2] + 2 * (dim2padding + patchspace[2])) * nslice_nounroll;

    long long int nstack_blocks_unroll =
        (n_threads + 2 * dim2padding) * nslice_unroll;
    long long int nstack_blocks_nounroll =
        (n_threads + 2 * (dim2padding + patchspace[2])) * nslice_nounroll;

    long long int memusage_unroll =
        ((nstack_unroll * (nsize_patch + 1)) + nstack) * sizeof(float);
    long long int memusage_nounroll =
        ((nstack_nounroll * 2) + nstack) * sizeof(float);
    long long int memusage_blocks_unroll =
        ((nstack_blocks_unroll * (nsize_patch + 1)) + 2 * nstack_blocks) *
        sizeof(float);
    long long int memusage_blocks_nounroll =
        ((nstack_blocks_nounroll * 2) + 2 * nstack_blocks) * sizeof(float);

    return;
  }

private:
  int nsize_search, nsize_patch; // amount of voxels in search and patch space
  long long int *search_positions,
      *patch_positions; // idx-shift of individual search and patch positions
  float *distweight;

  long long int expected_filesize = 0;

  float expapproximation(float x) {
    return (120.f + 60.f * x + 12.f * x * x + x * x * x) /
           (120.f - 60.f * x + 12.f * x * x - x * x * x);
  } // 3rd order Pade approximation
  float expapproximation_cutoff =
      -3.56648f; // inform the compiler when the expapproximation becomes
                 // negative

  // Polynomial approximation: float expapproximation(float x)
  // {return 1.00043+x*(1.00946+x*(0.50633+x*(0.15793+x*(0.03117+x*(0.00317)))));}
  // 5th order Pade: float expapproximation(float x){float x2 = x*x; return
  // (1.f+.5f*x+.111111111f*x2+.013888889f*x2*x+.000992063f*x2*x2+.000033069f*x2*x2*x)/(1.f-.5f*x
  //													+.111111111f*x2-.013888889f*x2*x+.000992063f*x2*x2-.000033069f*x2*x2*x);}

  void filterslice(int z0, float divisor, float *image_raw,
                   float *image_prefiltered, float *result, int shape[3],
                   protocol::DenoiseParameters *params);

  // dedicated filter kernel
  void filterslice_p111(int z0, float multiplier, float *image_raw,
                        float *image_previous, float *result, int shape[3],
                        protocol::DenoiseParameters *params);
  void filterslice_p112(int z0, float multiplier, float *image_raw,
                        float *image_previous, float *result, int shape[3],
                        protocol::DenoiseParameters *params);
  void filterslice_p113(int z0, float multiplier, float *image_raw,
                        float *image_previous, float *result, int shape[3],
                        protocol::DenoiseParameters *params);
  void filterslice_p221(int z0, float multiplier, float *image_raw,
                        float *image_previous, float *result, int shape[3],
                        protocol::DenoiseParameters *params);
  void filterslice_p222(int z0, float multiplier, float *image_raw,
                        float *image_previous, float *result, int shape[3],
                        protocol::DenoiseParameters *params);
  void filterslice_p331(int z0, float multiplier, float *image_raw,
                        float *image_previous, float *result, int shape[3],
                        protocol::DenoiseParameters *params);
  void filterslice_p332(int z0, float multiplier, float *image_raw,
                        float *image_previous, float *result, int shape[3],
                        protocol::DenoiseParameters *params);
  void filterslice_p333(int z0, float multiplier, float *image_raw,
                        float *image_previous, float *result, int shape[3],
                        protocol::DenoiseParameters *params);
};
} // namespace denoise

#endif // ITERNLM_CPU_H
