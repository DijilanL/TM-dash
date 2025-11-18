import dash
from dash import html, dcc, callback, Input, Output, State
import plotly.graph_objects as go
import requests

# Página de League of Legends
dash.register_page(__name__, path="/paginaa1", name="League of Legends")

# Usaremos Data Dragon en español
DD_VERSION_CACHE = None
DD_LANG = "es_ES"
CHAMPION_OPTIONS_CACHE = None



def get_latest_dd_version():
    """
    Obtiene y cachea la última versión de Data Dragon.
    """
    global DD_VERSION_CACHE
    if DD_VERSION_CACHE is not None:
        return DD_VERSION_CACHE
    try:
        resp = requests.get(
            "https://ddragon.leagueoflegends.com/api/versions.json", timeout=8
        )
        resp.raise_for_status()
        versions = resp.json()
        DD_VERSION_CACHE = versions[0]  
    except Exception:
        
        DD_VERSION_CACHE = "15.1.1"
    return DD_VERSION_CACHE


def fetch_all_champions():
    """
    Descarga la lista completa de campeones para llenar el dropdown
    (en español, pero con el 'id' oficial).
    """
    global CHAMPION_OPTIONS_CACHE
    if CHAMPION_OPTIONS_CACHE is not None:
        return CHAMPION_OPTIONS_CACHE

    version = get_latest_dd_version()
    url = (
        f"https://ddragon.leagueoflegends.com/cdn/"
        f"{version}/data/{DD_LANG}/champion.json"
    )
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        champs = data.get("data", {})
        options = []
        for champ_id, champ_info in champs.items():
            name = champ_info.get("name", champ_id)
            options.append({"label": name, "value": champ_id})
       
        options.sort(key=lambda o: o["label"])
        CHAMPION_OPTIONS_CACHE = options
        return options
    except Exception:
       
        CHAMPION_OPTIONS_CACHE = [
            {"label": "Ahri", "value": "Ahri"},
            {"label": "Lux", "value": "Lux"},
            {"label": "Yasuo", "value": "Yasuo"},
            {"label": "Garen", "value": "Garen"},
        ]
        return CHAMPION_OPTIONS_CACHE


def fetch_champion_data(champ_id: str) -> dict:
    """
    Descarga la info de un campeón concreto (en español).
    """
    version = get_latest_dd_version()
    url = (
        f"https://ddragon.leagueoflegends.com/cdn/"
        f"{version}/data/{DD_LANG}/champion/{champ_id}.json"
    )
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        champ_data = data.get("data", {}).get(champ_id, {})
        if not champ_data:
            return {"id": champ_id, "name": champ_id, "title": ""}
        return champ_data
    except Exception:
        return {"id": champ_id, "name": champ_id, "title": ""}


def build_stats_figure(champ_data: dict, level: int):
    """
    Gráfica 1: stats base vs stats al nivel elegido.
    """
    stats = champ_data.get("stats")
    if not isinstance(stats, dict):
        fig = go.Figure()
        fig.add_annotation(
            text="No hay estadísticas disponibles para este campeón.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=40, r=40, t=60, b=120),
            height=420,
        )
        return fig

    lvl = max(1, min(int(level or 1), 18))

    stats_cfg = [
        ("Vida", "hp", "hpperlevel"),
        ("Maná / Recurso", "mp", "mpperlevel"),
        ("AD", "attackdamage", "attackdamageperlevel"),
        ("Armadura", "armor", "armorperlevel"),
        ("Resist. mágica", "spellblock", "spellblockperlevel"),
        ("Vel. de ataque", "attackspeed", "attackspeedperlevel"),
    ]

    labels = []
    base_vals = []
    lvl_vals = []

    for label, base_key, per_key in stats_cfg:
        base = float(stats.get(base_key, 0.0))
        per = float(stats.get(per_key, 0.0))
        val_lvl = base + (lvl - 1) * per
        labels.append(label)
        base_vals.append(base)
        lvl_vals.append(val_lvl)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=labels,
            y=base_vals,
            name="Nivel 1",
            marker=dict(line=dict(width=0.5)),
            hovertemplate="%{x}<br>Valor: %{y:.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=labels,
            y=lvl_vals,
            name=f"Nivel {lvl}",
            marker=dict(line=dict(width=0.5)),
            hovertemplate="%{x}<br>Valor: %{y:.2f}<extra></extra>",
        )
    )

    champ_name = champ_data.get("name", "")
    fig.update_layout(
        title=dict(
            text=f"<b>Stats base vs nivel {lvl} — {champ_name}</b>",
            x=0.5,
            font=dict(size=16),
        ),
        barmode="group",
        xaxis_title="Estadística",
        yaxis_title="Valor",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=60, r=40, t=80, b=130),
        font=dict(family="Outfit", size=12),
        legend=dict(
            orientation="h",
            x=0.5,
            y=-0.25,          # leyenda abajo
            xanchor="center",
            yanchor="top",
        ),
        height=430,
    )
    fig.update_xaxes(tickangle=-35)
    fig.update_yaxes(rangemode="tozero", showgrid=True, gridwidth=1, gridcolor="#eee")
    return fig


