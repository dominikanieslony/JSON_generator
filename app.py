import streamlit as st
import json
from datetime import datetime

TEMPLATE_PATH = "template.json"


# ----------------------------
# LOAD TEMPLATE (LOCAL ONLY)
# ----------------------------
def load_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ----------------------------
# IDS
# ----------------------------
def generate_commercial_id():
    return datetime.now().strftime("%Y%m%d%H%M")


def generate_order_line_id(commercial_id, index):
    return f"{commercial_id}{str(index).zfill(3)}"


# ----------------------------
# TAX CALC
# ----------------------------
def calc_tax(amount, rate):
    return round(amount * rate / (100 + rate), 2)


# ----------------------------
# SESSION INIT
# ----------------------------
if "offers" not in st.session_state:
    st.session_state.offers = []

st.set_page_config(page_title="JSON Generator", layout="centered")

st.title("📦 JSON Order Generator")


# ----------------------------
# FORM
# ----------------------------
with st.form("offer_form"):
    offer_id = st.text_input("Offer ID *")
    offer_price = st.number_input("Offer Price", step=0.01)
    rate = st.number_input("Rate (%)", step=0.1)

    shipping_type_code = st.selectbox(
        "Shipping Type Code",
        ["STD", "doorstep", "floor", "appointment"]
    )

    code = st.selectbox(
        "VAT Code",
        ["vat-de-standard", "vat-de-reduced"]
    )

    submitted = st.form_submit_button("Add Offer Line")

    if submitted:
        errors = []

        if not offer_id or not offer_id.strip():
            errors.append("Offer ID is required")

        if offer_price <= 0:
            errors.append("Offer Price must be greater than 0")

        if rate <= 0:
            errors.append("Rate must be greater than 0")

        if errors:
            for e in errors:
                st.error(e)
        else:
            st.session_state.offers.append({
                "offer_id": offer_id.strip(),
                "offer_price": float(offer_price),
                "rate": float(rate),
                "shipping_type_code": shipping_type_code,
                "code": code
            })
            st.success("✅ Offer line added")


# ----------------------------
# CURRENT OFFERS
# ----------------------------
st.subheader("📋 Current Offer Lines")

if st.session_state.offers:
    for i, o in enumerate(st.session_state.offers, start=1):
        col1, col2 = st.columns([8, 1])

        with col1:
            st.write(
                f"**{i}.** {o['offer_id']} | "
                f"{o['offer_price']} EUR | "
                f"{o['rate']}%"
            )

        with col2:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.offers.pop(i - 1)
                st.rerun()
else:
    st.info("No offer lines yet.")


# ----------------------------
# GENERATE JSON
# ----------------------------
if st.button("🚀 Generate JSON"):

    if not st.session_state.offers:
        st.error("Add at least one offer line.")
        st.stop()

    template = load_template()
    commercial_id = generate_commercial_id()

    template["commercial_id"] = commercial_id

    offers_list = []

    for idx, o in enumerate(st.session_state.offers, start=1):

        tax = calc_tax(o["offer_price"], o["rate"])

        offer = {
            "order_line_id": generate_order_line_id(commercial_id, idx),
            "currency_iso_code": "EUR",
            "offer_id": o["offer_id"],
            "shipping_type_code": o["shipping_type_code"],
            "quantity": 1,
            "offer_price": o["offer_price"],
            "price": o["offer_price"],
            "taxes": [
                {
                    "amount": tax,
                    "code": o["code"],
                    "rate": o["rate"]
                }
            ],
            "shipping_price": 0.00
        }

        offers_list.append(offer)

    template["offers"] = offers_list

    json_output = json.dumps(template, indent=4, ensure_ascii=False)

    st.subheader("🔎 JSON Preview")
    st.code(json_output, language="json")

    filename = f"generated_{commercial_id}.json"

    st.download_button(
        "📥 Download JSON",
        data=json_output,
        file_name=filename,
        mime="application/json"
    )


# ----------------------------
# RESET
# ----------------------------
if st.button("🧹 Reset"):
    st.session_state.offers = []
    st.success("Reset done")
