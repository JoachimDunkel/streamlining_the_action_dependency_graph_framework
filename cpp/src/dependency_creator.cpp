#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <tuple>
#include <utility>
#include <vector>
#include <unordered_map>
#include <algorithm>

namespace py = pybind11;

using Pos2D = std::tuple<int, int>; 

struct Action {
    Pos2D start_s;
    Pos2D goal_g;
    int time_step_t;
    int shuttle_R;
    int related_vertex_id;

    explicit Action(Pos2D start_s, Pos2D goal_g,
                    int time_step_t, int shuttle_R, int related_vertex_id)
        : start_s(std::move(start_s)), goal_g(std::move(goal_g)), 
          time_step_t(time_step_t), shuttle_R(shuttle_R),
          related_vertex_id(related_vertex_id) {}

    bool operator<(const Action& other) const {
        return time_step_t < other.time_step_t;
    }
};

void sort_actions_by_time_step(std::vector<Action>& actions) {
    std::sort(actions.begin(), actions.end());
}

enum class DepCreationMethod {
    EXHAUSTIVE,
    CP,
    SCP
};

struct Pos2DHash {
    std::size_t operator()(const Pos2D& t) const {
        return (static_cast<std::size_t>(std::get<0>(t)) << 32) | static_cast<std::size_t>(std::get<1>(t));
    }
};

typedef std::unordered_map<Pos2D, std::vector<Action>, Pos2DHash> ActionMap;

ActionMap create_candidate_action_lookup(const std::vector<Action>& all_actions) {
    ActionMap candidate_action_lookup_S;
    for (const auto& action : all_actions) {
        candidate_action_lookup_S[action.start_s].push_back(action);
    }
    return candidate_action_lookup_S;
}

std::optional<Action> find_rel_candidate(const std::vector<Action>& candidate_actions, const Action& for_this_action) {
    auto it = std::upper_bound(candidate_actions.begin(), candidate_actions.end(), for_this_action);
    if (it != candidate_actions.begin()) {
        --it;
    } else {
        return std::nullopt;
    }

    while (it >= candidate_actions.begin()) {
        const Action& candidate = *it;
        if (candidate.shuttle_R == for_this_action.shuttle_R) {
            // --it;
            // continue;
            return std::nullopt;
        }

        if (candidate.time_step_t <= for_this_action.time_step_t) {
            return candidate;
        }
        --it;
    }

    return std::nullopt;
}

std::vector<std::tuple<int, int>> create_type2_dependencies(const std::vector<Action>& all_actions, DepCreationMethod method_to_use) {
    std::vector<std::tuple<int, int>> dependencies;

    switch (method_to_use)
    {
        case DepCreationMethod::EXHAUSTIVE:
            {
                for (const auto& action_a : all_actions) {
                    for (const auto& action_b : all_actions) {
                        if (action_a.shuttle_R == action_b.shuttle_R) {
                            continue;
                        }
                        if (action_a.goal_g == action_b.start_s &&
                            action_a.time_step_t >= action_b.time_step_t) {
                            dependencies.emplace_back(action_b.related_vertex_id, action_a.related_vertex_id);
                        }
                    }
                }
            }
        break;
        case DepCreationMethod::CP:
            {
                auto candidate_action_lookup_S = create_candidate_action_lookup(all_actions);
                for (const auto& a_i : all_actions) {
                    for (const auto& c_i : candidate_action_lookup_S[a_i.goal_g])
                    {
                        if (a_i.shuttle_R == c_i.shuttle_R) {
                            continue;
                        }
                        if (c_i.time_step_t <= a_i.time_step_t) {
                            dependencies.emplace_back(c_i.related_vertex_id, a_i.related_vertex_id);
                        }
                    }
                }
            }
        break;
        case DepCreationMethod::SCP:
            {
                auto candidate_action_lookup_S = create_candidate_action_lookup(all_actions);
                for (auto& [start_pos, candidate_actions_C] : candidate_action_lookup_S) {
                    std::vector<Action>& actions = candidate_actions_C; 
                    std::sort(actions.begin(), actions.end());
                }

                for (const auto& a_i : all_actions) {
                    auto candidate_actions_C = candidate_action_lookup_S[a_i.goal_g];
                    
                    auto candidate_ck = find_rel_candidate(candidate_actions_C, a_i);
                    if (candidate_ck.has_value()) {
                        dependencies.emplace_back(candidate_ck->related_vertex_id, a_i.related_vertex_id);
                    }
                }
            }
        break;
    }
    return dependencies;
}

std::string hello_from_cpp() {
    return "hello from cpp";
}

PYBIND11_MODULE(dependency_creator, m) {
    m.def("hello_from_cpp", &hello_from_cpp, "A function that returns 'hello from cpp'");

    py::enum_<DepCreationMethod>(m, "DepCreationMethod")
        .value("EXHAUSTIVE", DepCreationMethod::EXHAUSTIVE)
        .value("CP", DepCreationMethod::CP)
        .value("SCP", DepCreationMethod::SCP);
    
    py::class_<Action>(m, "Action")
        .def(py::init<Pos2D, Pos2D, int, int, int>())
        .def_readwrite("start_s", &Action::start_s)
        .def_readwrite("goal_g", &Action::goal_g)
        .def_readwrite("time_step_t", &Action::time_step_t)
        .def_readwrite("shuttle_R", &Action::shuttle_R)
        .def_readwrite("related_vertex_id", &Action::related_vertex_id);

    m.def("create_type2_dependencies", &create_type2_dependencies, "Create Type 2 dependencies from a list of actions",
      py::arg("all_actions"), py::arg("dep_creation_method"));
}