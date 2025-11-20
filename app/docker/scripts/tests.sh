#!/bin/sh -e
DC_BUILD="docker compose -f docker-compose.test.yml build"
DC_TEST="docker compose -f docker-compose.test.yml -p auth_test"

find . -name '*.pyc' -delete

${DC_BUILD}

${DC_TEST} run backend pytest -p no:cacheprovider --capture=no $@ || true
${DC_TEST} down --remove-orphans -v
