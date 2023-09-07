#include <iostream>
#ifdef _OPENMP
    #include <omp.h>
#endif
#include <sys/types.h>
#include <sys/stat.h>
#include <fstream>

#include "auxiliary.h"

#include "noiselevel.h"
#include "iternlm_cpu.h"

using namespace std;

/*********************************************************************************************************************************************************
 *
 * Location: Helmholtz-Zentrum fuer Material und Kuestenforschung, Max-Planck-Strasse 1, 21502 Geesthacht
 * Author: Stefan Bruns
 * Contact: bruns@nano.ku.dk
 * Edited by: Roman V. Vasilyev, Mail.ru Group
 * Contact: vasilyev.rw@gmail.com
 *
 * License: TBA
 *
 *********************************************************************************************************************************************************/

 // THIS IS A CPU VERSION

template<typename T>
T* nlm_denoise(const T* data_ptr, int shape[3], int n_iterations, int search_radius, bool verbose)
{
	protocol::DenoiseParameters params;
#ifdef _OPENMP
	params.cpu.max_threads = omp_get_max_threads();
#else
	params.cpu.max_threads = 1;
#endif
	params.maxiterations = n_iterations;
	params.radius_searchspace[0] = search_radius;
	params.radius_searchspace[1] = search_radius;
	params.radius_searchspace[2] = search_radius;
	int data_len = shape[0] * shape[1] * shape[2];
	float* tmp_data = new float[data_len];
	float* current = tmp_data;
	const T* current_input = data_ptr;
	for (size_t vx = 0; vx < data_len; vx++)
	{
		*current = static_cast<float>(*current_input);
		current++;
		current_input++;
	}

	float* output = nullptr;

	denoise::IterativeNLM_CPU iternlm;
	if (verbose)
	{
		iternlm.print_estimatedmemory(shape, &params);
		//cout << "--------------------------------------------------" << endl;
	}

	noise::NoiseLevel noise(params.noiselevel.n_samples, params.noiselevel.patchsize, shape);
	for (int iter = 1; iter <= params.maxiterations; iter++)
	{
		//cout << "Iteration " << iter << endl;
		float* noise_level = noise.get_noiselevel(tmp_data, &params);
		output = iternlm.Run_GaussianNoise(iter, tmp_data, output, noise_level, shape, &params, verbose);
	}

	// reverse transfer
	current = output;
	T* result = new T[data_len];
	T* current_output = result;
	for (size_t vx = 0; vx < data_len; vx++)
	{
		*current_output = static_cast<T>(round(*current));
		current++;
		current_output++;
	}
	delete[] tmp_data;
	free(output);
	return result;
}
