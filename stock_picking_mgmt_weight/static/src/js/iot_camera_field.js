/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, useRef} from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Dialog } from "@web/core/dialog/dialog";

export class FieldIotCamera extends Component {
    setup() {
        this.weightImg = useRef("weightCamera");
        this.getCameraInterval = null;

        onMounted(() => {
            console.log("✅ FieldIotCamera mounted", this.weightImg);
            if (!this.weightImg.el) {
                console.error("❌ Img element not found!");
                return;
            }
            this.getImage();
        });

        onWillUnmount(() => {
            console.log("DESTROYING FieldIotCamera...");
            clearInterval(this.getCameraInterval);
        });
    }

    getImage() {
        if (!this.weightImg.el) return;

        fetch("/stock_picking_mgmt_weight/camera/read", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({}),
        })
        .then(r => r.json())
        .then(data => {
            const url_image = data.result?.url_image || "";
            const refresh_time = data.result?.refresh_time || 5000;

            this.getCameraInterval = setInterval(() => {
                const timestamp = new Date().getTime();
                this.weightImg.el.setAttribute("src", url_image + "?t=" + timestamp);
            }, refresh_time);
        })
        .catch(err => {
            Dialog.alert(this, err, { title: "Iot Camera" });
        });
    }
}

FieldIotCamera.props = { ...standardFieldProps };

FieldIotCamera.template = "stock_picking_mgmt_weight.FieldIotCamera";

registry.category("fields").add("iot_camera", {
    component: FieldIotCamera,
});
