odoo.define('stock_valuation.InventoryReportListController', function (require) {
    "use strict";
    
    var InventoryReportListController = require('stock.InventoryReportListController');

    var includeDict = {
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.hasButtons) {
                // TODO Better approach: enable "Inventory Date" button but 
                //  with a new destination (product.average.price.date.wizard)
                //  instead of hiding it
                this.$buttons.find('button.btn-primary:first').hide();
            }
        }
    };    
    
    InventoryReportListController.include(includeDict);
    
});
    