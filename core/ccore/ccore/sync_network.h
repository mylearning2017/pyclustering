#ifndef _SYNC_NETWORK_H_
#define _SYNC_NETWORK_H_

#include "interface_network.h"

#include <vector>


typedef struct sync_oscillator {
	double phase;
	double frequency;
} sync_oscillator;


typedef struct sync_dynamic {
	double time;
	double phase;
} sync_dynamic;


class sync_network : public network {
private:
	std::vector<sync_oscillator>	* oscillators;	/* oscillators						*/
	double							weight;			/* multiplier for connections		*/
	unsigned int					cluster;		/* q parameter						*/

public:
	sync_network(const unsigned int size, const double weight_factor, const double frequency_factor, const conn_type connection_type, const initial_type initial_phases);
	
	virtual ~sync_network(void);

	double sync_order(void) const;

	double sync_local_order(void) const;

	std::vector< std::vector<unsigned int> * > * allocate_sync_ensembles(const double tolerance = 0.01) const;

	std::vector< std::vector<sync_dynamic> * > * simulate(const unsigned int steps, const double time, const solve_type solver, const bool collect_dynamic);

	std::vector< std::vector<sync_dynamic> * > * simulate_static(const unsigned int steps, const double time, const solve_type solver, const bool collect_dynamic);

	std::vector<sync_dynamic> * simulate_dynamic(const double order, const solve_type solver, const bool collect_dynamic, const double step = 0.1, const double step_int = 0.01, const double threshold_changes = 0.000001);

	static double phase_normalization(const double teta);

protected:
	virtual double phase_kuramoto(const double t, const double teta, const std::vector<double> & argv);

	virtual void calculate_phases(const solve_type solver, const double t, const double step, const double int_step);
};

#endif