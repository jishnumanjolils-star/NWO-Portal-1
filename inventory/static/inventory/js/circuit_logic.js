$(document).ready(function() {
    const nodeSelect = $('#id_customer_end_node');
    const equipmentSelect = $('#id_equipment');
    const sections = $('.node-section');
    const portContainer = $('#port-details-container');
    const portLabel = $('#port-logic-label');
    const nodeIpSection = $('#section-node-ip');
    const nodeIpInput = $('#node-ip');
    let madmInitialized = false;

    const bandwidthInput = $('#id_bandwidth');
    const ringSection = $('#section-circuit-ring');
    const ringDetailsSection = $('#section-circuit-ring-details');
    const ringImageInput = $('#id_ring_image');
    const ringSummaryInput = $('#id_ring_summary');

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

    function needsNodeIp(nodeType) {
        return ['A_NODE', 'MAAN_A3_A4', 'MADM', 'CPE', 'CPAN_B'].includes(nodeType);
    }

    let currentEquipmentType = '';

    function checkCpanVisibility() {
        const nodeVal = nodeSelect.val();
        const equipmentId = equipmentSelect.val();

        if (nodeVal === 'CPAN_B') {
            $('#section-cpan-details').show();
            if (window.CPANBNodeEngine) {
                window.CPANBNodeEngine.initialize();
            }
        } else if (equipmentId) {
            // Fetch equipment type from API
            $.get(`/api/equipment/${equipmentId}/`, function(data) {
                if (data.equipment_type === 'CPAN_B') {
                    $('#section-cpan-details').show();
                    if (window.CPANBNodeEngine) {
                        window.CPANBNodeEngine.initialize();
                    }
                } else {
                    $('#section-cpan-details').hide();
                    if (window.CPANBNodeEngine) {
                        window.CPANBNodeEngine.clear();
                    }
                }
            }).fail(function() {
                $('#section-cpan-details').hide();
                if (window.CPANBNodeEngine) {
                    window.CPANBNodeEngine.clear();
                }
            });
        } else {
            $('#section-cpan-details').hide();
            if (window.CPANBNodeEngine) {
                window.CPANBNodeEngine.clear();
            }
        }
    }

    function parseBandwidthToMbps(val) {
        const s = String(val || '').trim().toLowerCase();
        if (!s) return null;
        const m = s.match(/(\d+(?:\.\d+)?)\s*([a-z]+)?/);
        if (!m) return null;
        const num = parseFloat(m[1]);
        const unit = (m[2] || 'mbps').toLowerCase();
        if (!Number.isFinite(num)) return null;

        if (unit === 'g' || unit === 'gb' || unit === 'gbps') return num * 1000;
        if (unit === 'k' || unit === 'kb' || unit === 'kbps') return num / 1000;
        if (unit === 'm' || unit === 'mb' || unit === 'mbps') return num;
        return num;
    }

    function getIsRingSelected() {
        const select = $('#id_is_ring');
        if (select.length && select.is('select')) {
            const v = String(select.val() || '').toLowerCase();
            return v === 'true' || v === '1' || v === 'yes' || v === 'y';
        }
        const checked = $('input[name="is_ring"]:checked');
        if (checked.length) {
            const v = String(checked.val() || '').toLowerCase();
            return v === 'true' || v === '1' || v === 'yes' || v === 'y';
        }
        return false;
    }

    function setIsRingNo() {
        const radioNo = $('input[name="is_ring"]').filter(function() {
            return String($(this).val() || '').toLowerCase() === 'false' || String($(this).val() || '').toLowerCase() === '0';
        }).first();
        if (radioNo.length) {
            if (!radioNo.prop('checked')) {
                radioNo.prop('checked', true).trigger('change');
            }
            return;
        }
        const select = $('#id_is_ring');
        if (select.length && select.is('select')) {
            if (select.val() !== 'False') {
                select.val('False').trigger('change');
            }
            return;
        }
    }

    function updateRingUI() {
        const bwMbps = parseBandwidthToMbps(bandwidthInput.val());
        const showRing = bwMbps !== null && bwMbps > 10;

        if (!showRing) {
            ringSection.hide();
            ringDetailsSection.hide();
            setIsRingNo();
            if (ringSummaryInput.length) ringSummaryInput.val('');
            if (ringImageInput.length) ringImageInput.val('');
            $('#ring-image-preview-wrap').hide();
            $('#ring-image-preview').attr('src', '');
            return;
        }

        ringSection.show();
        const isRing = getIsRingSelected();
        if (isRing) {
            ringDetailsSection.show();
        } else {
            ringDetailsSection.hide();
            if (ringSummaryInput.length) ringSummaryInput.val('');
            if (ringImageInput.length) ringImageInput.val('');
            $('#ring-image-preview-wrap').hide();
            $('#ring-image-preview').attr('src', '');
        }
    }

    bandwidthInput.on('input change', updateRingUI);
    $(document).on('change', '#id_is_ring, input[name="is_ring"]', updateRingUI);
    ringImageInput.on('change', function() {
        const wrap = $('#ring-image-preview-wrap');
        const img = $('#ring-image-preview');
        wrap.hide();
        img.attr('src', '');
        if (!this.files || !this.files.length) return;
        const file = this.files[0];
        const ext = String(file.name || '').split('.').pop().toLowerCase();
        if (ext !== 'jpg' && ext !== 'jpeg') {
            alert('Please upload only JPG or JPEG images.');
            $(this).val('');
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            alert('Ring image must be 5 MB or smaller.');
            $(this).val('');
            return;
        }
        const reader = new FileReader();
        reader.onload = function(e) {
            img.attr('src', e.target.result);
            wrap.show();
        };
        reader.readAsDataURL(file);
    });

    nodeSelect.on('change', function() {
        const val = this.value;
        sections.hide();
        nodeIpSection.hide();
        nodeIpInput.prop('required', false);
        
        if (val === 'MEDIA_CONVERTER') {
            $('#section-media-converter').show();
            $('#id_mc_type').prop('required', true);
        } else {
            $('#id_mc_type').prop('required', false);
        }

        if (needsNodeIp(val)) {
            nodeIpSection.show();
            nodeIpInput.prop('required', true);
        } else {
            nodeIpInput.val('');
        }

        if (val === 'A_NODE') {
            $('#section-port-config').show();
            portLabel.text('A-Node (GE3-GE6)');
            generatePorts(['GE3', 'GE4', 'GE5', 'GE6']);
        } else if (val === 'MAAN_A3_A4') {
            $('#section-port-config').show();
            portLabel.text(`${val} (P1-P24, E1-E4)`);
            const ports = [];
            for (let i = 1; i <= 24; i++) ports.push(`P${i}`);
            for (let i = 1; i <= 4; i++) ports.push(`E${i}`);
            generatePorts(ports);
        } else if (val === 'CPAN_B') {
            checkCpanVisibility();
        } else if (val === 'MADM') {
            $('#section-madm').show();
            initMadmSection();
        } else {
            portContainer.empty();
        }
    }).trigger('change');

    equipmentSelect.on('change', checkCpanVisibility);

    updateRingUI();

    function generatePorts(ports) {
        const existingPorts = portContainer.find('.port-block').map(function() { return $(this).data('port'); }).get();
        if (JSON.stringify(existingPorts) === JSON.stringify(ports)) return;

        portContainer.empty();
        ports.forEach(port => {
            portContainer.append(`
                <div class="col-md-4 mb-3 port-block" data-port="${port}">
                    <div class="border p-2 rounded bg-light shadow-sm">
                        <div class="fw-bold text-success mb-2">Port: ${port}</div>
                        <input type="text" class="form-control form-control-sm mb-1 circuit-input" data-port="${port}" placeholder="Connected Circuit">
                        <input type="text" class="form-control form-control-sm mb-1 cable-input" data-port="${port}" placeholder="Cable Name">
                        <input type="text" class="form-control form-control-sm end-input" data-port="${port}" placeholder="System End">
                    </div>
                </div>
            `);
        });
    }

    function initMadmSection() {
        if (madmInitialized) return;
        madmInitialized = true;

        const section = $('#section-madm');
        const cards = [
            { key: 'com01', availableSel: '#circuit-madm-com01-available', fieldsSel: '#circuit-madm-com01-fields', portSel: '#circuit-madm-com01-port-details' },
            { key: 'agg06', availableSel: '#circuit-madm-agg06-available', fieldsSel: '#circuit-madm-agg06-fields', portSel: '#circuit-madm-agg06-port-details' },
            { key: 'elan05d', availableSel: '#circuit-madm-elan05d-available', fieldsSel: '#circuit-madm-elan05d-fields', portSel: '#circuit-madm-elan05d-port-details' },
            { key: 'a010000', availableSel: '#circuit-madm-a010000-available', fieldsSel: '#circuit-madm-a010000-fields', portSel: '#circuit-madm-a010000-port-details' }
        ];

        function isCardAvailable(cardKey) {
            const card = cards.find(c => c.key === cardKey);
            if (!card) return false;
            return String($(card.availableSel).val() || '').trim().toUpperCase() === 'Y';
        }

        function getSelectedSlots(cardKey) {
            const values = section.find(`.circuit-madm-slot[data-card="${cardKey}"]:checked`).map(function() {
                return $(this).val();
            }).get();
            return values.sort((a, b) => parseInt(a, 10) - parseInt(b, 10));
        }

        function setCardEnabled(cardKey, enabled) {
            const card = cards.find(c => c.key === cardKey);
            if (!card) return;

            if (enabled) {
                $(card.fieldsSel).show();
                section.find(`.circuit-madm-slot[data-card="${cardKey}"]`).prop('disabled', false);
            } else {
                $(card.fieldsSel).hide();
                section.find(`.circuit-madm-slot[data-card="${cardKey}"]`).prop('checked', false).prop('disabled', true);
                if (card.portSel) $(card.portSel).empty();
            }
        }

        function occupiedSlots() {
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
                        <td><input type="text" class="form-control form-control-sm circuit-madm-${cardKey}-circuit" data-port="${port}"></td>
                        <td><input type="text" class="form-control form-control-sm circuit-madm-${cardKey}-end" data-port="${port}"></td>
                        <td><input type="text" class="form-control form-control-sm circuit-madm-${cardKey}-cable" data-port="${port}"></td>
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

        function updatePorts() {
            const occupied = occupiedSlots();

            section.find('.circuit-madm-slot').each(function() {
                const slot = $(this).val();
                const cardKey = $(this).data('card');
                const owner = occupied[slot];
                const shouldDisable = owner && owner !== cardKey;
                if (shouldDisable && $(this).prop('checked')) $(this).prop('checked', false);
                $(this).prop('disabled', shouldDisable);
            });

            $('#circuit-madm-com01-port-details').empty();
            $('#circuit-madm-agg06-port-details').empty();
            $('#circuit-madm-elan05d-port-details').empty();
            $('#circuit-madm-a010000-port-details').empty();

            if (isCardAvailable('com01')) {
                getSelectedSlots('com01').forEach(slot => {
                    $('#circuit-madm-com01-port-details').append(renderPorts('com01', slot, 3, () => 'Coaxial'));
                });
            }
            if (isCardAvailable('agg06')) {
                getSelectedSlots('agg06').forEach(slot => {
                    $('#circuit-madm-agg06-port-details').append(renderPorts('agg06', slot, 16, p => (p <= 4 || p >= 13 ? 'Coaxial' : 'Optical')));
                });
            }
            if (isCardAvailable('elan05d')) {
                getSelectedSlots('elan05d').forEach(slot => {
                    $('#circuit-madm-elan05d-port-details').append(renderPorts('elan05d', slot, 72, p => ((p >= 1 && p <= 16) || (p >= 37 && p <= 52) ? 'LAN' : 'Optical')));
                });
            }

            if (isCardAvailable('a010000')) {
                const slots = getSelectedSlots('a010000');
                slots.forEach(slot => {
                    const port = `${slot}/1`;
                    $('#circuit-madm-a010000-port-details').append(`
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
                                                <td><input type="text" class="form-control form-control-sm circuit-madm-a010000-circuit" data-port="${port}"></td>
                                                <td><input type="text" class="form-control form-control-sm circuit-madm-a010000-end" data-port="${port}"></td>
                                                <td><input type="text" class="form-control form-control-sm circuit-madm-a010000-cable" data-port="${port}"></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    `);
                });
            }

            const warning = $('#circuit-madm-a010000-warning');
            warning.hide();
            if (isCardAvailable('a010000')) {
                const slots = getSelectedSlots('a010000');
                if (slots.some(s => parseInt(s, 10) < 7)) warning.show();
            }
        }

        cards.forEach(card => {
            $(card.availableSel).on('change', function() {
                setCardEnabled(card.key, isCardAvailable(card.key));
                updatePorts();
            });
            setCardEnabled(card.key, isCardAvailable(card.key));
        });

        $(document).on('change', '#section-madm .circuit-madm-slot', function() {
            const cardKey = String($(this).data('card') || '');
            if (cardKey === 'a010000' && $(this).prop('checked')) {
                const count = getSelectedSlots('a010000').length;
                if (count > 2) {
                    $(this).prop('checked', false);
                    alert('A010000 supports maximum 2 uplink slots only.');
                }
            }
            updatePorts();
        });
        updatePorts();
    }

    // CPAN B Node Logic is handled by unified window.CPANBNodeEngine

    $('form').on('submit', function(e) {
        const val = nodeSelect.val();
        let config = { type: val };
        const ipVal = String(nodeIpInput.val() || '').trim();

        const bwMbps = parseBandwidthToMbps(bandwidthInput.val());
        const showRing = bwMbps !== null && bwMbps > 10;
        const isRing = getIsRingSelected();
        if (showRing && isRing) {
            const summary = String(ringSummaryInput.val() || '').trim();
            if (!summary) {
                alert('Ring Summary is mandatory when Bandwidth > 10 Mbps and Circuit in Ring is Yes.');
                e.preventDefault();
                return false;
            }
            if (summary.length > 1000) {
                alert('Ring Summary must be 1000 characters or less.');
                e.preventDefault();
                return false;
            }
            if (ringImageInput.length && ringImageInput[0].files && ringImageInput[0].files.length) {
                const file = ringImageInput[0].files[0];
                const ext = String(file.name || '').split('.').pop().toLowerCase();
                if (ext !== 'jpg' && ext !== 'jpeg') {
                    alert('Please upload only JPG or JPEG images for Ring Details Upload.');
                    e.preventDefault();
                    return false;
                }
                if (file.size > 5 * 1024 * 1024) {
                    alert('Ring image must be 5 MB or smaller.');
                    e.preventDefault();
                    return false;
                }
            }
        }

        if (needsNodeIp(val)) {
            if (!isValidIpv4(ipVal)) {
                alert('Please enter a valid Node IP Address (IPv4).');
                e.preventDefault();
                return false;
            }
        }

        if (val === 'MEDIA_CONVERTER') {
            if (!$('#id_mc_type').val()) {
                alert('Type of Media Converter is mandatory');
                e.preventDefault();
                return false;
            }
        } else if (val === 'CPAN_B') {
            if (window.CPANBNodeEngine) {
                const cpanConfig = window.CPANBNodeEngine.collect(ipVal);
                if (!cpanConfig) {
                    e.preventDefault();
                    return false;
                }
                config = cpanConfig;
            }
        } else if (['A_NODE', 'MAAN_A3_A4'].includes(val)) {
            config.node_ip = ipVal;
            config.ports = [];
            $('.port-block').each(function() {
                const port = $(this).data('port');
                const circuit = $(this).find('.circuit-input').val();
                const cable = $(this).find('.cable-input').val();
                const end = $(this).find('.end-input').val();

                if (circuit || cable || end) {
                    if (!circuit || !cable || !end) {
                        alert(`Please fill all details for Port ${port} or leave it entirely empty.`);
                        e.preventDefault();
                        return false;
                    }
                    config.ports.push({ port, circuit, cable, system_end: end });
                }
            });

            if (config.ports.length === 0) {
                alert('At least one port entry is required for this node type.');
                e.preventDefault();
                return false;
            }
        } else if (val === 'MADM') {
            initMadmSection();

            const cardConfig = {};
            const occupied = new Set();
            const defs = [
                { key: 'com01', availableSel: '#circuit-madm-com01-available', ports: 3, typeFn: () => 'Coaxial' },
                { key: 'agg06', availableSel: '#circuit-madm-agg06-available', ports: 16, typeFn: p => (p <= 4 || p >= 13 ? 'Coaxial' : 'Optical') },
                { key: 'elan05d', availableSel: '#circuit-madm-elan05d-available', ports: 72, typeFn: p => ((p >= 1 && p <= 16) || (p >= 37 && p <= 52) ? 'LAN' : 'Optical') },
                { key: 'a010000', availableSel: '#circuit-madm-a010000-available', ports: 1, typeFn: () => 'Uplink' }
            ];

            function getSlots(cardKey) {
                const values = $('#section-madm').find(`.circuit-madm-slot[data-card="${cardKey}"]:checked`).map(function() {
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
                            circuit_name: $(`.circuit-madm-${def.key}-circuit[data-port="${port}"]`).val() || '',
                            other_system_end: $(`.circuit-madm-${def.key}-end[data-port="${port}"]`).val() || '',
                            cable_details: $(`.circuit-madm-${def.key}-cable[data-port="${port}"]`).val() || ''
                        });
                    }
                }
            }

            config = { type: 'MADM', node_ip: ipVal, madm: { cards: cardConfig, ports } };
        } else if (val === 'CPE') {
            config.node_ip = ipVal;
        }

        $('#id_node_configuration_json').val(JSON.stringify(config));
    });

    const existingConfigStr = $('#id_node_configuration_json').val();
    if (existingConfigStr) {
        try {
            const existingConfig = JSON.parse(existingConfigStr);
            if (existingConfig && existingConfig.node_ip) {
                nodeIpInput.val(existingConfig.node_ip);
            }
            if (existingConfig && existingConfig.type === 'MADM' && existingConfig.madm && existingConfig.madm.cards) {
                $('#section-madm').show();
                initMadmSection();

                const cards = existingConfig.madm.cards;
                const map = {
                    com01: { availableSel: '#circuit-madm-com01-available' },
                    agg06: { availableSel: '#circuit-madm-agg06-available' },
                    elan05d: { availableSel: '#circuit-madm-elan05d-available' },
                    a010000: { availableSel: '#circuit-madm-a010000-available' }
                };

                Object.keys(map).forEach(key => {
                    if (!cards[key]) return;
                    $(map[key].availableSel).val(cards[key].available || 'N').trigger('change');
                    if (Array.isArray(cards[key].slots)) {
                        cards[key].slots.forEach(slot => {
                            $('#section-madm').find(`.circuit-madm-slot[data-card="${key}"][value="${slot}"]`).prop('checked', true);
                        });
                    }
                });

                if (Array.isArray(existingConfig.madm.ports)) {
                    existingConfig.madm.ports.forEach(p => {
                        const port = p.port_name;
                        const card = String(p.card_type || '').trim().toLowerCase();
                        const key = card === 'com01' ? 'com01' : card === 'agg06' ? 'agg06' : card === 'elan05d' ? 'elan05d' : null;
                        if (!key) return;
                        $(`.circuit-madm-${key}-circuit[data-port="${port}"]`).val(p.circuit_name || '');
                        $(`.circuit-madm-${key}-end[data-port="${port}"]`).val(p.other_system_end || '');
                        $(`.circuit-madm-${key}-cable[data-port="${port}"]`).val(p.cable_details || '');
                    });
                }
            } else if (existingConfig && existingConfig.type === 'CPAN_B') {
                $('#section-cpan-details').show();
                if (window.CPANBNodeEngine) {
                    window.CPANBNodeEngine.initialize();
                    window.CPANBNodeEngine.load(existingConfig);
                }
            }
        } catch (e) {
            console.error('Error parsing existing config:', e);
        }
    }

    // Auto GPS Capture Logic
    $('#btn-capture-gps').on('click', function() {
        const btn = $(this);
        const originalHtml = btn.html();
        
        if ("geolocation" in navigator) {
            btn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span>');
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    $('#id_latitude').val(position.coords.latitude.toFixed(6));
                    $('#id_longitude').val(position.coords.longitude.toFixed(6));
                    btn.prop('disabled', false).html(originalHtml).removeClass('btn-outline-primary').addClass('btn-success');
                    setTimeout(() => btn.removeClass('btn-success').addClass('btn-outline-primary'), 2000);
                },
                function(error) {
                    alert("Error capturing location: " + error.message);
                    btn.prop('disabled', false).html(originalHtml);
                },
                { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
            );
        } else {
            alert("Geolocation is not supported by your browser.");
        }
    });
});
