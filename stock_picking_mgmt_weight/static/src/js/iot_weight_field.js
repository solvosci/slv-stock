/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, useRef} from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Dialog } from "@web/core/dialog/dialog";

export class FieldIotWeight extends Component {
    setup() {
        this.weightSpan = useRef("weightSpan");
        this.getWeightInterval = null;

        onMounted(() => {
            console.log("✅ FieldIotWeight mounted");
            console.log("Ref:", this.weightSpan);

            if (!this.weightSpan.el) {
                console.error("❌ Not found Span in template");
                return;
            }

            this.getWeightInterval = setInterval(() => {
                this.getWeight(this.weightSpan.el);
            }, 1000);
        });

        onWillUnmount(() => {
            console.log("DESTROYING...");
            clearInterval(this.getWeightInterval);
        });
    }

    getWeight(spanEl) {
        if (!spanEl) return;

        let scale = null;
        const scaleContainer = document.querySelector('div[name="picking_operations_scale_id"]');
        if (scaleContainer) {
            const scaleInput = scaleContainer.querySelector('input');
            if (!scaleInput || !scaleInput.value) {
                console.log("No scale selected, skipping weight fetch");
                return;
            }
            scale = scaleInput.value;
        } else {
            const aScale = document.querySelector('a[name="picking_operations_scale_id"] span');
            if (aScale) scale = aScale.textContent;
        }

        if (!scale) return;

        fetch("/stock_picking_mgmt_weight/scale/read", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ scale_name: scale }),
        })
            .then(r => r.json())
            .then(data => {
                const result = (data?.result) || { err: "Undefined error", value: "---" };
                console.log("Error: " + result.err);
                console.log("Value: " + result.value);

                spanEl.parentElement.classList.remove("o_field_empty");

                if (result.err) {
                    spanEl.textContent = result.value;
                    spanEl.setAttribute("title", result.err);
                    spanEl.classList.add("bg-danger");
                } else {
                    spanEl.classList.remove("bg-danger");
                    spanEl.removeAttribute("title");
                    spanEl.textContent = result.value;
                }
            })
            .catch(() => {
                console.log("FAILED");
                spanEl.textContent = "---";
                spanEl.setAttribute("title", "Server is not responding");
                spanEl.classList.add("bg-danger");
            });
    }

    _showErrorMessage(error) {
        Dialog.alert(this, error, { title: "Iot Weight" });
    }
}

FieldIotWeight.props = { ...standardFieldProps };

FieldIotWeight.template = "stock_picking_mgmt_weight.FieldIotWeight";

registry.category("fields").add("iot_weight", {
    component: FieldIotWeight,
});
