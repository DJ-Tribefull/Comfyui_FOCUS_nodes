import { api } from "../../scripts/api.js";

function FN_GlobalSeedHandler(event) {
	let nodes = app.graph._nodes_by_id;

	for (let i in nodes) {
		let node = nodes[i];

		// Handle 'Global Seed Controller (Focus Nodes)' nodes
		if (node.type == 'Global Seed Controller (Focus Nodes)') {
			if (node.widgets) {
				const w = node.widgets.find((w) => w.name == 'value');
				const last_w = node.widgets.find((w) => w.name == 'last_seed');
				if (w && last_w) {
					last_w.value = w.value;
					if (event.detail.value != null) {
						w.value = event.detail.value;
					}
				}
			}
		} else if (node.widgets) {
			// Handle 'seed' and 'noise_seed' widgets
			const w = node.widgets.find(
				(w) => (w.name == 'seed' || w.name == 'noise_seed') && w.type == 'number'
			);
			if (w && event.detail.seed_map[node.id] != undefined) {
				w.value = event.detail.seed_map[node.id];
			}
		}
	}
}

// Register the event listener
api.addEventListener("fn-global-seed", FN_GlobalSeedHandler);