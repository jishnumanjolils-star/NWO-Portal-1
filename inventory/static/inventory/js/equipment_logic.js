$(document).ready(function() {
    const eqTypeSelect = $('#id_equipment_type');
    const nameLabel = $('label[for="id_name"]');
    const cpanSections = $('#cpan-config-sections');
    const maanSections = $('#maan-a3a4-config-sections');
    const maanCSections = $('#maan-c-config-sections');
    const madmSections = $('#madm-config-sections');
    const nodeIpSection = $('#equipment-node-ip-section');
    const nodeIpInput = $('#equipment-node-ip');
    let maanCInitialized = false;
    let madmInitialized = false;
    let maanCCards = [];
    let madmCards = [];
    let getMaanCSelectedSlots = null;
    let isMaanCCardAvailable = null;
    let refreshMaanCSlots = null;
    let refreshMadm = null;

    function isValidIpv4(ip) {
        const val = String(ip || '').trim();
        const parts = val.split('.');
        if (parts.length !== 4) return false;
        return parts.every(p => {
            if (!/^\d+$/.test(p)) return false;
            if (p.length > 1 && p.startsWith('0')) return false;
            const n = parseInt(p, 10);
            return n >= 0 && n <= 255;
        });
    }

    function needsNodeIp(type) {
        return !!String(type || '').trim();
    }

    function updateFreePorts() {
        const totalRaw = $('#id_total_ports').val();
        const usedRaw = $('#id_used_ports').val();
        const total = parseInt(totalRaw, 10);
        const used = parseInt(usedRaw, 10);
        if (!Number.isFinite(total) || !Number.isFinite(used)) {
            $('#id_free_ports').val('');
            return;
        }
        $('#id_free_ports').val(Math.max(total - used, 0));
    }

    // 1. Equipment Type Selection Logic
    eqTypeSelect.on('change', function() {
        const selectedType = this.value;
        if (selectedType !== 'CPAN_B') {
            clearCPANBConfiguration();
        }

        if (needsNodeIp(selectedType)) {
            nodeIpSection.show();
            nodeIpInput.prop('required', true);
        } else {
            nodeIpSection.hide();
            nodeIpInput.prop('required', false).val('');
        }

        if (this.value === 'CPAN_B') {
            nameLabel.text('Ring ID*');
            cpanSections.show();
            maanSections.hide();
            maanCSections.hide();
            madmSections.hide();
            if (window.CPANBNodeEngine) {
                window.CPANBNodeEngine.initialize();
            }
        } else if (this.value === 'MAAN_A3_A4') {
            nameLabel.text('Equipment Name*');
            cpanSections.hide();
            maanSections.show();
            maanCSections.hide();
            madmSections.hide();
            generateMaanPorts();
        } else if (this.value === 'MAAN_C') {
            nameLabel.text('Equipment Name*');
            cpanSections.hide();
            maanSections.hide();
            maanCSections.show();
            madmSections.hide();
            initMaanCSection();
        } else if (this.value === 'MADM') {
            nameLabel.text('Equipment Name*');
            cpanSections.hide();
            maanSections.hide();
            maanCSections.hide();
            madmSections.show();
            initMadmSection();
        } else {
            nameLabel.text('Name*');
            cpanSections.hide();
            maanSections.hide();
            maanCSections.hide();
            madmSections.hide();
        }
    }).trigger('change');

    $('#id_total_ports, #id_used_ports').on('input change', updateFreePorts);
    updateFreePorts();

    function initMaanCSection() {
        if (maanCInitialized) {
            if (refreshMaanCSlots) refreshMaanCSlots();
            return;
        }
        maanCInitialized = true;

        const cards = [
            { key: 'cel16', availableSel: '#maan-c-cel16-available', fieldsSel: '#maan-c-cel16-fields', countSel: '#maan-c-cel16-count' },
            { key: 'cel13', availableSel: '#maan-c-cel13-available', fieldsSel: '#maan-c-cel13-fields', countSel: '#maan-c-cel13-count' },
            { key: 'cel12', availableSel: '#maan-c-cel12-available', fieldsSel: '#maan-c-cel12-fields', countSel: '#maan-c-cel12-count' },
            { key: 'cel6', availableSel: '#maan-c-cel6-available', fieldsSel: '#maan-c-cel6-fields', countSel: '#maan-c-cel6-count' },
            { key: 'csc1', availableSel: '#maan-c-csc1-available', fieldsSel: '#maan-c-csc1-fields', countSel: '#maan-c-csc1-count' },
            { key: 'csc2', availableSel: '#maan-c-csc2-available', fieldsSel: '#maan-c-csc2-fields', countSel: '#maan-c-csc2-count' }
        ];

        function isCardAvailable(cardKey) {
            const card = cards.find(c => c.key === cardKey);
            if (!card) return false;
            return String($(card.availableSel).val() || '').trim().toUpperCase() === 'Y';
        }

        function getSelectedCardSlots(cardKey) {
            const values = maanCSections.find(`.maan-c-slot[data-card="${cardKey}"]:checked`).map(function() {
                return $(this).val();
            }).get();
            return values.sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
        }

        function updateCel16UplinkPorts() {
            const available = isCardAvailable('cel16');
            if (!available) {
                $('#maan-c-cel16-uplink-ports').val('');
                return;
            }

            const slots = getSelectedCardSlots('cel16');
            const uplinks = [];
            slots.forEach(slot => {
                uplinks.push(`${slot}/5`);
                uplinks.push(`${slot}/6`);
            });
            $('#maan-c-cel16-uplink-ports').val(uplinks.join(', '));
        }

        function updateCel16PortDetails() {
            const container = $('#maan-c-cel16-port-details');
            container.empty();

            const available = isCardAvailable('cel16');
            if (!available) return;

            const slots = getSelectedCardSlots('cel16');
            slots.forEach(slot => {
                container.append(`
                    <div class="card border-info mb-3 shadow-sm">
                        <div class="card-header bg-info text-white py-2 fw-bold">CEL16 – Slot ${slot}</div>
                        <div class="card-body p-2">
                            <div class="table-responsive">
                                <table class="table table-sm table-bordered align-middle mb-0">
                                    <thead class="table-light">
                                        <tr>
                                            <th style="width: 90px;">Port</th>
                                            <th style="width: 120px;">Capacity</th>
                                            <th>Circuit Name</th>
                                            <th>Other System End</th>
                                            <th>Cable Details</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${[1,2,3,4,5,6].map(p => {
                                            const port = `${slot}/${p}`;
                                            const capacity = p <= 4 ? '10G' : '100G Uplink';
                                            return `
                                                <tr>
                                                    <td class="fw-bold">${port}</td>
                                                    <td>${capacity}</td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel16-circuit" data-port="${port}"></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel16-end" data-port="${port}"></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel16-cable" data-port="${port}"></td>
                                                </tr>
                                            `;
                                        }).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `);
            });
        }

        function updateCel13PortDetails() {
            const container = $('#maan-c-cel13-port-details');
            container.empty();

            const available = isCardAvailable('cel13');
            if (!available) return;

            const slots = getSelectedCardSlots('cel13');
            slots.forEach(slot => {
                container.append(`
                    <div class="card border-info mb-3 shadow-sm">
                        <div class="card-header bg-info text-white py-2 fw-bold">CEL13 – Slot ${slot}</div>
                        <div class="card-body p-2">
                            <div class="table-responsive">
                                <table class="table table-sm table-bordered align-middle mb-0">
                                    <thead class="table-light">
                                        <tr>
                                            <th style="width: 90px;">Port</th>
                                            <th style="width: 140px;">Capacity</th>
                                            <th>Circuit Name</th>
                                            <th>Other System End</th>
                                            <th>Cable Details</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr class="table-light">
                                            <td colspan="5" class="fw-bold">10G Ports (P1–P4)</td>
                                        </tr>
                                        ${[1,2,3,4].map(p => {
                                            const port = `${slot}/${p}`;
                                            return `
                                                <tr>
                                                    <td class="fw-bold">${port}</td>
                                                    <td><span class="badge bg-primary">10G</span></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel13-circuit" data-port="${port}"></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel13-end" data-port="${port}"></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel13-cable" data-port="${port}"></td>
                                                </tr>
                                            `;
                                        }).join('')}
                                        <tr class="table-light">
                                            <td colspan="5" class="fw-bold">STM E1 Ports (P5–P8)</td>
                                        </tr>
                                        ${[5,6,7,8].map(p => {
                                            const port = `${slot}/${p}`;
                                            return `
                                                <tr>
                                                    <td class="fw-bold">${port}</td>
                                                    <td><span class="badge bg-warning text-dark">STM E1</span></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel13-circuit" data-port="${port}"></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel13-end" data-port="${port}"></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel13-cable" data-port="${port}"></td>
                                                </tr>
                                            `;
                                        }).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `);
            });
        }

        function updateCel12PortDetails() {
            const container = $('#maan-c-cel12-port-details');
            container.empty();

            const available = isCardAvailable('cel12');
            if (!available) return;

            const slots = getSelectedCardSlots('cel12');
            slots.forEach(slot => {
                container.append(`
                    <div class="card border-primary mb-3 shadow-sm">
                        <div class="card-header bg-primary text-white py-2 fw-bold">CEL12 – Slot ${slot}</div>
                        <div class="card-body p-2">
                            <div class="table-responsive">
                                <table class="table table-sm table-bordered align-middle mb-0">
                                    <thead class="table-light">
                                        <tr>
                                            <th style="width: 90px;">Port</th>
                                            <th style="width: 120px;">Capacity</th>
                                            <th>Circuit Name</th>
                                            <th>Other System End</th>
                                            <th>Cable Details</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${[1,2,3,4,5,6,7,8].map(p => {
                                            const port = `${slot}/${p}`;
                                            return `
                                                <tr>
                                                    <td class="fw-bold">${port}</td>
                                                    <td><span class="badge bg-primary">10G</span></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel12-circuit" data-port="${port}"></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel12-end" data-port="${port}"></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel12-cable" data-port="${port}"></td>
                                                </tr>
                                            `;
                                        }).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `);
            });
        }

        function updateCel6PortDetails() {
            const container = $('#maan-c-cel6-port-details');
            container.empty();

            const available = isCardAvailable('cel6');
            if (!available) return;

            const slots = getSelectedCardSlots('cel6');
            slots.forEach(slot => {
                container.append(`
                    <div class="card border-success mb-3 shadow-sm">
                        <div class="card-header bg-success text-white py-2 fw-bold">CEL6 – Slot ${slot}</div>
                        <div class="card-body p-2">
                            <div class="table-responsive">
                                <table class="table table-sm table-bordered align-middle mb-0">
                                    <thead class="table-light">
                                        <tr>
                                            <th style="width: 90px;">Port</th>
                                            <th style="width: 120px;">Capacity</th>
                                            <th>Circuit Name</th>
                                            <th>Other System End</th>
                                            <th>Cable Details</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${[1,2,3,4,5,6,7,8].map(p => {
                                            const port = `${slot}/${p}`;
                                            return `
                                                <tr>
                                                    <td class="fw-bold">${port}</td>
                                                    <td><span class="badge bg-success">1G</span></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel6-circuit" data-port="${port}"></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel6-end" data-port="${port}"></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-cel6-cable" data-port="${port}"></td>
                                                </tr>
                                            `;
                                        }).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `);
            });
        }

        function updateCscPortDetails(cardKey) {
            const available = isCardAvailable(cardKey);
            const containerId = cardKey === 'csc1' ? '#maan-c-csc1-port-details' : '#maan-c-csc2-port-details';
            const title = cardKey === 'csc1' ? 'CSC1' : 'CSC2';
            const headerClass = cardKey === 'csc1' ? 'bg-primary' : 'bg-success';
            const textClass = 'text-white';

            const container = $(containerId);
            container.empty();
            if (!available) return;

            const slots = getSelectedCardSlots(cardKey);
            slots.forEach(slot => {
                container.append(`
                    <div class="card border-secondary mb-3 shadow-sm">
                        <div class="card-header ${headerClass} ${textClass} py-2 fw-bold">${title} – Slot ${slot}</div>
                        <div class="card-body p-2">
                            <div class="table-responsive">
                                <table class="table table-sm table-bordered align-middle mb-0">
                                    <thead class="table-light">
                                        <tr>
                                            <th style="width: 90px;">Port</th>
                                            <th>Circuit Name</th>
                                            <th>Other System End</th>
                                            <th>Cable Details</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${[1,2,3,4,5,6,7,8,9,10,11].map(p => {
                                            const port = `${slot}/${p}`;
                                            return `
                                                <tr>
                                                    <td class="fw-bold">${port}</td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-${cardKey}-circuit" data-port="${port}"></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-${cardKey}-end" data-port="${port}"></td>
                                                    <td><input type="text" class="form-control form-control-sm maan-c-${cardKey}-cable" data-port="${port}"></td>
                                                </tr>
                                            `;
                                        }).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `);
            });
        }

        function setCardEnabled(cardKey, enabled) {
            const card = cards.find(c => c.key === cardKey);
            if (!card) return;

            if (enabled) {
                $(card.fieldsSel).show();
                maanCSections.find(`.maan-c-slot[data-card="${cardKey}"]`).prop('disabled', false);
            } else {
                $(card.fieldsSel).hide();
                $(card.countSel).val('');
                maanCSections.find(`.maan-c-slot[data-card="${cardKey}"]`).prop('checked', false).prop('disabled', true);
            }
        }

        function getOccupiedSlotsMap() {
            const occupied = {};
            cards.forEach(card => {
                if (!isCardAvailable(card.key)) return;
                getSelectedCardSlots(card.key).forEach(slot => {
                    occupied[slot] = card.key;
                });
            });
            return occupied;
        }

        function refreshMaanCSlotsUI() {
            const occupied = getOccupiedSlotsMap();

            maanCSections.find('.maan-c-slot').each(function() {
                const slot = $(this).val();
                const cardKey = $(this).data('card');
                const owner = occupied[slot];
                const shouldDisable = owner && owner !== cardKey;

                if (shouldDisable && $(this).prop('checked') && owner && owner !== cardKey) {
                    $(this).prop('checked', false);
                }

                $(this).prop('disabled', shouldDisable);
            });

            updateCel16UplinkPorts();
            updateCel16PortDetails();
            updateCel13PortDetails();
            updateCel12PortDetails();
            updateCel6PortDetails();
            updateCscPortDetails('csc1');
            updateCscPortDetails('csc2');
        }

        function handleAvailableChange(cardKey) {
            const enabled = isCardAvailable(cardKey);
            setCardEnabled(cardKey, enabled);
            refreshMaanCSlotsUI();
        }

        function handleSlotChange(changedEl) {
            const slot = $(changedEl).val();
            const cardKey = $(changedEl).data('card');

            if ($(changedEl).prop('checked')) {
                const conflict = maanCSections.find(`.maan-c-slot[value="${slot}"]:checked`).filter(function() {
                    return $(this).data('card') !== cardKey;
                });
                if (conflict.length > 0) {
                    $(changedEl).prop('checked', false);
                    alert(`Slot ${slot} already assigned to another card.`);
                }
            }

            refreshMaanCSlotsUI();
        }

        cards.forEach(card => {
            $(card.availableSel).on('change', function() {
                handleAvailableChange(card.key);
            });
            handleAvailableChange(card.key);
        });

        $(document).on('input', '#maan-c-config-sections input[type="number"]', function() {
            refreshMaanCSlotsUI();
        });

        $(document).on('change', '#maan-c-config-sections .maan-c-slot', function() {
            handleSlotChange(this);
        });

        $(document).on('click', '#maan-c-config-sections .maan-c-slot', function() {
            const el = this;
            setTimeout(() => handleSlotChange(el), 0);
        });

        refreshMaanCSlotsUI();

        let lastMaanCSignature = null;
        setInterval(() => {
            if (eqTypeSelect.val() !== 'MAAN_C') return;

            const signatureParts = [];
            for (const card of cards) {
                const available = String($(card.availableSel).val() || '').trim().toUpperCase();
                const count = String($(card.countSel).val() || '').trim();
                const slots = getSelectedCardSlots(card.key).join(',');
                signatureParts.push(`${card.key}:${available}:${count}:${slots}`);
            }
            const signature = signatureParts.join('|');

            if (signature !== lastMaanCSignature) {
                lastMaanCSignature = signature;
                refreshMaanCSlotsUI();
            }
        }, 300);

        maanCCards = cards;
        getMaanCSelectedSlots = getSelectedCardSlots;
        isMaanCCardAvailable = isCardAvailable;
        refreshMaanCSlots = refreshMaanCSlotsUI;
    }

    function initMadmSection() {
        if (madmInitialized) {
            if (refreshMadm) refreshMadm();
            return;
        }
        madmInitialized = true;

        const cards = [
            { key: 'com01', availableSel: '#madm-com01-available', fieldsSel: '#madm-com01-fields', portSel: '#madm-com01-port-details' },
            { key: 'agg06', availableSel: '#madm-agg06-available', fieldsSel: '#madm-agg06-fields', portSel: '#madm-agg06-port-details' },
            { key: 'elan05d', availableSel: '#madm-elan05d-available', fieldsSel: '#madm-elan05d-fields', portSel: '#madm-elan05d-port-details' },
            { key: 'a010000', availableSel: '#madm-a010000-available', fieldsSel: '#madm-a010000-fields', portSel: '#madm-a010000-port-details' }
        ];

        function isCardAvailable(cardKey) {
            const card = cards.find(c => c.key === cardKey);
            if (!card) return false;
            return String($(card.availableSel).val() || '').trim().toUpperCase() === 'Y';
        }

        function getSelectedSlots(cardKey) {
            const values = madmSections.find(`.madm-slot[data-card="${cardKey}"]:checked`).map(function() {
                return $(this).val();
            }).get();
            return values.sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
        }

        function setCardEnabled(cardKey, enabled) {
            const card = cards.find(c => c.key === cardKey);
            if (!card) return;

            if (enabled) {
                $(card.fieldsSel).show();
                madmSections.find(`.madm-slot[data-card="${cardKey}"]`).prop('disabled', false);
            } else {
                $(card.fieldsSel).hide();
                madmSections.find(`.madm-slot[data-card="${cardKey}"]`).prop('checked', false).prop('disabled', true);
                if (card.portSel) $(card.portSel).empty();
            }
        }

        function getOccupiedSlotsMap() {
            const occupied = {};
            cards.forEach(card => {
                if (!isCardAvailable(card.key)) return;
                getSelectedSlots(card.key).forEach(slot => {
                    occupied[slot] = card.key;
                });
            });
            return occupied;
        }

        function badge(type) {
            if (type === 'Coaxial') return '<span class="badge bg-warning text-dark">Coaxial</span>';
            if (type === 'Optical') return '<span class="badge bg-primary">Optical</span>';
            if (type === 'LAN') return '<span class="badge bg-success">LAN</span>';
            if (type === 'Uplink') return '<span class="badge bg-danger">Uplink</span>';
            return `<span class="badge bg-secondary">${type}</span>`;
        }

        function renderPorts(cardKey, slot, portCount, typeFn) {
            const rows = Array.from({ length: portCount }, (_, idx) => idx + 1).map(p => {
                const port = `${slot}/${p}`;
                const type = typeFn(p);
                return `
                    <tr>
                        <td class="fw-bold">${port}</td>
                        <td>${badge(type)}</td>
                        <td><input type="text" class="form-control form-control-sm madm-${cardKey}-circuit" data-port="${port}"></td>
                        <td><input type="text" class="form-control form-control-sm madm-${cardKey}-end" data-port="${port}"></td>
                        <td><input type="text" class="form-control form-control-sm madm-${cardKey}-cable" data-port="${port}"></td>
                    </tr>
                `;
            }).join('');

            return `
                <div class="card mb-3 shadow-sm border-light">
                    <div class="card-header bg-light fw-bold">${cardKey.toUpperCase()} – Slot ${slot}</div>
                    <div class="card-body p-2">
                        <div class="table-responsive">
                            <table class="table table-sm table-bordered align-middle mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th style="width: 90px;">Port</th>
                                        <th style="width: 120px;">Type</th>
                                        <th>Circuit Name</th>
                                        <th>Other System End</th>
                                        <th>Cable Details</th>
                                    </tr>
                                </thead>
                                <tbody>${rows}</tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        }

        function updateCom01Ports() {
            const container = $('#madm-com01-port-details');
            container.empty();
            if (!isCardAvailable('com01')) return;
            getSelectedSlots('com01').forEach(slot => {
                container.append(renderPorts('com01', slot, 3, () => 'Coaxial'));
            });
        }

        function updateAgg06Ports() {
            const container = $('#madm-agg06-port-details');
            container.empty();
            if (!isCardAvailable('agg06')) return;
            getSelectedSlots('agg06').forEach(slot => {
                container.append(renderPorts('agg06', slot, 16, p => (p <= 4 || p >= 13 ? 'Coaxial' : 'Optical')));
            });
        }

        function updateElan05dPorts() {
            const container = $('#madm-elan05d-port-details');
            container.empty();
            if (!isCardAvailable('elan05d')) return;
            getSelectedSlots('elan05d').forEach(slot => {
                container.append(renderPorts('elan05d', slot, 72, p => ((p >= 1 && p <= 16) || (p >= 37 && p <= 52) ? 'LAN' : 'Optical')));
            });
        }

        function updateA010000Warning() {
            const warning = $('#madm-a010000-warning');
            warning.hide();
            if (!isCardAvailable('a010000')) return;
            const slots = getSelectedSlots('a010000');
            const hasLow = slots.some(s => parseInt(s, 10) < 7);
            if (hasLow) warning.show();
        }

        function updateA010000Ports() {
            const container = $('#madm-a010000-port-details');
            container.empty();
            if (!isCardAvailable('a010000')) return;
            getSelectedSlots('a010000').forEach(slot => {
                const port = `${slot}/1`;
                container.append(`
                    <div class="card mb-3 shadow-sm border-danger">
                        <div class="card-header bg-danger text-white fw-bold">A010000 – Slot ${slot}</div>
                        <div class="card-body p-2">
                            <div class="table-responsive">
                                <table class="table table-sm table-bordered align-middle mb-0">
                                    <thead class="table-light">
                                        <tr>
                                            <th style="width: 90px;">Uplink Port</th>
                                            <th style="width: 120px;">Type</th>
                                            <th>Circuit Name</th>
                                            <th>Other System End</th>
                                            <th>Cable Details</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td class="fw-bold">${port}</td>
                                            <td>${badge('Uplink')}</td>
                                            <td><input type="text" class="form-control form-control-sm madm-a010000-circuit" data-port="${port}"></td>
                                            <td><input type="text" class="form-control form-control-sm madm-a010000-end" data-port="${port}"></td>
                                            <td><input type="text" class="form-control form-control-sm madm-a010000-cable" data-port="${port}"></td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                `);
            });
        }

        function refreshMadmUI() {
            const occupied = getOccupiedSlotsMap();

            madmSections.find('.madm-slot').each(function() {
                const slot = $(this).val();
                const cardKey = $(this).data('card');
                const owner = occupied[slot];
                const shouldDisable = owner && owner !== cardKey;
                if (shouldDisable && $(this).prop('checked')) $(this).prop('checked', false);
                $(this).prop('disabled', shouldDisable);
            });

            updateCom01Ports();
            updateAgg06Ports();
            updateElan05dPorts();
            updateA010000Warning();
            updateA010000Ports();
        }

        cards.forEach(card => {
            $(card.availableSel).on('change', function() {
                setCardEnabled(card.key, isCardAvailable(card.key));
                refreshMadmUI();
            });
            setCardEnabled(card.key, isCardAvailable(card.key));
        });

        $(document).on('change', '#madm-config-sections .madm-slot', function() {
            const cardKey = String($(this).data('card') || '');
            if (cardKey === 'a010000' && $(this).prop('checked')) {
                const count = getSelectedSlots('a010000').length;
                if (count > 2) {
                    $(this).prop('checked', false);
                    alert('A010000 supports maximum 2 uplink slots only.');
                }
            }
            refreshMadmUI();
        });

        refreshMadmUI();

        madmCards = cards;
        refreshMadm = refreshMadmUI;
    }

    function generateMaanPorts() {
        const container = $('#maan-a3a4-port-details');
        if (container.children().length > 0) return; // Already generated

        container.empty();
        
        const ports = [];
        for (let i = 1; i <= 24; i++) ports.push(`P${i}`);
        for (let i = 1; i <= 4; i++) ports.push(`E${i}`);

        ports.forEach(port => {
            let func = "";
            const pNum = parseInt(port.substring(1));
            if (port.startsWith('P')) {
                if (pNum <= 12) func = "1G Out";
                else if (pNum <= 16) func = "10G Out";
                else if (pNum <= 20) func = "1GE LAN Port";
                else func = "STM Ports";
            } else {
                func = "Expansion Port";
            }

            container.append(`
                <div class="col-md-3 mb-3">
                    <div class="border p-2 rounded bg-light small shadow-sm">
                        <div class="fw-bold text-success">Port: ${port}</div>
                        <div class="text-muted mb-2 small">Function: ${func}</div>
                        
                        <input type="text" class="form-control form-control-sm mb-1 maan-circuit" data-port="${port}" placeholder="Circuit Name">
                        <input type="text" class="form-control form-control-sm mb-1 maan-cable" data-port="${port}" placeholder="Cable Data">
                        <input type="text" class="form-control form-control-sm mb-1 maan-end" data-port="${port}" placeholder="System End">
                        <input type="text" class="form-control form-control-sm maan-remarks" data-port="${port}" placeholder="Remarks">
                    </div>
                </div>
            `);
        });
    }

    // --- CPAN B Node Logic ---
    function getSelectedXsv3Slots() {
        return $('.xsv3-slot:checked').map(function() {
            return $(this).val();
        }).get().sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
    }

    function enforceXsv3SlotLimit() {
        const limit = parseInt($('#xsv3-count').val()) || 0;
        const allSlots = $('.xsv3-slot');
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

    function updateStmSection() {
        const selectedSlots = $('.stm-slot:checked').map(function() { return $(this).val(); }).get().sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
        const container = $('#stm-port-details');
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

    function updateMsv1Section() {
        const selectedSlots = $('.msv1-slot:checked').map(function() { return $(this).val(); }).get().sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
        const container = $('#msv1-port-details');
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

    // Event Bindings for CPAN B
    $(document).on('change', '#xsv3-count', updateXsv3Section);
    $(document).on('change', '.xsv3-slot', function() {
        const limit = parseInt($('#xsv3-count').val()) || 0;
        if (limit > 0 && $(this).prop('checked')) {
            if ($('.xsv3-slot:checked').length > limit) {
                $(this).prop('checked', false);
                alert(`XSV3 Card Inserted Slots selection is limited to ${limit}.`);
            }
        }
        updateXsv3Section();
    });

    $(document).on('change', '#stm-available', function() {
        if (this.value === 'Y') {
            $('#stm-slots-container').show();
            updateStmSection();
        } else {
            $('#stm-slots-container').hide();
            $('.stm-slot').prop('checked', false);
            $('#stm-port-details').empty();
        }
    });
    $(document).on('change', '.stm-slot', updateStmSection);
    $(document).on('change', '.msv1-slot', updateMsv1Section);

    $(document).on('change', '#gsv4-available', function() {
        if (this.value === 'Y') {
            $('#gsv4-slots-container').show();
            updateGsv4Section();
        } else {
            $('#gsv4-slots-container').hide();
            $('.gsv4-slot').prop('checked', false);
            $('#gsv4-port-details').empty();
        }
    });
    $(document).on('change', '.gsv4-slot', updateGsv4Section);

    $(document).on('change', '#sncv1-available', function() {
        if (this.value === 'Y') {
            $('#sncv1-slots-container').show();
            updateSncv1Section();
        } else {
            $('#sncv1-slots-container').hide();
            $('.sncv1-slot').prop('checked', false);
            $('#sncv1-port-details').empty();
        }
    });
    $(document).on('change', '.sncv1-slot', updateSncv1Section);

    $(document).on('change', '#e1cv1-available', function() {
        if (this.value === 'Y') {
            $('#e1cv1-details-container').show();
            $('#e1cv1-ddf-details').prop('required', true);
        } else {
            $('#e1cv1-details-container').hide();
            $('#e1cv1-ddf-details').val('').prop('required', false);
        }
    });

    function updateGsv4Section() {
        const selectedSlots = $('.gsv4-slot:checked').map(function() { return $(this).val(); }).get().sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
        const container = $('#gsv4-port-details');
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

    function updateSncv1Section() {
        const selectedSlots = $('.sncv1-slot:checked').map(function() { return $(this).val(); }).get().sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
        const container = $('#sncv1-port-details');
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

    function clearCPANBConfiguration() {
        $('#xsv3-count').val('');
        $('.xsv3-slot').prop('checked', false);
        $('#xsv3-port-details').empty();
        $('#xsv3-uplink-ports').val('');
        $('#stm-available').val('N');
        $('#stm-slots-container').hide();
        $('.stm-slot').prop('checked', false);
        $('#stm-port-details').empty();
        $('.msv1-slot').prop('checked', false);
        $('#msv1-port-details').empty();
        $('#gsv4-available').val('N');
        $('#gsv4-slots-container').hide();
        $('.gsv4-slot').prop('checked', false);
        $('#gsv4-port-details').empty();
        $('#sncv1-available').val('N');
        $('#sncv1-slots-container').hide();
        $('.sncv1-slot').prop('checked', false);
        $('#sncv1-port-details').empty();
        $('#e1cv1-available').val('N');
        $('#e1cv1-details-container').hide();
        $('#e1cv1-ddf-details').val('');
    }

    // Handle Form Submission
    $('form').on('submit', function(e) {
        const type = eqTypeSelect.val();
        const ipVal = String(nodeIpInput.val() || '').trim();
        const total = parseInt($('#id_total_ports').val(), 10);
        const used = parseInt($('#id_used_ports').val(), 10);

        if (Number.isFinite(total) && Number.isFinite(used) && used > total) {
            alert('Used Ports cannot be greater than Total Ports.');
            e.preventDefault();
            return false;
        }

        if (needsNodeIp(type)) {
            if (!isValidIpv4(ipVal)) {
                alert('Please enter a valid Node IP Address (IPv4).');
                e.preventDefault();
                return false;
            }
        }
        
        if (type === 'CPAN_B') {
            if (window.CPANBNodeEngine) {
                const config = window.CPANBNodeEngine.collect(ipVal);
                if (!config) {
                    e.preventDefault();
                    return false;
                }
                $('#id_configuration_json').val(JSON.stringify(config));
            }
        } 
        else if (type === 'MAAN_A3_A4') {
            const config = {
                type: 'MAAN_A3_A4',
                node_ip: ipVal,
                ports: []
            };

            $('.maan-circuit').each(function() {
                const port = $(this).data('port');
                config.ports.push({
                    port: port,
                    circuit: $(this).val(),
                    cable: $(`.maan-cable[data-port="${port}"]`).val(),
                    system_end: $(`.maan-end[data-port="${port}"]`).val(),
                    remarks: $(`.maan-remarks[data-port="${port}"]`).val()
                });
            });

            $('#id_configuration_json').val(JSON.stringify(config));
        } else if (type === 'MAAN_C') {
            initMaanCSection();

            const occupied = new Set();
            const cardConfig = {};

            for (const card of maanCCards) {
                const available = $(card.availableSel).val();
                const selectedSlots = available === 'Y' ? getMaanCSelectedSlots(card.key) : [];
                const count = available === 'Y' ? (parseInt($(card.countSel).val(), 10) || 0) : 0;

                if (available === 'Y') {
                    if (count <= 0) {
                        alert(`Please enter Number of Cards for ${card.key.toUpperCase()}.`);
                        e.preventDefault();
                        return false;
                    }

                    if (selectedSlots.length !== count) {
                        alert(`Slot count must match Number of Cards for ${card.key.toUpperCase()}.`);
                        e.preventDefault();
                        return false;
                    }

                    for (const slot of selectedSlots) {
                        if (occupied.has(slot)) {
                            alert(`Slot ${slot} already assigned to another card.`);
                            e.preventDefault();
                            return false;
                        }
                        occupied.add(slot);
                    }
                }

                cardConfig[card.key] = { available, count, slots: selectedSlots };
            }

            if (cardConfig.cel16 && cardConfig.cel16.available === 'Y') {
                const uplinks = [];
                const ports = [];
                cardConfig.cel16.slots.forEach(slot => {
                    uplinks.push(`${slot}/5`);
                    uplinks.push(`${slot}/6`);
                    [1,2,3,4,5,6].forEach(p => {
                        const port = `${slot}/${p}`;
                        ports.push({
                            port,
                            capacity: p <= 4 ? '10G' : '100G Uplink',
                            circuit: $(`.maan-c-cel16-circuit[data-port="${port}"]`).val() || '',
                            system_end: $(`.maan-c-cel16-end[data-port="${port}"]`).val() || '',
                            cable: $(`.maan-c-cel16-cable[data-port="${port}"]`).val() || ''
                        });
                    });
                });
                cardConfig.cel16.uplink_ports = uplinks;
                cardConfig.cel16.ports = ports;
            }

            if (cardConfig.cel13 && cardConfig.cel13.available === 'Y') {
                const ports = [];
                cardConfig.cel13.slots.forEach(slot => {
                    [1,2,3,4,5,6,7,8].forEach(p => {
                        const port = `${slot}/${p}`;
                        ports.push({
                            port,
                            capacity: p <= 4 ? '10G' : 'STM E1',
                            circuit: $(`.maan-c-cel13-circuit[data-port="${port}"]`).val() || '',
                            system_end: $(`.maan-c-cel13-end[data-port="${port}"]`).val() || '',
                            cable: $(`.maan-c-cel13-cable[data-port="${port}"]`).val() || ''
                        });
                    });
                });
                cardConfig.cel13.ports = ports;
            }

            if (cardConfig.cel12 && cardConfig.cel12.available === 'Y') {
                const ports = [];
                cardConfig.cel12.slots.forEach(slot => {
                    [1,2,3,4,5,6,7,8].forEach(p => {
                        const port = `${slot}/${p}`;
                        ports.push({
                            port,
                            capacity: '10G',
                            circuit: $(`.maan-c-cel12-circuit[data-port="${port}"]`).val() || '',
                            system_end: $(`.maan-c-cel12-end[data-port="${port}"]`).val() || '',
                            cable: $(`.maan-c-cel12-cable[data-port="${port}"]`).val() || ''
                        });
                    });
                });
                cardConfig.cel12.ports = ports;
            }

            if (cardConfig.cel6 && cardConfig.cel6.available === 'Y') {
                const ports = [];
                cardConfig.cel6.slots.forEach(slot => {
                    [1,2,3,4,5,6,7,8].forEach(p => {
                        const port = `${slot}/${p}`;
                        ports.push({
                            port,
                            capacity: '1G',
                            circuit: $(`.maan-c-cel6-circuit[data-port="${port}"]`).val() || '',
                            system_end: $(`.maan-c-cel6-end[data-port="${port}"]`).val() || '',
                            cable: $(`.maan-c-cel6-cable[data-port="${port}"]`).val() || ''
                        });
                    });
                });
                cardConfig.cel6.ports = ports;
            }

            if (cardConfig.csc1 && cardConfig.csc1.available === 'Y') {
                const ports = [];
                cardConfig.csc1.slots.forEach(slot => {
                    [1,2,3,4,5,6,7,8,9,10,11].forEach(p => {
                        const port = `${slot}/${p}`;
                        ports.push({
                            port,
                            capacity: 'CSC',
                            circuit: $(`.maan-c-csc1-circuit[data-port="${port}"]`).val() || '',
                            system_end: $(`.maan-c-csc1-end[data-port="${port}"]`).val() || '',
                            cable: $(`.maan-c-csc1-cable[data-port="${port}"]`).val() || ''
                        });
                    });
                });
                cardConfig.csc1.ports = ports;
            }

            if (cardConfig.csc2 && cardConfig.csc2.available === 'Y') {
                const ports = [];
                cardConfig.csc2.slots.forEach(slot => {
                    [1,2,3,4,5,6,7,8,9,10,11].forEach(p => {
                        const port = `${slot}/${p}`;
                        ports.push({
                            port,
                            capacity: 'CSC',
                            circuit: $(`.maan-c-csc2-circuit[data-port="${port}"]`).val() || '',
                            system_end: $(`.maan-c-csc2-end[data-port="${port}"]`).val() || '',
                            cable: $(`.maan-c-csc2-cable[data-port="${port}"]`).val() || ''
                        });
                    });
                });
                cardConfig.csc2.ports = ports;
            }

            const config = { type: 'MAAN_C', node_ip: ipVal, cards: cardConfig };
            $('#id_configuration_json').val(JSON.stringify(config));
        } else if (type === 'MADM') {
            initMadmSection();

            const cardConfig = {};
            const occupied = new Set();

            const defs = [
                { key: 'com01', availableSel: '#madm-com01-available', ports: 3, typeFn: () => 'Coaxial' },
                { key: 'agg06', availableSel: '#madm-agg06-available', ports: 16, typeFn: p => (p <= 4 || p >= 13 ? 'Coaxial' : 'Optical') },
                { key: 'elan05d', availableSel: '#madm-elan05d-available', ports: 72, typeFn: p => ((p >= 1 && p <= 16) || (p >= 37 && p <= 52) ? 'LAN' : 'Optical') },
                { key: 'a010000', availableSel: '#madm-a010000-available', ports: 1, typeFn: () => 'Uplink' }
            ];

            function getSlots(cardKey) {
                const values = $('#madm-config-sections').find(`.madm-slot[data-card="${cardKey}"]:checked`).map(function() {
                    return $(this).val();
                }).get();
                return values.sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
            }

            for (const def of defs) {
                const available = String($(def.availableSel).val() || '').trim().toUpperCase();
                const slots = available === 'Y' ? getSlots(def.key) : [];

                if (available === 'Y') {
                    if (def.key === 'a010000' && slots.length > 2) {
                        alert('A010000 supports maximum 2 uplink slots only.');
                        e.preventDefault();
                        return false;
                    }
                    for (const slot of slots) {
                        if (occupied.has(slot)) {
                            alert(`Slot ${slot} already assigned to another card.`);
                            e.preventDefault();
                            return false;
                        }
                        occupied.add(slot);
                    }
                }

                cardConfig[def.key] = { available, count: slots.length, slots };
            }

            const ports = [];
            for (const def of defs) {
                if (def.ports <= 0) continue;
                if (!cardConfig[def.key] || cardConfig[def.key].available !== 'Y') continue;

                for (const slot of cardConfig[def.key].slots) {
                    for (let p = 1; p <= def.ports; p++) {
                        const port = `${slot}/${p}`;
                        ports.push({
                            card_type: def.key.toUpperCase(),
                            slot_number: parseInt(slot, 10),
                            port_name: port,
                            port_type: def.typeFn(p),
                            circuit_name: $(`.madm-${def.key}-circuit[data-port="${port}"]`).val() || '',
                            other_system_end: $(`.madm-${def.key}-end[data-port="${port}"]`).val() || '',
                            cable_details: $(`.madm-${def.key}-cable[data-port="${port}"]`).val() || ''
                        });
                    }
                }
            }

            const config = { type: 'MADM', node_ip: ipVal, madm: { cards: cardConfig, ports } };
            $('#id_configuration_json').val(JSON.stringify(config));
        } else if (needsNodeIp(type)) {
            const config = { type, node_ip: ipVal };
            $('#id_configuration_json').val(JSON.stringify(config));
        }
    });

    const existingConfigStr = $('#id_configuration_json').val();
    if (existingConfigStr) {
        try {
            const existingConfig = JSON.parse(existingConfigStr);
            if (existingConfig && existingConfig.node_ip) {
                nodeIpSection.show();
                nodeIpInput.prop('required', true).val(existingConfig.node_ip);
            }
            if (existingConfig && existingConfig.type === 'CPAN_B') {
                if (existingConfig.xsv3) {
                    $('#xsv3-count').val(existingConfig.xsv3.count || '').trigger('change');
                    if (Array.isArray(existingConfig.xsv3.slots)) {
                        existingConfig.xsv3.slots.forEach(slot => $(`.xsv3-slot[value="${slot}"]`).prop('checked', true));
                        updateXsv3Section();
                    }
                    if (Array.isArray(existingConfig.xsv3.ports)) {
                        existingConfig.xsv3.ports.forEach(p => {
                            $(`.xsv3-cable[data-port="${p.port}"]`).val(p.cable || '');
                            $(`.xsv3-end[data-port="${p.port}"]`).val(p.system_end || '');
                        });
                    }
                }
                if (existingConfig.stm) {
                    $('#stm-available').val(existingConfig.stm.available || 'N').trigger('change');
                    if (Array.isArray(existingConfig.stm.slots)) {
                        existingConfig.stm.slots.forEach(slot => $(`.stm-slot[value="${slot}"]`).prop('checked', true));
                        updateStmSection();
                    }
                    if (Array.isArray(existingConfig.stm.ports)) {
                        existingConfig.stm.ports.forEach(p => {
                            $(`.stm-cable[data-port="${p.port}"]`).val(p.cable || '');
                            $(`.stm-end[data-port="${p.port}"]`).val(p.system_end || '');
                        });
                    }
                }
                if (existingConfig.msv1) {
                    if (Array.isArray(existingConfig.msv1.slots)) {
                        existingConfig.msv1.slots.forEach(slot => $(`.msv1-slot[value="${slot}"]`).prop('checked', true));
                        updateMsv1Section();
                    }
                    if (Array.isArray(existingConfig.msv1.ports)) {
                        existingConfig.msv1.ports.forEach(p => {
                            $(`.msv1-sfp[data-port="${p.port}"]`).val(p.sfp || 'Single');
                            $(`.msv1-cable[data-port="${p.port}"]`).val(p.cable || '');
                            $(`.msv1-end[data-port="${p.port}"]`).val(p.system_end || '');
                        });
                    }
                }
                if (existingConfig.gsv4) {
                    $('#gsv4-available').val(existingConfig.gsv4.available || 'N').trigger('change');
                    if (Array.isArray(existingConfig.gsv4.slots)) {
                        existingConfig.gsv4.slots.forEach(slot => $(`.gsv4-slot[value="${slot}"]`).prop('checked', true));
                        updateGsv4Section();
                    }
                    if (Array.isArray(existingConfig.gsv4.ports)) {
                        existingConfig.gsv4.ports.forEach(p => {
                            $(`.gsv4-circuit[data-port="${p.port}"]`).val(p.circuit_name || '');
                            $(`.gsv4-cable[data-port="${p.port}"]`).val(p.cable || '');
                            $(`.gsv4-end[data-port="${p.port}"]`).val(p.system_end || '');
                        });
                    }
                }
                if (existingConfig.sncv1) {
                    $('#sncv1-available').val(existingConfig.sncv1.available || 'N').trigger('change');
                    if (Array.isArray(existingConfig.sncv1.slots)) {
                        existingConfig.sncv1.slots.forEach(slot => $(`.sncv1-slot[value="${slot}"]`).prop('checked', true));
                        updateSncv1Section();
                    }
                    if (Array.isArray(existingConfig.sncv1.ports)) {
                        existingConfig.sncv1.ports.forEach(p => {
                            $(`.sncv1-circuit[data-port="${p.port}"]`).val(p.circuit_name || '');
                            $(`.sncv1-cable[data-port="${p.port}"]`).val(p.cable || '');
                            $(`.sncv1-end[data-port="${p.port}"]`).val(p.system_end || '');
                        });
                    }
                }
                if (existingConfig.e1cv1) {
                    $('#e1cv1-available').val(existingConfig.e1cv1.available || 'N').trigger('change');
                    $('#e1cv1-ddf-details').val(existingConfig.e1cv1.ddf_details || '');
                }
            }
            if (existingConfig && existingConfig.type === 'MADM' && existingConfig.madm && existingConfig.madm.cards) {
                initMadmSection();
                const cards = existingConfig.madm.cards;

                const map = {
                    com01: { availableSel: '#madm-com01-available' },
                    agg06: { availableSel: '#madm-agg06-available' },
                    elan05d: { availableSel: '#madm-elan05d-available' },
                    a010000: { availableSel: '#madm-a010000-available' }
                };

                Object.keys(map).forEach(key => {
                    if (!cards[key]) return;
                    $(map[key].availableSel).val(cards[key].available || 'N').trigger('change');
                    if (Array.isArray(cards[key].slots)) {
                        cards[key].slots.forEach(slot => {
                            $('#madm-config-sections').find(`.madm-slot[data-card="${key}"][value="${slot}"]`).prop('checked', true);
                        });
                    }
                });

                if (refreshMadm) refreshMadm();

                if (Array.isArray(existingConfig.madm.ports)) {
                    existingConfig.madm.ports.forEach(p => {
                        const port = p.port_name;
                        const card = String(p.card_type || '').trim().toLowerCase();
                        const key = card === 'com01' ? 'com01' : card === 'agg06' ? 'agg06' : card === 'elan05d' ? 'elan05d' : null;
                        if (!key) return;
                        $(`.madm-${key}-circuit[data-port="${port}"]`).val(p.circuit_name || '');
                        $(`.madm-${key}-end[data-port="${port}"]`).val(p.other_system_end || '');
                        $(`.madm-${key}-cable[data-port="${port}"]`).val(p.cable_details || '');
                    });
                }
            }
        } catch (e) {}
    }
});