def build_scaling_figure(champ_data: dict, level: int):
    """
    Gráfica 2: cuánto escala cada stat (total y por nivel).
    """
    stats = champ_data.get("stats")
    if not isinstance(stats, dict):
        fig = go.Figure()
        fig.add_annotation(
            text="No hay estadísticas disponibles para este campeón.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=40, r=40, t=60, b=120),
            height=360,
        )
        return fig

    lvl = max(1, min(int(level or 1), 18))

    stats_cfg = [
        ("Vida", "hp", "hpperlevel"),
        ("Maná / Recurso", "mp", "mpperlevel"),
        ("AD", "attackdamage", "attackdamageperlevel"),
        ("Armadura", "armor", "armorperlevel"),
        ("Resist. mágica", "spellblock", "spellblockperlevel"),
        ("Vel. de ataque", "attackspeed", "attackspeedperlevel"),
    ]

    labels = []
    inc_totales = []
    per_levels = []

    for label, _, per_key in stats_cfg:
        per = float(stats.get(per_key, 0.0))
        delta = (lvl - 1) * per
        labels.append(label)
        inc_totales.append(delta)
        per_levels.append(per)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=labels,
            y=inc_totales,
            name=f"Incremento total (1 → {lvl})",
            marker=dict(line=dict(width=0.5)),
            hovertemplate="%{x}<br>Δ total: %{y:.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=labels,
            y=per_levels,
            name="Crecimiento por nivel",
            marker=dict(line=dict(width=0.5)),
            hovertemplate="%{x}<br>Por nivel: %{y:.2f}<extra></extra>",
        )
    )

    champ_name = champ_data.get("name", "")
    fig.update_layout(
        title=dict(
            text=f"<b>Escalado de stats hasta nivel {lvl} — {champ_name}</b>",
            x=0.5,
            font=dict(size=16),
        ),
        barmode="group",
        xaxis_title="Estadística",
        yaxis_title="Valor de crecimiento",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=60, r=40, t=70, b=130),
        font=dict(family="Outfit", size=12),
        legend=dict(
            orientation="h",
            x=0.5,
            y=-0.25,         
            xanchor="center",
            yanchor="top",
        ),
        height=380,
    )
    fig.update_xaxes(tickangle=-35)
    fig.update_yaxes(rangemode="tozero", showgrid=True, gridwidth=1, gridcolor="#eee")
    return fig


def build_info_figure(champ_data: dict):
    """
    Gráfica 3: ataque / defensa / magia / dificultad (info general).
    """
    info = champ_data.get("info")
    if not isinstance(info, dict):
        fig = go.Figure()
        fig.add_annotation(
            text="Sin información de ataque/defensa/magia/dificultad.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=40, r=40, t=40, b=120),
            height=320,
        )
        return fig

    labels = ["Ataque", "Defensa", "Magia", "Dificultad"]
    vals = [
        info.get("attack", 0),
        info.get("defense", 0),
        info.get("magic", 0),
        info.get("difficulty", 0),
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=labels,
            y=vals,
            name="Perfil del campeón",
            marker=dict(line=dict(width=0.5)),
            hovertemplate="%{x}<br>Valor: %{y:.1f}<extra></extra>",
        )
    )
    champ_name = champ_data.get("name", "")
    fig.update_layout(
        title=dict(
            text=f"<b>Perfil general — {champ_name}</b>",
            x=0.5,
            font=dict(size=15),
        ),
        xaxis_title="Dimensión",
        yaxis_title="Valor",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=60, r=40, t=70, b=130),
        font=dict(family="Outfit", size=12),
        legend=dict(
            orientation="h",
            x=0.5,
            y=-0.25,          # leyenda abajo
            xanchor="center",
            yanchor="top",
        ),
        height=340,
    )
    fig.update_yaxes(rangemode="tozero", showgrid=True, gridwidth=1, gridcolor="#eee")
    return fig



