import { app } from "../../scripts/app.js";


app.registerExtension({
    name: "Comfy.Focus",
    nodeCreated(node, app) {
        if (node.comfyClass === "Global Seed Controller (Focus Nodes)") {
            console.log("FN Global Seed node created:", node);
        }
        register_splitter(node, app);
    }
});
