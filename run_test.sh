#!/bin/bash
coverage run --omit *test*.py -m lazyevaluate.test
coverage report -m