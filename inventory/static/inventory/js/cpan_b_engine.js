/**
 * CPAN B Node Shared Engine
 * This engine handles all dynamic logic for CPAN B Node configuration sections:
 * - XSV3, STM, MSV1, GSV4, SNCV1, E1CV1
 * 
 * It is used by both Equipment and Circuit forms to ensure consistent behavior.
 */

window.CPANBNodeEngine = (function($) {
    'use strict';

    // Internal state/selectors
    const selectors = {
        xsv3: {
            count: '#xsv3-count',
            slots: '.xsv3-slot',
            uplinkPorts: '#xsv3-uplink-ports',
            portDetails: '#xsv3-port-details'
        },
        stm: {
            available: '#stm-available',
            container: '#stm-slots-container',
            slots: '.stm-slot',
            portDetails: '#stm-port-details'
        },
        msv1: {
            slots: '.msv1-slot',
            portDetails: '#msv1-port-details'
        },
        gsv4: {
            available: '#gsv4-available',
            container: '#gsv4-slots-container',
            slots: '.gsv4-slot',
            portDetails: '#gsv4-port-details'
        },
        sncv1: {
            available: '#sncv1-available',
            container: '#sncv1-slots-container',
            slots: '.sncv1-slot',
            portDetails: '#sncv1-port-details'
        },
        e1cv1: {
            available: '#e1cv1-available',
            container: '#e1cv1-details-container',
            ddf: '#e1cv1-ddf-details'
        }
    };

    // --- XSV3 Logic ---
    function getSelectedXsv3Slots() {
        return $(selectors.xsv3.slots + ':checked').map(function() {
            return $(this).val();
        }).get().sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
    }

    function enforceXsv3SlotLimit() {
        const limit = parseInt($(selectors.xsv3.count).val()) || 0;
        const allSlots = $(selectors.xsv3.slots);
        if (!allSlots.length) return;

        if (limit <= 0) {
            allSlots.prop('checked', false).prop('disabled', true);
            return;
        }

        allSlots.prop('disabled', false);
        const checked = allSlots.filter(':checked').toArray().sort((a, b) => parseInt($(a).val(), 10) - parseInt($(b).val(), 10));

        if (checked.length > limit) {
            checked.slice(limit).forEach(el => $(el).prop('checked', false));
        }

        if (allSlots.filter(':checked').length >= limit) {
            allSlots.not(':checked').prop('disabled', true);
        }
    }

    function updateXsv3Section() {
        enforceXsv3SlotLimit();
        const selectedSlots = getSelectedXsv3Slots();
        
        // Ensure the value is set correctly
        const derivedPorts = selectedSlots.map(slot => `${slot}/1`).join(', ');
        $('#xsv3-uplink-ports').val(derivedPorts);

        const container = $('#xsv3-port-details');
        container.empty();
        selectedSlots.forEach(slot => {
            const port = `${slot}/1`;
            container.append(`
                <div class="col-md-6 mb-3">
                    <div class="border p-2 rounded bg-light shadow-sm">
                        <label class="fw-bold mb-1 text-primary">UL ${port}:</label>
                        <input type="text" class="form-control mb-1 xsv3-cable" data-port="${port}" placeholder="Connected Cable Data" required>
                        <input type="text" class="form-control xsv3-end" data-port="${port}" placeholder="Connected System End" required>
                    </div>
                </div>
            `);
        });
    }

    // --- STM Logic ---
    function getSelectedStmSlots() {
        return $(selectors.stm.slots + ':checked').map(function() {
            return $(this).val();
        }).get().sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
    }

    function updateStmSection() {
        const selectedSlots = getSelectedStmSlots();
        const container = $(selectors.stm.portDetails);
        container.empty();
        selectedSlots.forEach(slot => {
            const n = parseInt(slot, 10);
            for (let i = 1; i <= n; i++) {
                const port = `${slot}/${i}`;
                container.append(`
                    <div class="col-md-4 mb-3">
                        <div class="border p-2 rounded bg-light">
                            <label class="fw-bold mb-1">Port ${port}:</label>
                            <input type="text" class="form-control mb-1 stm-cable" data-port="${port}" placeholder="Connected Cable Data" required>
                            <input type="text" class="form-control stm-end" data-port="${port}" placeholder="Other System End" required>
                        </div>
                    </div>
                `);
            }
        });
    }

    // --- MSV1 Logic ---
    function getSelectedMsv1Slots() {
        return $(selectors.msv1.slots + ':checked').map(function() {
            return $(this).val();
        }).get().sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
    }

    function updateMsv1Section() {
        const selectedSlots = getSelectedMsv1Slots();
        const container = $(selectors.msv1.portDetails);
        container.empty();
        selectedSlots.forEach(slot => {
            container.append(`
                <div class="col-12 mb-3">
                    <div class="card bg-light">
                        <div class="card-header py-1 fw-bold">Slot ${slot} Ports</div>
                        <div class="card-body p-2">
                            <div class="row">
                                ${Array.from({length: 8}, (_, i) => i + 1).map(portNum => `
                                    <div class="col-md-3 mb-2">
                                        <div class="border p-1 rounded bg-white small">
                                            <label class="fw-bold d-block">${slot}/${portNum}:</label>
                                            <select class="form-select form-select-sm mb-1 msv1-sfp" data-port="${slot}/${portNum}" required>
                                                <option value="Single">Single</option>
                                                <option value="Dual">Dual</option>
                                            </select>
                                            <input type="text" class="form-control form-control-sm mb-1 msv1-cable" data-port="${slot}/${portNum}" placeholder="Connected Cable Data" required>
                                            <input type="text" class="form-control form-control-sm msv1-end" data-port="${slot}/${portNum}" placeholder="Other System End" required>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `);
        });
    }

    // --- GSV4 Logic ---
    function getSelectedGsv4Slots() {
        return $(selectors.gsv4.slots + ':checked').map(function() {
            return $(this).val();
        }).get().sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
    }

    function updateGsv4Section() {
        const selectedSlots = getSelectedGsv4Slots();
        const container = $(selectors.gsv4.portDetails);
        container.empty();
        selectedSlots.forEach(slot => {
            container.append(`
                <div class="col-12 mb-3">
                    <div class="card bg-light border-primary">
                        <div class="card-header py-1 fw-bold bg-primary text-white">GSV4 - Slot ${slot}</div>
                        <div class="card-body p-2">
                            <div class="row">
                                ${[1, 2, 3, 4].map(p => `
                                    <div class="col-md-3 mb-2">
                                        <div class="border p-2 rounded bg-white shadow-sm">
                                            <div class="fw-bold text-primary small mb-1">Port: ${slot}/${p}</div>
                                            <input type="text" class="form-control form-control-sm mb-1 gsv4-circuit" data-port="${slot}/${p}" placeholder="Circuit Name">
                                            <input type="text" class="form-control form-control-sm mb-1 gsv4-cable" data-port="${slot}/${p}" placeholder="Cable Data">
                                            <input type="text" class="form-control form-control-sm gsv4-end" data-port="${slot}/${p}" placeholder="System End">
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `);
        });
    }

    // --- SNCV1 Logic ---
    function getSelectedSncv1Slots() {
        return $(selectors.sncv1.slots + ':checked').map(function() {
            return $(this).val();
        }).get().sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
    }

    function updateSncv1Section() {
        const selectedSlots = getSelectedSncv1Slots();
        const container = $(selectors.sncv1.portDetails);
        container.empty();
        selectedSlots.forEach(slot => {
            container.append(`
                <div class="col-12 mb-3">
                    <div class="card bg-light border-primary">
                        <div class="card-header py-1 fw-bold bg-primary text-white">SNCV1 - Slot ${slot}</div>
                        <div class="card-body p-2">
                            <div class="row">
                                ${[1, 2, 3, 4].map(p => `
                                    <div class="col-md-3 mb-2">
                                        <div class="border p-2 rounded bg-white shadow-sm">
                                            <div class="fw-bold text-primary small mb-1">Port: ${slot}/${p}</div>
                                            <input type="text" class="form-control form-control-sm mb-1 sncv1-circuit" data-port="${slot}/${p}" placeholder="Circuit Name">
                                            <input type="text" class="form-control form-control-sm mb-1 sncv1-cable" data-port="${slot}/${p}" placeholder="Cable Data">
                                            <input type="text" class="form-control form-control-sm sncv1-end" data-port="${slot}/${p}" placeholder="System End">
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `);
        });
    }

    // --- Initialization & Event Binding ---
    let initialized = false;

    function bindEvents() {
        if (initialized) return;
        initialized = true;

        // XSV3
        $(document).on('change', selectors.xsv3.count, function() {
            updateXsv3Section();
        });
        $(document).on('change', selectors.xsv3.slots, function() {
            const limit = parseInt($(selectors.xsv3.count).val()) || 0;
            if (limit > 0 && $(this).prop('checked')) {
                if ($(selectors.xsv3.slots + ':checked').length > limit) {
                    $(this).prop('checked', false);
                    alert(`XSV3 Card Inserted Slots selection is limited to ${limit}.`);
                }
            }
            updateXsv3Section();
        });

        // STM
        $(document).on('change', selectors.stm.available, function() {
            if (this.value === 'Y') {
                $(selectors.stm.container).show();
                updateStmSection();
            } else {
                $(selectors.stm.container).hide();
                $(selectors.stm.slots).prop('checked', false);
                $(selectors.stm.portDetails).empty();
            }
        });
        $(document).on('change', selectors.stm.slots, updateStmSection);

        // MSV1
        $(document).on('change', selectors.msv1.slots, updateMsv1Section);

        // GSV4
        $(document).on('change', selectors.gsv4.available, function() {
            if (this.value === 'Y') {
                $(selectors.gsv4.container).show();
                updateGsv4Section();
            } else {
                $(selectors.gsv4.container).hide();
                $(selectors.gsv4.slots).prop('checked', false);
                $(selectors.gsv4.portDetails).empty();
            }
        });
        $(document).on('change', selectors.gsv4.slots, updateGsv4Section);

        // SNCV1
        $(document).on('change', selectors.sncv1.available, function() {
            if (this.value === 'Y') {
                $(selectors.sncv1.container).show();
                updateSncv1Section();
            } else {
                $(selectors.sncv1.container).hide();
                $(selectors.sncv1.slots).prop('checked', false);
                $(selectors.sncv1.portDetails).empty();
            }
        });
        $(document).on('change', selectors.sncv1.slots, updateSncv1Section);

        // E1CV1
        $(document).on('change', selectors.e1cv1.available, function() {
            if (this.value === 'Y') {
                $(selectors.e1cv1.container).show();
                $(selectors.e1cv1.ddf).prop('required', true);
            } else {
                $(selectors.e1cv1.container).hide();
                $(selectors.e1cv1.ddf).val('').prop('required', false);
            }
        });
    }

    function initializeCPANBConfiguration() {
        bindEvents();
        updateXsv3Section();
        if ($(selectors.stm.available).val() === 'Y') {
            $(selectors.stm.container).show();
            updateStmSection();
        }
        updateMsv1Section();
        if ($(selectors.gsv4.available).val() === 'Y') {
            $(selectors.gsv4.container).show();
            updateGsv4Section();
        }
        if ($(selectors.sncv1.available).val() === 'Y') {
            $(selectors.sncv1.container).show();
            updateSncv1Section();
        }
        if ($(selectors.e1cv1.available).val() === 'Y') {
            $(selectors.e1cv1.container).show();
        }
    }

    function clearCPANBConfiguration() {
        $(selectors.xsv3.count).val('');
        $(selectors.xsv3.slots).prop('checked', false);
        $(selectors.xsv3.portDetails).empty();
        $(selectors.xsv3.uplinkPorts).val('');

        $(selectors.stm.available).val('N');
        $(selectors.stm.container).hide();
        $(selectors.stm.slots).prop('checked', false);
        $(selectors.stm.portDetails).empty();

        $(selectors.msv1.slots).prop('checked', false);
        $(selectors.msv1.portDetails).empty();

        $(selectors.gsv4.available).val('N');
        $(selectors.gsv4.container).hide();
        $(selectors.gsv4.slots).prop('checked', false);
        $(selectors.gsv4.portDetails).empty();

        $(selectors.sncv1.available).val('N');
        $(selectors.sncv1.container).hide();
        $(selectors.sncv1.slots).prop('checked', false);
        $(selectors.sncv1.portDetails).empty();

        $(selectors.e1cv1.available).val('N');
        $(selectors.e1cv1.container).hide();
        $(selectors.e1cv1.ddf).val('');
    }

    function collectConfig(nodeIp) {
        const xsv3Slots = getSelectedXsv3Slots();
        const xsv3Count = parseInt($(selectors.xsv3.count).val()) || 0;

        if (xsv3Count !== xsv3Slots.length) {
            alert(`Error: Number of XSV3 cards (${xsv3Count}) must match number of selected slots (${xsv3Slots.length}).`);
            return null;
        }

        // Validate mandatory fields
        let missingFields = false;
        $('.xsv3-cable, .xsv3-end, .stm-cable, .stm-end, .msv1-cable, .msv1-end').each(function() {
            if (!$(this).val()) {
                missingFields = true;
                return false;
            }
        });

        if (missingFields) {
            alert('Please fill all mandatory fields for XSV3, STM, and MSV1 cards.');
            return null;
        }

        if ($(selectors.gsv4.available).val() === 'Y' && getSelectedGsv4Slots().length === 0) {
            alert('At least one slot must be selected for GSV4 cards.');
            return null;
        }
        if ($(selectors.sncv1.available).val() === 'Y' && getSelectedSncv1Slots().length === 0) {
            alert('At least one slot must be selected for SNCV1 cards.');
            return null;
        }

        const config = {
            type: 'CPAN_B',
            node_ip: nodeIp,
            xsv3: { count: xsv3Count, slots: xsv3Slots, ports: [] },
            stm: { available: $(selectors.stm.available).val(), slots: $(selectors.stm.available).val() === 'Y' ? getSelectedStmSlots() : [], ports: [] },
            msv1: { slots: getSelectedMsv1Slots(), ports: [] },
            gsv4: { available: $(selectors.gsv4.available).val(), slots: $(selectors.gsv4.available).val() === 'Y' ? getSelectedGsv4Slots() : [], ports: [] },
            sncv1: { available: $(selectors.sncv1.available).val(), slots: $(selectors.sncv1.available).val() === 'Y' ? getSelectedSncv1Slots() : [], ports: [] },
            e1cv1: { available: $(selectors.e1cv1.available).val(), ddf_details: $(selectors.e1cv1.ddf).val() }
        };

        $('.xsv3-cable').each(function() {
            const port = $(this).data('port');
            config.xsv3.ports.push({ 
                port, 
                cable: $(this).val(), 
                system_end: $(`.xsv3-end[data-port="${port}"]`).val() 
            });
        });

        $('.stm-cable').each(function() {
            const port = $(this).data('port');
            config.stm.ports.push({ 
                port, 
                cable: $(this).val(), 
                system_end: $(`.stm-end[data-port="${port}"]`).val() 
            });
        });

        $('.msv1-sfp').each(function() {
            const port = $(this).data('port');
            config.msv1.ports.push({ 
                port, 
                sfp: $(this).val(), 
                cable: $(`.msv1-cable[data-port="${port}"]`).val(), 
                system_end: $(`.msv1-end[data-port="${port}"]`).val() 
            });
        });

        $('.gsv4-cable').each(function() {
            const port = $(this).data('port');
            config.gsv4.ports.push({ 
                port, 
                cable: $(this).val(), 
                system_end: $(`.gsv4-end[data-port="${port}"]`).val(),
                circuit_name: $(`.gsv4-circuit[data-port="${port}"]`).val()
            });
        });

        $('.sncv1-cable').each(function() {
            const port = $(this).data('port');
            config.sncv1.ports.push({ 
                port, 
                cable: $(this).val(), 
                system_end: $(`.sncv1-end[data-port="${port}"]`).val(),
                circuit_name: $(`.sncv1-circuit[data-port="${port}"]`).val()
            });
        });

        return config;
    }

    function loadConfig(config) {
        if (!config || config.type !== 'CPAN_B') return;

        if (config.xsv3) {
            $(selectors.xsv3.count).val(config.xsv3.count || '').trigger('change');
            if (Array.isArray(config.xsv3.slots)) {
                config.xsv3.slots.forEach(slot => $(`.xsv3-slot[value="${slot}"]`).prop('checked', true));
                updateXsv3Section();
            }
            if (Array.isArray(config.xsv3.ports)) {
                config.xsv3.ports.forEach(p => {
                    $(`.xsv3-cable[data-port="${p.port}"]`).val(p.cable || '');
                    $(`.xsv3-end[data-port="${p.port}"]`).val(p.system_end || '');
                });
            }
        }

        if (config.stm) {
            $(selectors.stm.available).val(config.stm.available || 'N').trigger('change');
            if (Array.isArray(config.stm.slots)) {
                config.stm.slots.forEach(slot => $(`.stm-slot[value="${slot}"]`).prop('checked', true));
                updateStmSection();
            }
            if (Array.isArray(config.stm.ports)) {
                config.stm.ports.forEach(p => {
                    $(`.stm-cable[data-port="${p.port}"]`).val(p.cable || '');
                    $(`.stm-end[data-port="${p.port}"]`).val(p.system_end || '');
                });
            }
        }

        if (config.msv1) {
            if (Array.isArray(config.msv1.slots)) {
                config.msv1.slots.forEach(slot => $(`.msv1-slot[value="${slot}"]`).prop('checked', true));
                updateMsv1Section();
            }
            if (Array.isArray(config.msv1.ports)) {
                config.msv1.ports.forEach(p => {
                    $(`.msv1-sfp[data-port="${p.port}"]`).val(p.sfp || 'Single');
                    $(`.msv1-cable[data-port="${p.port}"]`).val(p.cable || '');
                    $(`.msv1-end[data-port="${p.port}"]`).val(p.system_end || '');
                });
            }
        }

        if (config.gsv4) {
            $(selectors.gsv4.available).val(config.gsv4.available || 'N').trigger('change');
            if (Array.isArray(config.gsv4.slots)) {
                config.gsv4.slots.forEach(slot => $(`.gsv4-slot[value="${slot}"]`).prop('checked', true));
                updateGsv4Section();
            }
            if (Array.isArray(config.gsv4.ports)) {
                config.gsv4.ports.forEach(p => {
                    $(`.gsv4-circuit[data-port="${p.port}"]`).val(p.circuit_name || '');
                    $(`.gsv4-cable[data-port="${p.port}"]`).val(p.cable || '');
                    $(`.gsv4-end[data-port="${p.port}"]`).val(p.system_end || '');
                });
            }
        }

        if (config.sncv1) {
            $(selectors.sncv1.available).val(config.sncv1.available || 'N').trigger('change');
            if (Array.isArray(config.sncv1.slots)) {
                config.sncv1.slots.forEach(slot => $(`.sncv1-slot[value="${slot}"]`).prop('checked', true));
                updateSncv1Section();
            }
            if (Array.isArray(config.sncv1.ports)) {
                config.sncv1.ports.forEach(p => {
                    $(`.sncv1-circuit[data-port="${p.port}"]`).val(p.circuit_name || '');
                    $(`.sncv1-cable[data-port="${p.port}"]`).val(p.cable || '');
                    $(`.sncv1-end[data-port="${p.port}"]`).val(p.system_end || '');
                });
            }
        }

        if (config.e1cv1) {
            $(selectors.e1cv1.available).val(config.e1cv1.available || 'N').trigger('change');
            $(selectors.e1cv1.ddf).val(config.e1cv1.ddf_details || '');
        }
    }

    // Public API
    return {
        initialize: initializeCPANBConfiguration,
        clear: clearCPANBConfiguration,
        collect: collectConfig,
        load: loadConfig
    };

})(jQuery);
