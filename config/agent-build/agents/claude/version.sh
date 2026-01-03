#!/usr/bin/env bash
set -euo pipefail

# Use npm to determine version despite installing with non-rpm
# Reason: Claude infrastructure reports wrong/old version
#
# The official installer way leads to this url:
# https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases/stable
# but there this version is reported:
# 2.0.67
# while actually this version is currently correct:
# 2.0.76
#
# See bug: https://github.com/anthropics/claude-code/issues/13888
#
# The official installer is preferred as only then does Claude support syntax-highlighting

npm view @anthropic-ai/claude-code version
