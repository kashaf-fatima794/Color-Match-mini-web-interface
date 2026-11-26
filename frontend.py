
import io
import random
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from backend import load_data, train_model, predict_colour, matching_palette, rgb_to_hex

st.set_page_config(
    page_title="Celeste's Colour Studio",
    page_icon="🎨",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');
.stApp {
    background:linear-gradient(135deg,#fff5f8,#fff8fb,#fff0f5);
    color:#704154;font-family:'DM Sans',sans-serif;
}
.block-container {max-width:1400px;padding-top:1.8rem;padding-bottom:3rem;}
.hero {
    background:linear-gradient(120deg,#ffdce8,#ffe1ec,#ffeaf1);
    padding:32px;border-radius:25px;margin-bottom:25px;
    border:1px solid white;box-shadow:0 12px 35px #a34d7012;
}
.hero h1 {font-family:'Playfair Display',serif;color:#71384f;font-size:42px;margin:8px 0;}
.hero p {color:#9b7588;margin:0;font-size:15px;}
.heading {font-family:'Playfair Display',serif;color:#80445e;font-size:26px;font-weight:600;}
.muted {color:#b58b9b;font-size:13px;margin-bottom:15px;}
.card {
    background:#ffffffd9;border:1px solid #f5dce6;border-radius:20px;
    padding:20px;box-shadow:0 8px 30px #a34d700a;margin-bottom:14px;
}
.swatch {height:78px;border-radius:12px;margin-bottom:8px;border:1px solid #0000000b;}
.swatch-label {font-size:12px;color:#946579;font-weight:700;}
.swatch-hex {font-size:12px;color:#b58b9b;}
div.stButton>button {
    border-radius:12px;background:#ffe4ed;color:#a34d70;
    border:1px solid #f5c4d5;font-weight:700;min-height:42px;
}
div.stButton>button:hover {background:#f8d0df;color:#71384f;border-color:#efb4ca;}
div[data-testid="stMetric"] {background:#fff5f8;border:1px solid #f5dce6;border-radius:15px;padding:15px;}
div[data-testid="stMetric"] label,
div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] p {color:#946579 !important;opacity:1 !important;}
div[data-testid="stMetricValue"],div[data-testid="stMetricValue"] > div {color:#71384f !important;opacity:1 !important;}
.stMarkdown,.stMarkdown p,.stMarkdown label {color:#704154;}
hr {border-color:#f5dce6;}
footer {visibility:hidden;}
div[data-testid="stMetric"] {
    overflow-wrap: anywhere;
    word-break: normal;
}

div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] > div {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: normal !important;
    line-height: 1.4;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_dataset():
    return load_data("color_pedia.csv")

@st.cache_resource
def get_model():
    data = get_dataset()
    return train_model(data)

try:
    df = get_dataset()
    model, accuracy = get_model()
except Exception as error:
    st.error(f"Could not load or train the colour model: {error}")
    st.info("Check that color_pedia.csv is in the same folder as frontend.py and backend.py.")
    st.stop()

st.markdown("""
<div class="hero">
  <h1>Celeste's Colour Studio</h1>
  <p>An AI colour explorer and digital sketchbook, made for your imagination.</p>
</div>
""", unsafe_allow_html=True)

if "rgb" not in st.session_state:
    st.session_state.rgb = (130, 145, 181)
if "brush_colour" not in st.session_state:
    st.session_state.brush_colour = "#000000"
if "brush_size" not in st.session_state:
    st.session_state.brush_size = 5

# Keep sliders synced with the selected RGB colour.
for key, value in zip(("red_slider", "green_slider", "blue_slider"), st.session_state.rgb):
    if key not in st.session_state:
        st.session_state[key] = int(value)
if "canvas_colour_picker" not in st.session_state:
    st.session_state.canvas_colour_picker = st.session_state.brush_colour

def choose_random_colour():
    new_rgb = tuple(random.randint(0, 255) for _ in range(3))
    st.session_state.rgb = new_rgb
    st.session_state.red_slider = new_rgb[0]
    st.session_state.green_slider = new_rgb[1]
    st.session_state.blue_slider = new_rgb[2]

def select_brush_colour(colour):
    st.session_state.brush_colour = colour
    st.session_state.canvas_colour_picker = colour

tab_ai = st.container()
tab_canvas = st.container()

with tab_ai:
    left, right = st.columns([0.85, 1.15], gap="large")
    with left:
        st.markdown('<div class="heading">Create a shade</div><div class="muted">Adjust RGB values or choose a palette colour.</div>', unsafe_allow_html=True)
        current = st.session_state.rgb
        r = st.slider("🔴 Red", 0, 255, int(current[0]), key="red_slider")
        g = st.slider("🟢 Green", 0, 255, int(current[1]), key="green_slider")
        b = st.slider("🔵 Blue", 0, 255, int(current[2]), key="blue_slider")
        st.session_state.rgb = (r, g, b)
        selected_hex = rgb_to_hex(r, g, b)
        st.markdown(
            f'<div class="card"><div style="height:140px;border-radius:15px;background:{selected_hex};"></div>'
            f'<p style="margin:15px 0 5px;color:#b58b9b;font-size:11px;letter-spacing:2px;">SELECTED COLOUR</p>'
            f'<span style="background:#ffe4ed;padding:8px 12px;border-radius:9px;color:#a34d70;font-weight:700;">{selected_hex}</span>'
            f'<p style="color:#9b7588;font-size:13px;">RGB ({r}, {g}, {b})</p></div>',
            unsafe_allow_html=True
        )
        st.button("Random colour", use_container_width=True, on_click=choose_random_colour)

    result = predict_colour(model, df, r, g, b)
    with right:
        st.markdown('<div class="heading">Your colour match</div><div class="muted">A close match from your dataset, with its colour family and mood.</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="card"><div style="height:150px;border-radius:15px;background:{selected_hex};"></div>'
            f'<h2 style="font-family:Playfair Display,serif;color:#80445e;margin-bottom:0;">{result["match_name"]}</h2>'
            f'<p style="color:#b58b9b;font-size:13px;">Closest dataset colour</p></div>',
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        c1.metric("Predicted family", result["family"])
        c2.metric("Dataset HEX", result["match_hex"])
        c3, c4 = st.columns(2)
        c3.metric("Emotion", result["emotion"])
        c4.metric("Mood", result["mood"])

    st.markdown("---")
    st.markdown('<div class="heading">Matching palette</div><div class="muted">Choose a swatch to use it as your drawing colour. Your sketchbook is directly below.</div>', unsafe_allow_html=True)
    palette = matching_palette(r, g, b)
    palette_cols = st.columns(len(palette))
    for i, item in enumerate(palette):
        with palette_cols[i]:
            st.markdown(
                f'<div class="swatch" style="background:{item["hex"]};"></div>'
                f'<div class="swatch-label">{item["label"]}</div>'
                f'<div class="swatch-hex">{item["hex"]}</div>',
                unsafe_allow_html=True
            )
            st.button("Use colour", key=f"use_palette_{i}", use_container_width=True,
                      on_click=select_brush_colour, args=(item["hex"],))

    m1, m2, m3 = st.columns(3)
    m1.metric("Test accuracy", f"{accuracy * 100:.1f}%")
    m2.metric("Colour families", int(df["Family"].nunique()))
    m3.metric("Usable dataset rows", len(df))

with tab_canvas:
    st.markdown('<div class="heading">Your digital sketchbook</div><div class="muted">Draw in the canvas, pick a brush colour, and download your artwork as a PNG.</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        canvas_colour = st.color_picker("Brush colour", key="canvas_colour_picker")
        st.session_state.brush_colour = canvas_colour
    with c2:
        brush_size = st.slider("Brush size", 1, 30, int(st.session_state.brush_size), key="canvas_brush_size")
        st.session_state.brush_size = brush_size
    with c3:
        background = st.selectbox("Canvas background", ["White", "Warm paper", "Black"], key="canvas_background")
    background_hex = {"White": "#FFFFFF", "Warm paper": "#FFF9F0", "Black": "#17131D"}[background]

    # ======================================
    # CANVAS SECTION START
    # Drawing canvas, brush, eraser, undo and PNG download
    # ======================================

    canvas_html = f"""
    <div style="font-family:Arial,sans-serif;color:#946579;margin-bottom:8px;">
      Draw below. Use the controls to change brush, size, erase, undo, clear, and download.
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;">
      <button id="undo" style="padding:8px 14px;border:0;border-radius:9px;background:#ffe4ed;color:#a34d70;font-weight:bold;">Undo</button>
      <button id="erase" style="padding:8px 14px;border:0;border-radius:9px;background:#ffe4ed;color:#a34d70;font-weight:bold;">Eraser</button>
      <button id="draw" style="padding:8px 14px;border:0;border-radius:9px;background:#ffe4ed;color:#a34d70;font-weight:bold;">Brush</button>
      <button id="clear" style="padding:8px 14px;border:0;border-radius:9px;background:#f8d0df;color:#71384f;font-weight:bold;">Clear canvas</button>
      <button id="download" style="padding:8px 14px;border:0;border-radius:9px;background:#dfeee6;color:#356b50;font-weight:bold;">Download PNG</button>
    </div>
    <canvas id="art" style="display:block;width:100%;height:470px;border:1px solid #f5dce6;border-radius:15px;touch-action:none;cursor:crosshair;"></canvas>
    <script>
    const canvas = document.getElementById('art');
    const ctx = canvas.getContext('2d');
    const bg = '{background_hex}';
    let colour = '{canvas_colour}';
    let size = {brush_size};
    let drawing = false;
    let erasing = false;
    let strokes = [];
    let activeStroke = null;
    function resizeCanvas() {{
      const old = document.createElement('canvas');
      old.width = canvas.width || 900; old.height = canvas.height || 470;
      old.getContext('2d').drawImage(canvas,0,0);
      const rect = canvas.getBoundingClientRect();
      canvas.width = Math.floor(rect.width * devicePixelRatio);
      canvas.height = Math.floor(470 * devicePixelRatio);
      ctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0);
      ctx.fillStyle = bg; ctx.fillRect(0,0,rect.width,470);
      if (old.width > 0) ctx.drawImage(old,0,0,old.width,old.height,0,0,rect.width,470);
    }}
    function redraw() {{
      const rect = canvas.getBoundingClientRect();
      ctx.clearRect(0,0,rect.width,470);
      ctx.fillStyle = bg; ctx.fillRect(0,0,rect.width,470);
      for (const stroke of strokes) {{
        if (!stroke.points.length) continue;
        ctx.beginPath();
        ctx.strokeStyle = stroke.colour;
        ctx.lineWidth = stroke.size;
        ctx.lineCap = 'round'; ctx.lineJoin = 'round';
        ctx.moveTo(stroke.points[0][0],stroke.points[0][1]);
        for (const p of stroke.points.slice(1)) ctx.lineTo(p[0],p[1]);
        if (stroke.points.length === 1) {{
          ctx.lineTo(stroke.points[0][0]+0.1,stroke.points[0][1]+0.1);
        }}
        ctx.stroke();
      }}
    }}
    function pos(e) {{
      const rect = canvas.getBoundingClientRect();
      return [e.clientX-rect.left,e.clientY-rect.top];
    }}
    canvas.addEventListener('pointerdown', e => {{
      drawing = true; canvas.setPointerCapture(e.pointerId);
      activeStroke = {{colour: erasing ? bg : colour,size,points:[pos(e)]}};
      strokes.push(activeStroke); redraw();
    }});
    canvas.addEventListener('pointermove', e => {{
      if (!drawing || !activeStroke) return;
      activeStroke.points.push(pos(e)); redraw();
    }});
    function stop() {{ drawing = false; activeStroke = null; }}
    canvas.addEventListener('pointerup',stop);
    canvas.addEventListener('pointercancel',stop);
    document.getElementById('undo').onclick = () => {{ strokes.pop(); redraw(); }};
    document.getElementById('clear').onclick = () => {{ strokes = []; redraw(); }};
    document.getElementById('erase').onclick = () => {{ erasing = true; }};
    document.getElementById('draw').onclick = () => {{ erasing = false; }};
    document.getElementById('download').onclick = () => {{
      const out = document.createElement('canvas');
      out.width = canvas.width; out.height = canvas.height;
      const ox = out.getContext('2d');
      ox.fillStyle = bg; ox.fillRect(0,0,out.width,out.height);
      ox.drawImage(canvas,0,0);
      const link = document.createElement('a');
      link.download = 'celestes-artwork.png';
      link.href = out.toDataURL('image/png');
      link.click();
    }};
    resizeCanvas();
    window.addEventListener('resize',resizeCanvas);
    </script>
    """
    components.html(canvas_html, height=570, scrolling=False)

    # ======================================
    # CANVAS SECTION END
    # ======================================

