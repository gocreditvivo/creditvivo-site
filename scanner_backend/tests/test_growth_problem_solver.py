from growth_problem_solver import build_problem_solver_brief, solve_growth_problem


def test_problem_solver_defines_core_skills():
    brief = build_problem_solver_brief()
    skill_names = {skill["name"] for skill in brief["skills"]}

    assert "question_triage" in skill_names
    assert "root_cause_analysis" in skill_names
    assert "solution_design" in skill_names
    assert "experiment_planning" in skill_names
    assert "answer_builder" in skill_names


def test_problem_solver_answers_scanner_completion_question():
    answer = solve_growth_problem("Why are customers not finishing the scanner?")

    assert answer["problem_type"] == "scanner_completion_problem"
    assert "scan_started" in answer["data_needed"]
    assert "scan_completed" in answer["data_needed"]
    assert "Best next move" in answer["plain_english_answer"]


def test_problem_solver_answers_ad_question():
    answer = solve_growth_problem("Which Google ads are not working?")

    assert answer["problem_type"] == "ad_performance_problem"
    assert "scan_started" in answer["data_needed"]
    assert "Owner" not in answer["plain_english_answer"]


def test_problem_solver_handles_unknown_question():
    answer = solve_growth_problem("What is the biggest unknown?")

    assert answer["problem_type"] == "general_growth_question"
    assert answer["ok"] is True
