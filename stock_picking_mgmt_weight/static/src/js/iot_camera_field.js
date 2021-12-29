odoo.define("stock_picking_mgmt_weight.FieldIotCamera", function(require) {
    "use strict";

    const core = require("web.core");
    const Dialog = require("web.Dialog");
    const AbstractField = require("web.AbstractField");
    const field_registry = require("web.field_registry");

    const _t = core._t;
    const _lt = core._lt;

    const FieldIotCamera = AbstractField.extend({
        description: _lt("Iot Camera"),
        supportedFieldTypes: ["binary"],
        template: "stock_picking_mgmt_weight.FieldIotCamera",
        // TODO custom_events

        init: function(parent, name, record, options) {
            this._super.apply(this, arguments);
            console.log("INIT FieldIotCamera");
        },

        start: function() {
            console.log("START FieldIotCamera");
            this.$img = this.$("img");
        
            var self = this;
            self.getImage();

            return this._super.apply(this, arguments);
        },

        destroy: function () {
            console.log("DESTROYING...");
            clearInterval(this.getCameraInterval);
        },
        
        getImage: function() {
            var self = this;

            $.ajax({
                url: "/stock_picking_mgmt_weight/camera/read",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({})
            }).done(data => {
                var url_image = data.result.url_image;
                var refresh_time = data.result.refresh_time;

                this.getCameraInterval = setInterval(() => {
                    var timestamp = new Date().getTime();
                    self.$img.attr("src", url_image + "&t=" + timestamp);
                }, refresh_time);
            });
        },

        _showErrorMessage: function(error) {
            Dialog.alert(this, error, {
                title: _t("Iot Camera"),
            });
        },
    });

    field_registry.add("iot_camera_field", FieldIotCamera);

    return FieldIotCamera;

});
