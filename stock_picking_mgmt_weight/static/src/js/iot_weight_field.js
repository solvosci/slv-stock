odoo.define("stock_picking_mgmt_weight.FieldIotWeight", function(require) {
    "use strict";

    const core = require("web.core");
    const Dialog = require("web.Dialog");
    const AbstractField = require("web.AbstractField");
    const field_registry = require("web.field_registry");

    const _t = core._t;
    const _lt = core._lt;

    const FieldIotWeight = AbstractField.extend({
        description: _lt("Iot Weight"),
        supportedFieldTypes: ["integer"],
        template: "stock_picking_mgmt_weight.FieldIotWeight",
        // TODO custom_events

        init: function(parent, name, record, options) {
            this._super.apply(this, arguments);
            console.log("INIT FieldIotWeight");
        },

        start: function() {
            console.log("START FieldIotWeight");
            this.$span = this.$("span");            

            var self = this;
            // this._showErrorMessage(_t("This is a test for start()."));
            //self.getWeight();
            this.getWeightInterval = setInterval(() => {
                self.getWeight();
            }, 1000);

            return this._super.apply(this, arguments);
        },

        destroy: function () {
            console.log("DESTROYING...");
            clearInterval(this.getWeightInterval);
        },

        getWeight: function() {
            var self = this;
            var last_weight;
            // if ( !self.$span.is(":visible") ) {
            //     // TODO JS thread is still running, but we still need it 
            //     //  active if user turns back from form view.
            //     // It should overload browser engine
            //     console.log("NOT VISIBLE!!! FieldIotWeigth");
            //     // clearInterval(self.getWeightInterval);
            //     return;
            // }
            $.ajax({
                url: "/stock_picking_mgmt_weight/scale/read",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({})
            }).done(data => {
                console.log("Error: " + data.result.err);
                console.log("Value: " + data.result.value);
                self.$span.parent().removeClass("o_field_empty");
                if ( data.result.err ) {
                    self.$span.text(data.result.value);
                    self.$span.attr("title", data.result.err);
                    self.$span.addClass("bg-danger");
                }
                else {
                    self.$span.removeClass("bg-danger");
                    self.$span.removeAttr("title");
                    self.$span.text(data.result.value);
                    last_weight = data.result.value;
                }
            }).fail(() => {
                console.log("FAILED");
            }).always(() => {
                console.log("FINISHED AbstractField");
                // TODO time between updates make optional
                /*
                window.setTimeout(() => {
                    self.getWeight();
                }, 1000);
                */
            });
        },

        _showErrorMessage: function(error) {
            Dialog.alert(this, error, {
                title: _t("Iot Weight"),
            });
        },
    });

    field_registry.add("iot_weight", FieldIotWeight);

    return FieldIotWeight;

});