def build_champion_card(champ_data: dict, skin_index: int):
    """
    Tarjeta con splash, nombre, título, rol, recurso y skin actual.
    """
    champ_id = champ_data.get("id", "Champion")
    champ_name = champ_data.get("name", champ_id)
    champ_title = champ_data.get("title", "")
    tags = champ_data.get("tags", [])
    partype = champ_data.get("partype", "")

    skins = champ_data.get("skins", []) or []
    total_skins = len(skins) if skins else 1
    idx = 0
    skin_name = "Predeterminada"
    skin_num = 0

    if skins:
        idx = max(0, min(skin_index, total_skins - 1))
        skin_info = skins[idx]
        skin_name = skin_info.get("name", "Predeterminada")
        skin_num = skin_info.get("num", 0)

    version = get_latest_dd_version()
    splash_url = (
        f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/"
        f"{champ_id}_{skin_num}.jpg"
    )

    roles_text = ", ".join(tags) if tags else "—"
    skin_label = f"Skin {idx + 1} de {total_skins}: {skin_name}"

    return html.Div(
        className="profile-card",
        children=[
            html.Img(
                src=splash_url,
                alt=f"{champ_name} - {skin_name}",
                className="profile-photo",
            ),
            html.Div(
                className="profile-caption",
                children=[
                    html.H4(champ_name),
                    html.P(champ_title),
                    html.P(f"Rol(es): {roles_text}"),
                    html.P(f"Recurso: {partype}" if partype else ""),
                    html.P(skin_label),
                ],
            ),
        ],
    )


def build_lore_section(champ_data: dict):
    """
    Lore, tips aliados y tips enemigos.
    """
    lore = champ_data.get("lore", "")
    allytips = champ_data.get("allytips", []) or []
    enemytips = champ_data.get("enemytips", []) or []

    short_lore = lore
    if len(short_lore) > 500:
        short_lore = short_lore[:500] + "..."

    children = []

    if short_lore:
        children.append(
            html.Div(
                [
                    html.H4("Historia (resumen)"),
                    html.P(short_lore),
                ],
                style={"marginBottom": "10px"},
            )
        )

    if allytips:
        children.append(
            html.Div(
                [
                    html.H4("Consejos para jugarlo"),
                    html.Ul([html.Li(tip) for tip in allytips]),
                ],
                style={"marginBottom": "10px"},
            )
        )

    if enemytips:
        children.append(
            html.Div(
                [
                    html.H4("Consejos para jugar en contra"),
                    html.Ul([html.Li(tip) for tip in enemytips]),
                ],
                style={"marginBottom": "10px"},
            )
        )

    if not children:
        children.append(html.P("No hay información adicional disponible."))

    return html.Div(children=children)


def clean_tooltip(text: str) -> str:
    """
    Limpia mínimamente el HTML de las descripciones de habilidades.
    """
    if not text:
        return ""
    t = text.replace("<br>", "\n").replace("<br />", "\n")
    t = t.replace("<br/>", "\n")
    for tag in ["<font color='#FFCC00'>", "</font>", "<font color='#99FF99'>"]:
        t = t.replace(tag, "")
    return t


