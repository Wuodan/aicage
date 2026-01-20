#!/usr/bin/env bash
set -euo pipefail

(
	for dir in aicage-image/agents/*; do
		agent=$(basename $dir)

    image_ref=ghcr.io/aicage/aicage:$agent-ubuntu
		if grep -q 'build_local: true' aicage-image/agents/$agent/agent.yaml; then
      image_ref=aicage:$agent-ubuntu
		fi

		echo "### START: $agent ###"
		docker run --rm -it \
			-v $(pwd)/scripts/debug/debug-print-agent_path.sh:'/usr/local/bin/debug-print-agent_path.sh' \
			--entrypoint debug-print-agent_path.sh \
			$image_ref \
				$agent
		echo "### END: $agent ###"
		echo
	done
) | tee debug-print.out

