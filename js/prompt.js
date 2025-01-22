import { ComfyApp, app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const originalQueuePrompt = api.queuePrompt;

async function queuePrompt_with_widget_idxs(number, { output, workflow }) {
    workflow.widget_idx_map = {};

    // Populate widget_idx_map with relevant widget indices

	for(let i in app.graph._nodes_by_id) {
		let widgets = app.graph._nodes_by_id[i].widgets;
		if(widgets) {
			for(let j in widgets) {
				if(['seed', 'noise_seed'].includes(widgets[j].name)
					&& widgets[j].type != 'converted-widget') {
					if(workflow.widget_idx_map[i] == undefined) {
						workflow.widget_idx_map[i] = {};
					}

					workflow.widget_idx_map[i][widgets[j].name] = parseInt(j);
				}
			}
		}
	}
	console.log("Mapping widgets in queuePrompt_with_widget_idxs:", workflow.widget_idx_map);
    return await originalQueuePrompt.call(api, number, { output, workflow });

}

// Override the default queuePrompt function
api.queuePrompt = queuePrompt_with_widget_idxs;

// Register the extension (optional logging for debugging)
app.registerExtension({
    name: "Comfy.FN.Seeds",
    nodeCreated(node, app) {
		if (node.comfyClass == "Global Seed Controller (Focus Nodes)") {
			console.log("Global Seed Controller (Focus Nodes) node created:", node);
        }
    }
});
