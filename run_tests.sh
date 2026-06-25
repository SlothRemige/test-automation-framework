#!/bin/bash
set -euo pipefail

ALLURE_DIR="allure-results"

usage() {
    cat <<EOF
Usage: ./run_tests.sh [command]

Commands:
  all         Run all tests with Allure report (default)
  api         Run API tests only
  api-p0      Run API p0 tests only
  web         Run Web tests (collected only, needs browser)
  mobile      Run Mobile tests (collected only, needs Appium)
  parallel    Run all tests with xdist parallel (auto workers)
  report      Generate Allure HTML report (requires allure CLI)
  clean       Clean allure results

Options (pass through to pytest):
  --env=staging    Switch environment

Examples:
  ./run_tests.sh api --env=staging
  ./run_tests.sh parallel
  ./run_tests.sh report
EOF
}

CMD="${1:-all}"
shift || true

case "$CMD" in
    all)
        echo "Running all tests with Allure..."
        pytest --alluredir="$ALLURE_DIR" "$@"
        ;;
    api)
        echo "Running API tests..."
        pytest tests/api/ --alluredir="$ALLURE_DIR" "$@"
        ;;
    api-p0)
        echo "Running API p0 tests..."
        pytest tests/api/ -m p0 --alluredir="$ALLURE_DIR" "$@"
        ;;
    web)
        echo "Running Web tests..."
        pytest tests/web/ --alluredir="$ALLURE_DIR" "$@"
        ;;
    mobile)
        echo "Running Mobile tests..."
        pytest tests/mobile/ --alluredir="$ALLURE_DIR" "$@"
        ;;
    parallel)
        echo "Running all tests in parallel..."
        pytest -n auto --alluredir="$ALLURE_DIR" "$@"
        ;;
    report)
        echo "Generating Allure HTML report..."
        allure generate "$ALLURE_DIR" -o allure-report --clean
        echo "Report generated at: allure-report/index.html"
        ;;
    clean)
        echo "Cleaning allure results..."
        rm -rf "$ALLURE_DIR" allure-report
        ;;
    *)
        usage
        exit 1
        ;;
esac
