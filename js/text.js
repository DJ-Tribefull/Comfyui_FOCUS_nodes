import { app } from '../../scripts/app.js'
import { ComfyWidgets } from '../../scripts/widgets.js'

app.registerExtension({
    name: 'Comfy.FN.TextDisplay',
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === 'Text Display (Focus Nodes)') {

            function populate(text) {
                console.log(this)
                if (this.widgets) {
                    for (let i = 1; i < this.widgets.length; i++) {
                        this.widgets[i].onRemove?.()
                    }
                    this.widgets.length = 1
                }

                const v = [...text]
                if (!v[0]) {
                    v.shift()
                }

                for (const list of v) {
                    const w = ComfyWidgets['STRING'](this, 'text', ['STRING', { multiline: true }], app).widget
                    w.inputEl.readOnly = true
                    w.inputEl.style.opacity = 0.6
                    w.value = list
                }
            }

            const onExecuted = nodeType.prototype.onExecuted
            nodeType.prototype.onExecuted = function (message) {
                onExecuted?.apply(this, arguments)
                populate.call(this, message.text)
            }

            const onConfigure = nodeType.prototype.onConfigure
            nodeType.prototype.onConfigure = function () {
                onConfigure?.apply(this, arguments)
                if (this.widgets_values?.length) {
                    populate.call(this, this.widgets_values)
                }
            }
        }
    },
})