
    # =====================================================
    # MACHINE CARDS GRID - UPDATED HTML RENDERING
    # =====================================================

    cols_per_row = 5 if st.session_state.compact_mode else 4

    card_cls = (
        "m-card compact"
        if st.session_state.compact_mode
        else "m-card"
    )

    for start in range(0, len(filtered), cols_per_row):
        row_cols = st.columns(cols_per_row)
        chunk = filtered.iloc[start:start + cols_per_row]

        for col, (_, m) in zip(row_cols, chunk.iterrows()):

            raw_mid = str(m["id"])
            mid = escape(raw_mid)
            mtype = escape(str(m["mtype"]))
            prog = escape(str(m["program"]))

            status = str(m["status"])
            if status not in ["Running", "Idle", "Alarm"]:
                status = "Idle"

            op = escape(str(m["operator"]))
            parts = max(safe_int(m["parts"]), 0)
            target = max(safe_int(m["target"], 1), 1)

            pct = min(int(round((parts / target) * 100)), 100)

            rpm = escape(str(m["rpm"]))
            oee = escape(str(m["oee"]))
            msg = str(m["message"]).strip()
            note = escape(str(m["note"]))
            upd = escape(str(m["updated"]))

            # STATUS BANNER
            banner_html = ""

            if msg == "GOOD WORKING":
                banner_html = (
                    '<div class="banner-good">✔ GOOD WORKING</div>'
                )
            elif msg == "PLEASE IMPROVEMENT":
                banner_html = (
                    '<div class="banner-warn">💬 PLEASE IMPROVEMENT</div>'
                )

            # MACHINE CARD HTML
            single_line_card = f"""
            <div class="{card_cls}">
                <div class="m-top">
                    <div>
                        <div class="m-id">{mid}</div>
                        <div class="m-sub">{mtype} • {prog}</div>
                    </div>
                    <span class="pill pill-{status}">
                        {escape(status)}
                    </span>
                </div>

                {banner_html}

                <div class="op-box">
                    <div>
                        <div class="m-sub" style="margin-top:0;">
                            ऑपरेटर
                        </div>
                        <div class="op-name">{op}</div>
                    </div>
                    <div>
                        <span class="mini-tag">ऑप</span>
                        <span class="mini-tag">प्रो</span>
                        <span class="mini-tag">💬</span>
                    </div>
                </div>

                <div class="prog-label">
                    <span>Progress</span>
                    <span>{parts}/{target} ({pct}%)</span>
                </div>

                <div class="prog-track">
                    <div class="prog-fill" style="width:{pct}%;"></div>
                </div>

                <div class="kpi-row">
                    <div class="kpi-box">
                        <div class="kpi-lbl">Parts</div>
                        <div class="kpi-val">{parts}</div>
                    </div>
                    <div class="kpi-box">
                        <div class="kpi-lbl">RPM</div>
                        <div class="kpi-val">{rpm}</div>
                    </div>
                    <div class="kpi-box">
                        <div class="kpi-lbl">OEE</div>
                        <div class="kpi-val">{oee}</div>
                    </div>
                </div>

                <div class="m-foot">
                    <span>{note}</span>
                    <span>{upd}</span>
                </div>
            </div>
            """

            with col:
                card_html = dedent(single_line_card).strip()

                # Render HTML as HTML, not as plain text
                st.markdown(
                    card_html,
                    unsafe_allow_html=True,
                )

                if st.button(
                    f"Edit {raw_mid}",
                    key=f"edit_btn_{raw_mid}",
                    use_container_width=True,
                ):
                    st.session_state.selected_machine = raw_mid
                    st.rerun(scope="fragment")