def build_abilities_section(champ_data: dict):
    """
    Pasiva + Q/W/E/R con icono, descripción y datos (CD, coste, alcance).
    Estará en la COLUMNA IZQUIERDA.
    """
    version = get_latest_dd_version()
    passive = champ_data.get("passive", {})
    spells = champ_data.get("spells", []) or []

    ability_cards = []

    # Pasiva
    if passive:
        p_name = passive.get("name", "Pasiva")
        p_desc = clean_tooltip(passive.get("description", ""))
        p_img = passive.get("image", {}).get("full")
        p_src = (
            f"https://ddragon.leagueoflegends.com/cdn/{version}/img/passive/{p_img}"
            if p_img
            else None
        )
        ability_cards.append(
            html.Div(
                className="ability-card",
                children=[
                    html.Div(
                        [
                            html.Span("Pasiva", style={"fontWeight": "600"}),
                            html.H5(p_name, style={"margin": "4px 0 4px"}),
                        ]
                    ),
                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "10px",
                            "alignItems": "flex-start",
                        },
                        children=[
                            html.Img(
                                src=p_src,
                                style={
                                    "width": "46px",
                                    "height": "46px",
                                    "borderRadius": "8px",
                                },
                            )
                            if p_src
                            else None,
                            dcc.Markdown(
                                clean_tooltip(p_desc),
                                style={"margin": 0, "whiteSpace": "pre-line"},
                            ),
                        ],
                    ),
                ],
                style={
                    "border": "1px solid rgba(0,0,0,0.08)",
                    "borderRadius": "10px",
                    "padding": "8px 10px",
                    "backgroundColor": "#f9fbff",
                },
            )
        )

    # Hechizos Q/W/E/R
    letters = ["Q", "W", "E", "R"]
    for idx, spell in enumerate(spells[:4]):
        letter = letters[idx] if idx < len(letters) else "H"
        s_name = spell.get("name", f"Habilidad {idx+1}")
        s_desc = clean_tooltip(spell.get("description", ""))
        img = spell.get("image", {}).get("full")
        s_src = (
            f"https://ddragon.leagueoflegends.com/cdn/{version}/img/spell/{img}"
            if img
            else None
        )

        cd = spell.get("cooldownBurn", "")
        cost = spell.get("costBurn", "")
        rng = spell.get("rangeBurn", "")

        meta_line = []
        if cd:
            meta_line.append(f"CD: {cd}")
        if cost:
            meta_line.append(f"Coste: {cost}")
        if rng:
            meta_line.append(f"Alcance: {rng}")
        meta_txt = " | ".join(meta_line)

        ability_cards.append(
            html.Div(
                className="ability-card",
                children=[
                    html.Div(
                        [
                            html.Span(
                                f"{letter}",
                                style={
                                    "fontWeight": "700",
                                    "marginRight": "4px",
                                },
                            ),
                            html.H5(s_name, style={"display": "inline-block"}),
                        ],
                        style={"marginBottom": "4px"},
                    ),
                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "10px",
                            "alignItems": "flex-start",
                        },
                        children=[
                            html.Img(
                                src=s_src,
                                style={
                                    "width": "46px",
                                    "height": "46px",
                                    "borderRadius": "8px",
                                },
                            )
                            if s_src
                            else None,
                            html.Div(
                                [
                                    dcc.Markdown(
                                        clean_tooltip(s_desc),
                                        style={
                                            "margin": 0,
                                            "whiteSpace": "pre-line",
                                        },
                                    ),
                                    html.P(
                                        meta_txt,
                                        style={
                                            "fontSize": "0.8rem",
                                            "margin": "4px 0 0",
                                            "opacity": 0.85,
                                        },
                                    )
                                    if meta_txt
                                    else None,
                                ]
                            ),
                        ],
                    ),
                ],
                style={
                    "border": "1px solid rgba(0,0,0,0.08)",
                    "borderRadius": "10px",
                    "padding": "8px 10px",
                    "backgroundColor": "#f9fbff",
                },
            )
        )

    if not ability_cards:
        return html.P("No hay información de habilidades disponible.")

    return html.Div(
        children=[
            html.H4("Habilidades"),
            html.Div(
                ability_cards,
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr",
                    "gap": "8px",
                },
            ),
        ],
        style={"marginTop": "10px"},
    )



layout = html.Div(
    className="page-container",
    children=[
        
        html.Div(
            className="content left",
            children=[
                html.H2(
                    "Campeones y Skins",
                    className="title",
                ),
                html.P(
                    "Busca un campeón por nombre, elige el nivel y explora su historia "
                    "y habilidades. A la derecha verás la skin actual y sus estadísticas.",
                    style={"marginBottom": "10px"},
                ),
                html.Div(
                    className="input-group",
                    children=[
                        html.Label("Campeón (busca escribiendo el nombre):"),
                        dcc.Dropdown(
                            id="lol-champion-select",
                            options=fetch_all_champions(),
                            value="Ahri",
                            className="input-field",
                            style={"width": "100%"},
                            placeholder="Escribe el nombre del campeón...",
                            searchable=True,
                        ),
                    ],
                ),
                html.Div(
                    className="input-group",
                    children=[
                        html.Label("Nivel (1–18):"),
                        dcc.Input(
                            id="lol-level-input",
                            type="number",
                            min=1,
                            max=18,
                            value=10,
                            step=1,
                            className="input-field",
                        ),
                    ],
                ),
                html.Button(
                    "Cargar campeón",
                    id="lol-load-button",
                    className="btn-generar",
                    n_clicks=0,
                    style={"marginTop": "8px"},
                ),
                html.Div(
                    id="lol-champion-info-text",
                    style={"marginTop": "12px"},
                ),

                html.Hr(style={"margin": "12px 0"}),

                html.Div(
                    id="lol-lore-section",
                    style={"marginTop": "6px"},
                ),

                html.Div(
                    id="lol-abilities-section",
                    style={"marginTop": "10px"},
                ),
            ],
        ),

    
        html.Div(
            className="content right",
            children=[
                html.H2("Detalle visual y estadísticas", className="title"),
                html.Div(
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "gap": "12px",
                        "marginBottom": "10px",
                    },
                    children=[
                        html.Button(
                            "◀",
                            id="lol-prev-skin",
                            n_clicks=0,
                            className="btn-generar",
                            style={"padding": "4px 10px"},
                        ),
                        html.Div(id="lol-skin-label"),
                        html.Button(
                            "▶",
                            id="lol-next-skin",
                            n_clicks=0,
                            className="btn-generar",
                            style={"padding": "4px 10px"},
                        ),
                    ],
                ),
                html.Div(id="lol-champion-card"),

                dcc.Graph(
                    id="lol-stats-graph",
                    style={
                        "height": "430px",
                        "width": "100%",
                        "marginTop": "18px",
                    },
                ),
                dcc.Graph(
                    id="lol-scaling-graph",
                    style={
                        "height": "380px",
                        "width": "100%",
                        "marginTop": "14px",
                    },
                ),
                dcc.Graph(
                    id="lol-info-graph",
                    style={
                        "height": "340px",
                        "width": "100%",
                        "marginTop": "14px",
                    },
                ),
            ],
        ),

        # Stores ocultos
        dcc.Store(id="lol-champion-data-store"),
        dcc.Store(id="lol-skin-index-store", data=0),
    ],
)


