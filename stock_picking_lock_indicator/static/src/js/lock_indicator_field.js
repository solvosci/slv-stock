/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

/**
 * Read-only indicator for boolean fields: renders a padlock icon when
 * the field value is true, and nothing at all when it is false.
 * Used on stock.picking's "is_locked" field in the list view.
 */
export class LockIndicatorField extends Component {
    static template = "stock_picking_lock_indicator.LockIndicatorField";
    static props = { ...standardFieldProps };

    get isLocked() {
        return this.props.record.data[this.props.name];
    }
}

registry.category("fields").add("lock_indicator", LockIndicatorField);
