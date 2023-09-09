#include <alpaqa/inner/directions/panoc/anderson.hpp>
#include <alpaqa/inner/directions/panoc/lbfgs.hpp>
#include <alpaqa/inner/directions/panoc/structured-lbfgs.hpp>
#include <alpaqa/inner/panoc.hpp>
#include <alpaqa/inner/zerofpr.hpp>

#include "alm-driver.hpp"
#include "cancel.hpp"
#include "panoc-driver.hpp"
#include "solver-driver.hpp"
#include "util.hpp"

namespace {

template <class T>
struct tag_t {};

template <template <class Direction> class Solver>
solver_func_t make_panoc_like_driver(std::string_view direction,
                                     [[maybe_unused]] Options &opts) {
    USING_ALPAQA_CONFIG(alpaqa::DefaultConfig);
    auto builder = []<class Direction>(tag_t<Direction>) {
        return [](std::string_view, Options &opts) -> solver_func_t {
            auto inner_solver = make_inner_solver<Solver<Direction>>(opts);
            auto solver       = make_alm_solver(std::move(inner_solver), opts);
            unsigned N_exp    = 0;
            set_params(N_exp, "num_exp", opts);
            return [solver{std::move(solver)},
                    N_exp](LoadedProblem &problem,
                           std::ostream &os) mutable -> SolverResults {
                auto cancel = alpaqa::attach_cancellation(solver);
                return run_alm_solver(problem, solver, os, N_exp);
            };
        };
    };
    std::map<std::string_view, solver_builder_func_t> builders{
        {"lbfgs", //
         builder(tag_t<alpaqa::LBFGSDirection<config_t>>())},
        {"anderson", //
         builder(tag_t<alpaqa::AndersonDirection<config_t>>())},
        {"struclbfgs", //
         builder(tag_t<alpaqa::StructuredLBFGSDirection<config_t>>())},
    };
    if (direction.empty())
        direction = "lbfgs";
    auto builder_it = builders.find(direction);
    if (builder_it != builders.end())
        return builder_it->second(direction, opts);
    else
        throw std::invalid_argument(
            "Unknown direction '" + std::string(direction) + "'\n" +
            "  Available directions: " +
            format_string_list(builders,
                               [](const auto &x) { return x.first; }));
}

} // namespace

solver_func_t make_panoc_driver(std::string_view direction, Options &opts) {
    return make_panoc_like_driver<alpaqa::PANOCSolver>(direction, opts);
}

solver_func_t make_zerofpr_driver(std::string_view direction, Options &opts) {
    return make_panoc_like_driver<alpaqa::ZeroFPRSolver>(direction, opts);
}
