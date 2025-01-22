import { api } from "../../scripts/api.js";

function FN_NodeFeedbackHandler(event) {
    let nodes = app.graph._nodes_by_id;
    let node = nodes[event.detail.node_id];
    if (node) {
        if (event.detail.type === "text") {
            const widget = node.widgets.find((w) => w.name === event.detail.widget_name);
            if (widget) {
                widget.value = event.detail.data;
            }
        }
    }
}

api.addEventListener("fn-node-feedback", FN_NodeFeedbackHandler);


function nodeOutputLabelHandler(event) {
	let nodes = app.graph._nodes_by_id;
	let node = nodes[event.detail.node_id];
	if(node) {
		node.outputs[event.detail.output_idx].label = event.detail.label;
	}
}

api.addEventListener("fn-node-output-label", nodeOutputLabelHandler);