@callback(
    Output("lol-champion-data-store", "data"),
    Output("lol-champion-info-text", "children"),
    Input("lol-load-button", "n_clicks"),
    Input("lol-champion-select", "value"),
    prevent_initial_call=False,
)
def cargar_campeon(n_clicks, champ_id):
    if not champ_id:
        return dash.no_update, "Selecciona un campeón."
    champ_data = fetch_champion_data(champ_id)
    name = champ_data.get("name", champ_id)
    title = champ_data.get("title", "")
    tags = champ_data.get("tags", [])
    roles = ", ".join(tags) if tags else "—"
    info_txt = f"Campeón: {name} — {title} | Rol(es): {roles}"
    return champ_data, info_txt


@callback(
    Output("lol-champion-card", "children"),
    Output("lol-stats-graph", "figure"),
    Output("lol-scaling-graph", "figure"),
    Output("lol-info-graph", "figure"),
    Output("lol-skin-label", "children"),
    Output("lol-skin-index-store", "data"),
    Output("lol-lore-section", "children"),
    Output("lol-abilities-section", "children"),
    Input("lol-prev-skin", "n_clicks"),
    Input("lol-next-skin", "n_clicks"),
    Input("lol-champion-data-store", "data"),
    Input("lol-level-input", "value"),
    State("lol-skin-index-store", "data"),
    prevent_initial_call=False,
)
def actualizar_vista(n_prev, n_next, champ_data, level, skin_index_actual):
    if not champ_data:
        fig_empty = go.Figure()
        fig_empty.add_annotation(
            text="Selecciona un campeón y pulsa 'Cargar campeón'.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        fig_empty.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            height=420,
            margin=dict(l=40, r=40, t=60, b=120),
        )
        empty_text = "Esperando selección de campeón..."
        empty_lore = html.P("Sin información disponible.")
        empty_abilities = html.P("Sin habilidades disponibles.")
        return (
            html.P(empty_text),
            fig_empty,
            fig_empty,
            fig_empty,
            "",
            0,
            empty_lore,
            empty_abilities,
        )

    skins = champ_data.get("skins", []) or []
    total_skins = len(skins) if skins else 1

    if skin_index_actual is None:
        skin_index_actual = 0
    idx = int(skin_index_actual)

    ctx = dash.callback_context
    if not ctx.triggered:
        idx = 0
    else:
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        if trigger == "lol-prev-skin" and total_skins > 0:
            idx = (idx - 1) % total_skins
        elif trigger == "lol-next-skin" and total_skins > 0:
            idx = (idx + 1) % total_skins
        elif trigger == "lol-champion-data-store":
            idx = 0

    lvl = level or 1
    card = build_champion_card(champ_data, idx)
    fig_stats = build_stats_figure(champ_data, lvl)
    fig_scaling = build_scaling_figure(champ_data, lvl)
    fig_info = build_info_figure(champ_data)
    lore_section = build_lore_section(champ_data)
    abilities_section = build_abilities_section(champ_data)

    if skins:
        skin_name = skins[idx].get("name", "Predeterminada")
        label_txt = f"Skin {idx + 1} de {total_skins}: {skin_name}"
    else:
        label_txt = "Skin única / predeterminada"

    return (
        card,
        fig_stats,
        fig_scaling,
        fig_info,
        label_txt,
        idx,
        lore_section,
        abilities_section,
    )
