odoo.define("stock_picking_mgmt_weight.ViewerIotWeight", function(require) {
    "use strict";

    const core = require("web.core");

    require("web.ListController").include({

        renderButtons: function($node) {
            var self = this;
            this._super.apply(this, arguments);
            if (this.$buttons) {
                console.log("RENDERING")
                this.iotViewer = this.$buttons.find(".oe_viewer_iot_weight");
                if ( this.iotViewer.length > 0 ) {
                    // TODO not working
                    this.iotViewer.parent(".o_list_buttons").addClass("oe_list_buttons_iot_weight");
                    this.iotViewer.bind("destroyed", () => {
                        console.log("DESTROYED!!!!!");
                        clearInterval(self.getWeightInterval);
                    });
                    this.getWeightInterval = setInterval(() => {
                        self.getWeight();
                    }, 1000);
                    // iotViewer.find("span").text("LOADED!!");
                }
            }
        },

        getWeight: function() {
            var self = this;
            if ( !self.iotViewer.is(":visible") ) {
                // TODO JS thread is still running, but we still need it 
                //  active if user turns back from form view.
                // It should overload browser engine
                console.log("NOT VISIBLE!!! NOT DETACHING...");
                // clearInterval(self.getWeightInterval);
                return;
            } 

            $.ajax({
                url: "/stock_picking_mgmt_weight/scale/read",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({})
            }).done(data => {
                console.log("Error: " + data.result.err);
                console.log("Value: " + data.result.value);
                // TODO error handling
                if ( data.result.err ) {
                    self.iotViewer.find("span").text(data.result.value);
                    self.iotViewer.find("span").attr("title", data.result.err)
                    self.iotViewer.find("span").addClass("bg-danger");
                }
                else {
                    self.iotViewer.find("span").removeAttr("title");
                    self.iotViewer.find("span").removeClass("bg-danger");
                    self.iotViewer.find("span").text(data.result.value);
                }
            }).fail(() => {
                console.log("FAILED");
            }).always(() => {
                console.log("FINISHED ListController");
            });
        },
    });
});
