odoo.define("stock_picking_mgmt_weight.FieldIotASM", function(require) {
    "use strict";

    const core = require("web.core");
    const Dialog = require("web.Dialog");
    const AbstractField = require("web.AbstractField");
    const field_registry = require("web.field_registry");

    const _t = core._t;
    const _lt = core._lt;

    const FieldIotASM = AbstractField.extend({
        description: _lt("Iot ASM"),
        supportedFieldTypes: ["char"],
        template: "stock_picking_mgmt_weight.FieldIotASM",
        // TODO custom_events

        init: function(parent, name, record, options) {
            this._super.apply(this, arguments);
            console.log("INIT FieldIotASM");
        },

        start: function() {
            console.log("START FieldIotASM");
            this.$color = this.$(".asm_color");
            this.$status = this.$(".asm_status");
        
            var self = this;
            self.getStatus();

            return this._super.apply(this, arguments);
        },

        destroy: function () {
            console.log("DESTROYING...");
            clearInterval(this.getASMInterval);
        },
        
        getStatus: function() {
            var self = this;

            $.ajax({
                url: "/stock_picking_mgmt_weight/asm/read",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({})
            }).done(data => {
                var color = "#" + data.result.color;
                var status = data.result.status;
                var refresh_time = data.result.refresh_time;
                

                this.getASMInterval = setInterval(() => {
                    self.$color.css("background-color", color);
                    self.$status.text(status);
                }, refresh_time);
            });
        },

        _showErrorMessage: function(error) {
            Dialog.alert(this, error, {
                title: _t("Iot ASM"),
            });
        },
    });

    field_registry.add("iot_asm_field", FieldIotASM);

    return FieldIotASM;

});
